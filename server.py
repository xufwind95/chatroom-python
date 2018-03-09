"""聊天室简单实现
   功能:公告和收发信息
"""
from socket import *
from select import *
import threading
import os


class ChatRoom():

    def __init__(self, members, inputs, servsock):
        self.members = members
        self.inputs = inputs
        self.servsock = servsock

    def register(self, sockfd, data):
        """认证登记"""
        name = data[7:]
        self.members.append({'name': name, 'sockfd': sockfd})
        self.brocast(name + ' 登入系统')

    def logout(self, sockfd):
        """退出聊天室"""
        name = ''
        remv_member = None
        for member in self.members:
            if member['sockfd'] is sockfd:
                name = member['name']
                remv_member = member
        sockfd.close()
        self.inputs.remove(sockfd)
        if name:
            self.members.remove(remv_member)
            if name == 'server':
                print('server come here...')
            self.brocast(name + '退出系统')

    def say(self, msg, sockfd):
        """发言"""
        name = ''
        for d in self.members:
            if d['sockfd'] is sockfd:
                name = d['name']
        sendmsg = name + ' say:' + msg
        print(sendmsg)
        for d in self.members:
            if d['sockfd'] is not sockfd and d['sockfd'] is not self.servsock:
                try:
                    d['sockfd'].send(sendmsg.encode())
                except BrokenPipeError:
                    self.logout(d['sockfd'])

    def brocast(self, msg):
        """发布公告"""
        sendmsg = 'server say:' + msg
        print(sendmsg)
        for d in self.members:
            if d['sockfd'] is not self.servsock:
                try:
                    d['sockfd'].send(sendmsg.encode())
                except BrokenPipeError:
                    self.logout(d['sockfd'])

    def close_server(self):
        print('服务器将退出...')
        for sockfd in self.inputs:
            sockfd.close()
        print('服务器退出')
        os._exit(0)

    def get_inputs(self):
        return self.inputs

    def get_members(self):
        return self.members


def server_say(house):
    """系统公告"""
    while True:
        s = input()
        if s:
            house.brocast(s)


def main():
    s = socket()
    s.bind(('0.0.0.0', 9999))
    s.listen()
    # 记录与服务器链接的所有线程
    inputs = [s]
    members = [{'name': 'server', 'sockfd': s}]
    house = ChatRoom(members, inputs, s)
    print('server started......')
    # 服务器要发信息的话，也在子线程完成
    t = threading.Thread(target=server_say, args=(house,))
    t.setDaemon(True)
    t.start()
    while True:
        try:
            rs, ws, es = select(house.get_inputs(), [], [])
            for r in rs:
                if r is s:
                    connfd, addr = s.accept()
                    house.get_inputs().append(connfd)
                else:
                    data = r.recv(1024).decode()
                    if not data:
                        pass
                    elif data == 'logout':
                        house.logout(r)
                    elif data[:6] == 'joinin':
                        house.register(r, data)
                    else:
                        house.say(data, r)
        except KeyboardInterrupt:
            house.close_server()


if __name__ == '__main__':
    main()
