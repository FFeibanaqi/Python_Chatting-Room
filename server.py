'''
asyncore框架（并发处理的特殊工具）可以同时处理多个连接实现用户之间的交流
其中的dispatcher类基本上是一个套接字对象，但它具有额外的事件处理特性
'''
from asyncore import dispatcher
from asynchat import async_chat
import asyncore,socket

PORT = 5555
class EndSession(Exception):pass

'''
接受连接并产生单个会话，处理到其他会话的广播
'''
class ChatServer(asyncore.dispatcher):
    def __init__(self, port):
        dispatcher.__init__(self)
        self.create_socket(socket.AF_INET,socket.SOCK_STREAM)  #指定套接字所需要的类型
        self.set_reuse_addr()   #处理服务器没有正常关闭下重用同一的地址的问题（port）
        self.bind(('192.168.0.7', port))
        self.listen(5)
        self.users = {}
        self.main_room = ChatRoom(self)

     #调用允许客户端连接的self.accept函数
    def handle_accept(self):
        conn, addr = self.accept()
        ChatSession(self, conn)

'''
ChatSession对象会将读取的数据作为保存为字符串列表data
asynchat模块：收集来自客户端的数据（文本）并进行响应
其中async_chat类用于大多数基本的套接字读写操作
'''
class ChatSession(async_chat):
    def __init__(self, server, sock):
        async_chat.__init__(self, sock)
        self.server = server
        self.set_terminator(b'\n') #设定终止符
        self.data = []
        self.name = None
        self.enter(LoginRoom(server))

    def enter(self, room):
        # 从当前房间移除自身，然后添加到指定房间
        try:
            cur = self.room
        except AttributeError:
            pass
        else:
            cur.remove(self)
        self.room = room
        room.add(self)

    def collect_incoming_data(self, data):   #读入更多数据时，调用此方法将新读入的加入列表中, 接收客户端的数据
        self.data.append(data.decode("utf-8"))

    def found_terminator(self):     #发现终止符(即客户端的一条数据结束时的处理)时被调用，使用连接当前数据项的方法创建新行，并置self,data为空列表
        line = ''.join(self.data)   #由于使用字符串列表习惯性连接（join字符串方法）
        self.data = []
        try: self.room.handle(self, line.encode("utf-8"))
        except EndSession:      # 退出聊天室的处理
            self.handle_close()

    def handle_close(self):     # 当 session 关闭时，将进入 LogoutRoom
        async_chat.handle_close(self)
        self.enter(LogoutRoom(self.server))
'''
简单命令处理
'''
class CommandHandler:    # 响应未知命令
    def unknown(self, session, cmd):
        session.push(('Unknown command {} \n'.format(cmd)).encode("utf-8"))   # async_chat.push 方法发送消息

    def handle(self, session, line):
        line = line.decode()        # 命令处理
        if not line.strip():
            return
        parts = line.split(' ', 1)
        cmd = parts[0]
        try:
            line = parts[1].strip()
        except IndexError:
            line = ''   # 通过协议代码执行相应的方法
        method = getattr(self, 'do_' + cmd, None)
        try:
            method(session, line)
        except TypeError:
            self.unknown(session, cmd)
            
'''
包含多个用户的环境，负责基本的命令处理和广播
'''
class Room(CommandHandler):    
    def __init__(self, server):
        self.server = server
        self.sessions = []

    def add(self, session):        # 一个用户进入房间
        self.sessions.append(session)

    def remove(self, session):     # 一个用户离开房间
        self.sessions.remove(session)

    def broadcast(self, line):     # 向所有的用户发送指定消息,使用 asyn_chat.push 方法发送数据
        for session in self.sessions:
            session.push(line)

    def do_logout(self, session, line):  # 退出房间
        raise EndSession

'''
处理登录用户
'''
class LoginRoom(Room):
    def add(self, session):      # 用户连接成功的回应
        Room.add(self, session)  # 使用asyn_chat.push 方法发送数据
        session.push(b'Connect Success')

    def do_login(self, session, line):   # 用户登录逻辑
        name = line.strip()  # 获取用户名称
        if not name:
            session.push(b'UserName Empty')
        elif name in self.server.users:   # 检查是否有同名用户
            session.push(b'UserName Exist')
        else:     # 登陆的用户进入主聊天室
            session.name = name
            session.enter(self.server.main_room)

'''
删除离开的用户
'''
class LogoutRoom(Room):
    def add(self, session):  # 从服务器中移除
        try:del self.server.users[session.name]
        except KeyError:pass
    
'''
聊天房间
'''
class ChatRoom(Room):
    def add(self, session):        # 广播新用户的进入
        session.push(b'Login Success')
        self.broadcast((session.name + '进入聊天室.\n').encode("utf-8"))
        self.server.users[session.name] = session
        Room.add(self, session)

    def remove(self, session):        # 广播用户的离开
        Room.remove(self, session)
        self.broadcast((session.name + '离开了聊天室.\n').encode("utf-8"))

    def do_say(self, session, line):        # 广播客户端发送消息
        self.broadcast((session.name + ': ' + line + '\n').encode("utf-8"))

    def do_look(self, session, line):       # 查看在线用户
        session.push(b'Online Users:\n')
        for other in self.sessions:
            session.push((other.name + '\n').encode("utf-8"))

if __name__ == '__main__':    
    try:        #键盘意外中断处理
        s = ChatServer(PORT)
        asyncore.loop()   #调用asyncore启动服务器来循环监听
    except KeyboardInterrupt:
        print("chat server exit")