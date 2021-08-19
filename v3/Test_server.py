import asyncio
from asyncio import exceptions
import threading
import time

clientlist = {}

roverlist = {}
stationlist = {}

msgIn_q = asyncio.Queue()
msgOut_q = asyncio.Queue()
class processor:
    def __init__(self):
        self.rover= 'ROVER|1'
    def parse_message(self,msg):
        if 'STATION' in msg:
            returnlist = self.parse_station(msg)
        elif 'ROVER' in msg:
            returnlist = self.parse_rover(msg)

        else:
            returnlist = []

        return returnlist
    def parse_rover(self,msg):
        print(msg)
        return []
    def parse_station(self,msg):
        returnaddr = msg[:9]

        if 'CALL' in msg :
            return [(5,self.rover,"FORWARD"),(8,returnaddr,"CALL|ACK")]
        if 'GO' in msg:
            return [(5,self.rover,"REVERSE"),(8,returnaddr,"GO|ACK")]
        if 'ROVERCROSSED' in msg:
            return [(5,self.rover,"SLOWDOWN"),(8,returnaddr,"CROSS|YES")]
        if 'STOP' in msg:
            return [(5,self.rover,"STOP"),(8,returnaddr,"STOP|ACK")]
        if 'EMERGENCY' in msg:
            return [(5,self.rover,"EMERGENCY"),(8,returnaddr,"EMERGENCY|ACK")]

obj = processor()
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
    try:
        while True:
            msg_list = []
            to_rover = []
            to_hmi = []
            if msgIn_q.empty():
                await asyncio.sleep(0.1) 
                continue
            msg = await msgIn_q.get()
            msg_list = obj.parse_message(msg)
            if msg_list:
                for element in msg_list:
                    await msgOut_q.put(element)
            await asyncio.sleep(0.1)
    except KeyboardInterrupt:
        pass
    except:
        raise



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
    try:
        t1.start()
        t2.start()
        worker1()
    except KeyboardInterrupt:
        print("Exiting")

