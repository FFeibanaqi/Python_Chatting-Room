一．	需求分析:
  在网络日渐普及的今天，更加新型的聊天软件层出不穷，虽然有很多这种软件，但是人们总会选择那些满足自己使用需求且符合自己审美需求的软件。由此，萌生了做一个个性化的聊天软件，既然要求个性化，那么GUI的选择就很重要，当然是在自己所使用的语言下考虑。
  服务器可以支持多个用户在线聊天。
  用户不需求具体的注册，只需在登陆时选择好自己要使用的名字，服务器会自己帮用户记录这个用户名。
二．	概要设计
  1.	语言的选择：Python(现下最火的语言，当然抱着好奇心挑战下，在深入了解和学习后，从此就喜欢上了这门语言)
  2.	GUI的选择：Wxpython(在选择GUI的使用时纠结了很久，但最后还是选择了这个稳定性强，UI设计还不错的wxpython,结果的效果还不错)
  3.	框架的选择：
    1）. asyncore框架（并发处理的特殊工具）可以同时处理多个连接实现用户之间的交流其中的dispatcher类基本上是一个套接字对象，但它具有额外的事件处理特性。
    2）. asynchat模块：收集来自客户端的数据（文本）并进行响应其中async_chat类似于大多数基本的套接字读写操作
  4.协议的选择：
    用户和服务器之间的连接使用的是Telnet协议。（应用层协议，远程登陆协议）
  4.	实现方式：
    客户/服务器模式
三．	详细设计：
  1.流程设计图：
 
  2.主要函数的作用：
    服务器端主要的函数：
       1）. def collect_incoming_data(self, data)：读入更多数据时，调用此方法将新读入的加入列表中, 接收客户端的数据
       2）. def found_terminator(self): 发现终止符(即客户端的一条数据结束时的处理)时被调用，使用连接当前数据项的方法创建新行，并置self,data为空列表
       3）. def handle(self, session, line): 命令处理
       4）. def add(self, session):一个用户进入房间
       5）. def remove(self, session):一个用户离开房间
       6）.def broadcast(self, line):向所有的用户发送指定消息,使用 asyn_chat.push 方法发送数据
       7）.def do_login(self, session, line): 用户的登录逻辑
    客户端主要的函数：
       1）. def __init__(self, parent, id, title, size):初始化添加控件并绑定事件
       2）. def login(self, event):用户登陆操作
       3）. def handle(self, session, line): 命令处理
       4）.def showDialog(self, title, content, size): 显示错误信息对话框
       5）. def OnEraseBack1(self,event):背景图片的巧妙化处理
       6）. def lookUsers(self, event):查看当前在线用户
