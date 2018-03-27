import random
import socket
import threading

import remoteCLI


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
