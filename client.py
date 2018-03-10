"""聊天室客户端"""
from socket import *
from select import *
from tkinter import *
import os
import threading
import traceback
import time


class Client():

    def __init__(self, sockfd):
        self.sockfd = sockfd

    def login(self):
        """登录"""
        while True:
            name = input('请数据您的群聊名:')
            if not name:
                print('聊天名字不能为空')
            else:
                break
        self.sockfd.send(('joinin ' + name).encode())
        return True

    def logout(self):
        """退出"""
        try:
            self.sockfd.send('logout'.encode())
        except BrokenPipeError:
            pass
        self.sockfd.close()
        print('登出成功，欢迎下次再来!')
        os._exit(0)

    def print_menu(self):
        """客户端菜单显示"""
        print('+---------------------+')
        print('|1 joinin             |')
        print('|2 logout             |')
        print('+---------------------+')

    def get_sockfd(self):
        return self.sockfd


def show_room_member(data, listLianxi, scroLianxi):
    msg = data.split('`room-members#`:', 1)
    words = msg[0]
    if len(msg) > 1:
        members = msg[1]
    Linkman = members.split(',')
    listLianxi.delete(0, listLianxi.size())
    for line in Linkman:
        listLianxi.insert(END, "  群成员 ------ " + str(line))
    scroLianxi.config(command=listLianxi.yview)  # scrollbar滚动时listbox同时滚动
    return words


def recvmsg(client, txtMsgList, listLianxi, scroLianxi):
    """接受群信息
    因接受信息和发送信息不能同时通过阻塞完成
    这里将其中一个放在线程或进程中，通过内核通知的方式实现
    """
    while True:
        rs, ws, es = select([client.get_sockfd()], [], [])
        for r in rs:
            data = r.recv(1024).decode()
            msg = data.split(' #say#`:', 1)
            str_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            if len(msg) > 1:
                name = msg[0]
                words = msg[1]
                txtMsgList.insert(END, name + ' ' +
                                  str_time + ':\n', 'greencolor')
                if '`room-members#`:' in words:
                    words = show_room_member(words, listLianxi, scroLianxi)
                txtMsgList.insert(END, words + '\n')
            else:
                txtMsgList.insert(END, data)


def client_ui(client, sockfd):

    def sendMsg():  # 发送消息
        msg = txtMsg.get('0.0', END).strip()
        try:
            sockfd.send(msg.encode())
        except BrokenPipeError:
            print('服务器故障，聊天终止')
            client.logout()
        txtMsg.delete('0.0', END)  # 删除中间刚输入的内容

    def cancelMsg():  # 取消消息
        txtMsg.delete('0.0', END)

    def sendMsgEvent(event):  # 发送消息事件:
        if event.keysym == "Return":
            sendMsg()

    def logout():
        client.logout()

    # 创建窗口
    window = Tk()
    window.title('房间1')

    # 创建frame容器
    frmLT = Frame(width=500, height=320, bg='white')
    frmLC = Frame(width=500, height=150, bg='white')
    frmLB = Frame(width=500, height=30)
    frmRT = Frame(width=200, height=500)

    # 创建控件
    txtMsgList = Text(frmLT)
    txtMsgList.tag_config('greencolor', foreground='#008C00')  # 创建tag
    txtMsg = Text(frmLC)
    # help('tkinter.Text') # 看用法用这个
    txtMsg.bind("<KeyPress-Return>", sendMsgEvent)

    # Scrollbar控件
    scroLianxi = Scrollbar(
        frmRT, width=11, cursor='pirate', troughcolor="white")
    # Listbox控件
    listLianxi = Listbox(frmRT, width=22, height=25,
                         yscrollcommand=scroLianxi.set)

    # 将收到的信息发送到面板上
    t = threading.Thread(target=recvmsg, args=(
        client, txtMsgList, listLianxi, scroLianxi))
    t.setDaemon(True)
    t.start()

    # 发送取消按钮和图片
    btnSend = Button(frmLB, text='发送(回车)', width=8, command=sendMsg)
    btnCancel = Button(frmLB, text='取消', width=8, command=cancelMsg)
    btnLogout = Button(frmLB, text='退出', width=8, command=logout)

    # 窗口布局columnspan选项可以指定控件跨越多列显示，
    # 而rowspan选项同样可以指定控件跨越多行显示。
    frmLT.grid(row=0, column=0, columnspan=2, padx=1, pady=3)
    frmLC.grid(row=1, column=0, columnspan=2, padx=1, pady=3)
    frmLB.grid(row=2, column=0, columnspan=2)
    frmRT.grid(row=0, column=2, columnspan=2, rowspan=3, padx=2, pady=3)
    # 固定大小
    frmLT.grid_propagate(0)
    frmLC.grid_propagate(0)
    frmLB.grid_propagate(0)
    frmRT.grid_propagate(0)

    # 按钮
    btnSend.grid(row=2, column=0)
    btnCancel.grid(row=2, column=1)
    btnLogout.grid(row=2, column=2)

    txtMsgList.grid()
    txtMsg.grid()

    scroLianxi.grid(row=0, column=1, ipady=120)
    listLianxi.grid(row=0, column=0)

    # 主事件循环
    window.mainloop()


def main():
    s = socket()
    s.connect(('0.0.0.0', 9999))

    client = Client(s)
    client.print_menu()
    login = False
    try:
        while True:
            cmd = input('please input:')
            if cmd == '2':
                client.logout()
                break
            elif cmd == '1':
                login = client.login()
                break

        if login:
            client_ui(client, s)

    except KeyboardInterrupt:
        traceback.print_exc()
        client.logout()


if __name__ == '__main__':
    main()
