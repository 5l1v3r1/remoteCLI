import remoteCLI

cli = remoteCLI.CLI()
cli.connect("127.0.0.1", 12345)
print(cli.recvline())

for i in range(100):
    paras = cli.recvUntilFind(r"([0-9]{1,}) \+ ([0-9]{1,})")  
    answer = int(paras[0]) + int(paras[1])
    print(i, paras, answer)
    cli.sendLine(str(answer))

while True:
    print(cli.recvline())