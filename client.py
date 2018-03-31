import wx
import telnetlib
from time import sleep
import _thread as thread

'''
登录窗口
'''
class LoginFrame(wx.Frame):
    def __init__(self, parent, id, title, size):      # 初始化添加控件并绑定事件
        wx.Frame.__init__(self, parent, id, title)
        self.panel=wx.Panel(self)
        self.panel.Bind(wx.EVT_ERASE_BACKGROUND,self.OnEraseBack)
        self.SetSize(size)
        self.Center()
        self.serverAddressLabel = wx.StaticText(self.panel, label="Server Address", pos=(30, 100), size=(100, 23),style=wx.ALIGN_CENTER)
        self.userNameLabel = wx.StaticText(self.panel, label="UserName", pos=(60, 150), size=(80, 23),style=wx.ALIGN_CENTER)
        self.serverAddress = wx.TextCtrl(self.panel, pos=(160, 97), size=(150, 25))
        self.userName = wx.TextCtrl(self.panel, pos=(160, 147), size=(150, 25))
        self.loginButton = wx.Button(self.panel, label='Login', pos=(130, 245), size=(130, 30))
        self.loginButton.Bind(wx.EVT_BUTTON, self.login) #绑定登录事件
        self.Show()    #调用app.mainloop()前需要调用窗口的Show方法，否则会一直隐藏
        
    def OnEraseBack(self,event):
        dc=event.GetDC()
        if not dc:
            dc=wx.ClientDC(self)
            rect=self.GetUpdateRegion().GetBox()
            dc.SetClippingRegion(rect)
        dc.Clear()
        bmp=wx.Bitmap("D:\python\Code/bkg.png")
        dc.DrawBitmap(bmp,0,0)
        
    def login(self, event):
        print("login")
        try:
            print("try")
            serverAddress = self.serverAddress.GetLineText(0).split(':')
            print(serverAddress[0])
            print(serverAddress[1])
            con.open(serverAddress[0], port=int(serverAddress[1]), timeout=10)   #con = telnetlib.Telnet()连接Telnet服务器
            print("rep")
            response = con.read_some()   #read_some()只要有结果就返回
            print(response)
            if response != b'Connect Success':
                print("ppp")
                self.showDialog('Error', 'Connect Fail!', (200, 100))
                return
            con.write(('login ' + str(self.userName.GetLineText(0)) + '\n').encode("utf-8"))
            response = con.read_some()
            if response == b'UserName Empty':
                print("hhh")
                self.showDialog('Error', 'UserName Empty!', (200, 100))
            elif response == b'UserName Exist':
                print("sss")
                self.showDialog('Error', 'UserName Exist!', (200, 100))
            else:
                self.Close()
                ChatFrame(None, 2, title='文艺小青年聊天室', size=(500, 400))
        except Exception as e :
            print(e)
            self.showDialog('Error', 'Connect Fail!', (95, 20))

    def showDialog(self, title, content, size):    # 显示错误信息对话框
        dialog = wx.Dialog(self, title=title, size=size)
        dialog.Center()
        wx.StaticText(dialog, label=content)
        dialog.ShowModal()
        
'''
聊天界面
'''
class ChatFrame(wx.Frame):
     def __init__(self, parent, id, title, size):
        wx.Frame.__init__(self, parent, id, title)
        self.panel=wx.Panel(self)
        self.panel.Bind(wx.EVT_ERASE_BACKGROUND,self.OnEraseBack1)
        self.SetSize(size)
        self.Center()
        self.chatFrame = wx.TextCtrl(self.panel, pos=(5, 5), size=(490, 310), style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.message = wx.TextCtrl(self.panel, pos=(5, 320), size=(300, 25))
        self.sendButton = wx.Button(self.panel, label="发送", pos=(310, 320), size=(58, 25))
        self.usersButton = wx.Button(self.panel, label="用户", pos=(373, 320), size=(58, 25))
        self.closeButton = wx.Button(self.panel, label="退出", pos=(436, 320), size=(58, 25))
        #对相应的按钮进行事件绑定
        self.sendButton.Bind(wx.EVT_BUTTON, self.send)        
        self.usersButton.Bind(wx.EVT_BUTTON, self.lookUsers)       
        self.closeButton.Bind(wx.EVT_BUTTON, self.close)
        thread.start_new_thread(self.receive, ())    #在子线程中接受服务器发来的消息
        self.Show()
        
     def OnEraseBack1(self,event):
        dc=event.GetDC()
        if not dc:
            dc=wx.ClientDC(self)
            rect=self.GetUpdateRegion().GetBox()
            dc.SetClippingRegion(rect)
        dc.Clear()
        bmp=wx.Bitmap("D:\python\Code/chattingbkg.png")
        dc.DrawBitmap(bmp,0,0)

     def send(self, event):        # 发送消息
        message = str(self.message.GetLineText(0)).strip()
        if message != '':
            con.write(('say ' + message + '\n').encode("utf-8"))
            self.message.Clear()

     def lookUsers(self, event):  # 查看当前在线用户
        con.write(b'look\n')

     def close(self, event):      # 关闭窗口
        con.write(b'logout\n')
        con.close()
        self.Close()

     def receive(self):          # 接受服务器的消息
        while True:
            sleep(0.8)
            result = con.read_very_eager()
            if result != '':
                self.chatFrame.AppendText(result)

if __name__ == '__main__':
    app = wx.App()
    con = telnetlib.Telnet()
    LoginFrame(None, -1, title="Login", size=(420, 350))
    app.MainLoop()
