#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import socket
import threading


class CLI():
    buffer: str
    sck: socket.socket
    charset: str

    def __init__(self, charset="utf-8"):
        self.buffer = str()
        self.sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.charset = charset

    def __del__(self):
        try:
            self.sck.close()
        except Exception:
            pass

    def connect(self, address: str, port: int):
        self.sck.connect((address, port))

    def reconnect(self, address: str, port: int, resetBuffer=True):
        if resetBuffer:
            self.buffer = str()

        try:
            self.sck.close()
        except Exception:
            pass

        self.sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sck.connect((address, port))

    def recvline(self, lineCount=1):
        '''
        Receive lines.

        Example: `recvline(3)`   
        If received `"123\\n456\\n789\\n!@#"` from remote.  
        Will return `list(["123","456","789"])` and keeping `"!@#"` in buffer.
        '''

        lines = list()

        while len(lines) < lineCount:
            index = self.buffer.find('\n')
            while index == -1:
                self.buffer += self.sck.recv(2048).decode(self.charset)
                index = self.buffer.find('\n')
            lines.append(self.buffer[0:index])
            self.buffer = self.buffer[index + 1:]

        if lineCount == 1:
            return lines[0]
        else:
            return lines

    def recvUntilHave(self, target: str):
        '''
        Receive data until contain target in it.

        Example: `recvUntilHave("flag")`  
        If received `"zxc\\nvbbnmflagqwe"` from remote.  
        Will return `"zxc\\nvbbnmflag"` and keeping `"qwe"` in buffer.
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

        Example: `recvUntilHave("flag")`  
        If received `"zxc\\nvbbnmflagqwe\\nsomethingelse\\n233"` from remote.  
        Will return `list(["zxc", "vbbnmflagqwe"])` and keeping `"somethingelse\\n233"` in buffer.
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

    def recvUntilFind(self, regEx: str, onlyReturnRegEx=False):
        '''
        Receive data until regEx can be found.

        Example: `recvUntilHave("flag\\{.+\\}")`   
        If received `"zxc\\nvbbnmflag{2333}can'tseeme\\nsomethingelse"` from remote.           
        Will return `"zxc\\nvbbnmflag{2333}"` and keeping `"can'tseeme\\nsomethingelse"` in buffer. 

        If `onlyReturnRegEx == True`, will only return `"flag{2333}"` and keeping `"can'tseeme\\nsomethingelse"` in buffer. 

        Additional, if have group, like `'('` and `')'` in regEx , it will return all groups.        
        Example: `recvUntilHave("test([0-4]{1,})([5-9]{1,})abc)`  
        Received `"test123456789abcdefg"` from remote.  
        Will return `list(["1234","56789"])` and keeping `"abcdefg"` in buffer.  
        '''

        reg = re.compile(regEx)

        while True:
            try:
                iter = reg.finditer(self.buffer)
                result = iter.__next__()

                if len(result.regs) == 1:
                    if onlyReturnRegEx:
                        data = self.buffer[result.start():result.end()]
                    else:
                        data = self.buffer[0:result.end()]
                    self.buffer = self.buffer[result.end():]
                else:
                    data = list(result.groups())
                    # result.regs[-1][1] is the index of last char in groups.
                    self.buffer = self.buffer[result.regs[-1][1]:]
                break
            except StopIteration:
                self.buffer += self.sck.recv(2048).decode(self.charset)

        return data

    def recvLinesUntilFind(self, regEx: str):
        '''
        Receive lines until regEx can be found.

        Example: `recvUntilHave("flag\\{.+\\}")`  
        Received `"zxc\\nvbbnmflag{2333}can'tseeme\\nsomethingelse"` from remote.  
        Will return `list(["zxc", "vbbnmflag{2333}can'tseeme"])` and keeping `"somethingelse"` in buffer.
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

    def console(self):
        '''
        Start interacting, just like nc.
        '''
        def listen():
            while True:
                print(self.sck.recv(2048).decode(), end='')

        threading.Thread(target=listen).start()
        print(self.buffer, end='')
        
        while True:
            data = input()
            self.sendLine(data)
