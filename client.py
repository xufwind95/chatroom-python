from socket import *
import os
import threading
from select import *
import traceback


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
        self.sockfd.send('logout'.encode())
        self.sockfd.close()
        print('登出成功，欢迎下次再来!')
        os._exit(0)

    def say(self):
        """发言"""
        while True:
            msg = input()
            if msg == 'q':
                self.logout()
            else:
                try:
                    self.sockfd.send(msg.encode())
                except BrokenPipeError:
                    print('服务器故障，聊天终止')
                    self.logout()

    def print_menu(self):
        """客户端菜单显示"""
        print('+---------------------+')
        print('|1 joinin             |')
        print('|2 logout             |')
        print('+---------------------+')

    def get_sockfd(self):
        return self.sockfd


def recvmsg(client):
    """接受群信息
    因接受信息和发送信息不能同时通过阻塞完成
    这里将其中一个放在线程或进程中，通过内核通知的方式实现
    """
    while True:
        rs, ws, es = select([client.get_sockfd()], [], [])
        for r in rs:
            data = r.recv(1024).decode()
            print(data)


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
            print('login success')
            t = threading.Thread(target=recvmsg, args=(client,))
            t.setDaemon(True)
            t.start()
            client.say()

    except KeyboardInterrupt:
        traceback.print_exc()
        client.logout()


if __name__ == '__main__':
    main()
