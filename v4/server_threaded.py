import asyncio
from asyncio import exceptions
from freezefast import Freezefast
import threading
import time

clientlist = {}

roverlist = {}
stationlist = {}

msgIn_q = asyncio.Queue()
msgOut_q = asyncio.Queue()
freeze_obj = Freezefast()

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
    last_update = time.time()
    while True:
        msg_list = []
        to_rover = []
        to_hmi = []
        if msgIn_q.empty():
            to_rover = freeze_obj.handle_call_queue()
            if time.time() - last_update > 2:
                to_hmi = freeze_obj.HMI_update()
                if to_hmi:
                    await msgOut_q.put(to_hmi[0])
                last_update = time.time()
            # print("to _HMI : ",to_hmi)
            # print("to_rover: ",to_rover)
            if len(to_rover) >0 :
                await msgOut_q.put(to_rover[0])
            if to_hmi:
                await msgOut_q.put(to_hmi[0])
            await asyncio.sleep(0.1)
            continue
        msg = await msgIn_q.get()
        msg_list = freeze_obj.parse_message(msg)
        if msg_list:
            for element in msg_list:
                await msgOut_q.put(element)
        await asyncio.sleep(0.1)



async def sendMessages():
    print("sendMessage Thread active")
    while True:
        if msgOut_q.empty():
            await asyncio.sleep(0.1)
            continue
        msg = await msgOut_q.get() # msg is a (priority,destination,data)
        try:
            print(msg)
            clientlist[msg[1]][1].write(msg[2].encode())
            await clientlist[msg[1]][1].drain()
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
