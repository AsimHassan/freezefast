import asyncio
from asyncio import exceptions
import threading

clientlist = {}

roverlist = {}
stationlist = {}

msgIn_q = asyncio.Queue()
msgOut_q = asyncio.Queue()

async def connection(reader:asyncio.StreamReader,writer:asyncio.StreamWriter):
    print("new conection")
    msgIn = await reader.readuntil('.'.encode())
    msgIn = msgIn.decode()
    msgIn = msgIn[0:-1]
    msgIn = msgIn.split('|')
    clientlist["|".join(msgIn[0:2])]= (reader,writer)
    clientname ="|".join(msgIn[0:2]) 
    try:
        while True:
            msg = await reader.readuntil('.'.encode())
            msg = msg.decode().strip()
            msg = msg[0:-1]
            await msgIn_q.put(msg)
            await asyncio.sleep(0.1)
    except KeyboardInterrupt:
        print("Keyboard Interupt")
        writer.close()
        return
    except asyncio.exceptions.IncompleteReadError:
        del clientlist[clientname]
        print(f"Remote closed connection: {clientname}")

async def process():
    print("process thread ready")
    while True:
        if msgIn_q.empty():
            await asyncio.sleep(0.1)
            continue
        msg = await msgIn_q.get()

        msg = msg.split("|")
        destination = '|'.join(msg[0:2])
        payload = '|'.join(msg[2:])
        msgout = (destination,payload)
        await msgOut_q.put(msgout)
        await asyncio.sleep(0.1)



async def sendMessages():
    print("sendMessage Thread active")
    while True:
        if msgOut_q.empty():
            await asyncio.sleep(0.1)
            continue
        msg = await msgOut_q.get()
        try:
            clientlist[msg[0]][1].write(msg[1j].encode())
            await clientlist[msg[0]][1].drain()
        except KeyError:
            print("the client is disconnected")
        await asyncio.sleep(0.1)


async def server_rover():
    server = None
    try :
        server = await asyncio.start_server(
                connection,
                '192.168.3.64',
                1234)
        print("Server Running")
        async with server:
            await server.serve_forever()
    except KeyboardInterrupt:
        server.close()



def worker1():
    asyncio.run(process())

def worker2():
    asyncio.run(sendMessages())

def worker3():
    try :
        asyncio.run(server_rover())
    except KeyboardInterrupt:
        print("Interrupt")
    except:
        raise


if __name__ == '__main__':
    threads = []
    t1 = threading.Thread(target=worker3)
    t2 = threading.Thread(target=worker2)
    threads.append(t1)
    threads.append(t2)

    t1.start()
    t2.start()
    worker1()
