#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import socket


class cli():
    buffer: str
    sck: socket.socket
    charset: str

    def __init__(self, buffer=str(), sck=socket.socket(socket.AF_INET, socket.SOCK_STREAM), charset="utf-8"):
        self.buffer = buffer
        self.sck = sck
        self.charset = charset

    def __del__(self):
        try:
            self.sck.close()
        except Exception:
            pass

    def connect(self, address: str, port: int):
        self.sck.connect((address, port))

    def reconnect(self, address: str, port: int):
        self.sck.close()
        self.sck.connect((address, port))

    def recvline(self, lineCount=1):
        '''
        Receive lines.

        Example: recvline(3) \n
        Received "123\\n456\\n789\\n!@#" from remote. \n
        Will return list(["123","456","789"]) and keeping "!@#" in buffer.
        '''

        lines = list()

        while len(lines) < lineCount:
            index = self.buffer.find('\n')
            while index == -1:
                self.buffer += self.sck.recv(2048).decode(self.charset)
                index = self.buffer.find('\n')
            lines.append(self.buffer[0:index])
            self.buffer = self.buffer[index + 1:]

        return lines

    def recvUntilHave(self, target: str):
        '''
        Receive data until contain target in it.

        Example: recvUntilHave("flag") \n
        Received "zxc\\nvbbnmflagqwe" from remote. \n
        Will return "zxc\\nvbbnmflag" and keeping "qwe" in buffer.
        '''

        index = self.buffer.find(target)
        while index == -1:
            self.buffer += self.sck.recv(2048).decode(self.charset)
            index = self.buffer.find(target)
        data = self.buffer[0:index + len(target)]
        self.buffer = self.buffer[index + len(target):]

        return data

    def recvLinesUntilHave(self, target: str):
        '''
        Receive lines until contain target in it.

        Example: recvUntilHave("flag") \n
        Received "zxc\\nvbbnmflagqwe\\nsomethingelse\\n233" from remote. \n
        Will return list(["zxc", "vbbnmflagqwe"]) and keeping "somethingelse\\n233" in buffer.
        '''

        targetIndex = self.buffer.find(target)
        while targetIndex == -1:
            self.buffer += self.sck.recv(2048).decode(self.charset)
            targetIndex = self.buffer.find(target)

        index = self.buffer.find('\n', targetIndex)
        while index == -1:
            self.buffer += self.sck.recv(2048).decode(self.charset)
            index = self.buffer.find('\n', targetIndex)

        data = self.buffer[0:index]
        self.buffer = self.buffer[index + 1:]

        return data.split('\n')

    def recvUntilMatch(self, regEx: str):
        '''
        Receive data until match the regEx.

        Example: recvUntilHave("flag{.+}") \n
        Received "zxc\\nvbbnmflag{2333}can'tseeme\\nsomethingelse" from remote. \n
        Will return "zxc\\nvbbnmflag{2333}" and keeping "can'tseeme\\nsomethingelse" in buffer.
        '''

        reg = re.compile(regEx)

        while True:
            try:
                iter = reg.finditer(self.buffer)
                result = iter.__next__()
                data = self.buffer[0:result.end()]
                self.buffer = self.buffer[result.end():]
                break
            except StopIteration:
                self.buffer += self.sck.recv(2048).decode(self.charset)

        return data

    def recvLinesUntilMatch(self, regEx: str):
        '''
        Receive lines until match the regEx.

        Example: recvUntilHave("flag{.+}") \n
        Received "zxc\\nvbbnmflag{2333}can'tseeme\\nsomethingelse" from remote. \n
        Will return list(["zxc", "vbbnmflag{2333}can'tseeme"]) and keeping "somethingelse" in buffer.
        '''

        reg = re.compile(regEx)

        while True:
            try:
                iter = reg.finditer(self.buffer)
                result = iter.__next__()
                break
            except StopIteration:
                self.buffer += self.sck.recv(2048).decode(self.charset)

        index = self.buffer.find('\n', result.end())
        while index == -1:
            self.buffer += self.sck.recv(2048).decode(self.charset)
            index = self.buffer.find('\n', result.end())

        data = self.buffer[0:index]
        self.buffer = self.buffer[index + 1:]

        return data.split('\n')

    def sendData(self, data):
        try:
            data = data.encode()
        except Exception:
            pass
        self.sck.sendall(data)

    def sendLine(self, data):
        try:
            data = data.encode()
        except Exception:
            pass
        data = data+'\n'.encode()
        self.sck.sendall(data)
