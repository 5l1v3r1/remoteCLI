# Remote CLI

> 一个对socket简单的封装

有时候会碰到通过 nc 来交互的 miscs 或者 crypto 题， 于是就想着做个简单的封装吧  
省的大佬们手输答案233

## Examples

### server

```python
def handle(subsck):
    cli = remoteCLI.CLI()
    cli.sck = subsck
    cli.sendLine("100 rounds test, are you ready?")

    for i in range(100):
        x = random.randint(0, 100)
        y = random.randint(0, 100)

        cli.sendLine(str(x)+' + '+str(y)+' = ?')
        answer = cli.recvline()
        print(x, y, answer)

        if int(answer) == x+y:
            if i == 99:
                cli.sendLine("Congratulations, you got it.")
        else:
            cli.sendLine("Oops, better luck next time.")
            break

    cli.sck.close()
    return


mainsck = socket.socket()
mainsck.bind(("127.0.0.1", 12345))
mainsck.listen()

while True:
    subsck, addr = mainsck.accept()
    print(str(addr)+"connected")
    threading.Thread(target=handle, args=(subsck,)).start()
```

### client

```python
cli = remoteCLI.CLI()
cli.connect("127.0.0.1", 12345)
print(cli.recvline())

for i in range(100):
    paras = cli.recvUntilFind(r"([0-9]{1,}) \+ ([0-9]{1,})")
    answer = int(paras[0]) + int(paras[1])
    print(i, paras, answer)
    cli.sendLine(str(answer))

cli.console()
```

### output

> 100 rounds test, are you ready?
0 ['29', '33'] 62  
1 ['40', '34'] 74  
...  
...  
99 ['7', '43'] 50  
 = ?  
Congratulations, you got it.  
