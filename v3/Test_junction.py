import asyncio
import aioconsole
states = {
    'STATE:0':"IDLE",
    'STATE:1':"ROVER_CROSS",
    'STATE:2':"ROVER_CROSS_INTER",
    'STATE:3':"ROVER_CROSS2",
    'STATE:4':"ROVER_HERE",
    'STATE:5':"ROTATE",
    'STATE:6':"ROVER_READY_TO_LEAVE",
    'STATE:7':"ROVER_LEAVING",
    'STATE:8':"ROVER_LEAVING2",
    'STATE:9':"ROVER_LEFT",
    'STATE:10':"JUNCTION_ERROR"
}
ip = '192.168.3.64'
portno = 1234
async def Test_rover(reader:asyncio.StreamReader,writer:asyncio.StreamWriter):
    data = await reader.read(100)
    message = data.decode()
    print(message)
    print("Connnected")
    print("""
          1. CROSS
          2. STRAIGHT
          """)
    try:
        while True:
            await asyncio.sleep(0.1)
            try:
                choice = await asyncio.wait_for(aioconsole.ainput(""),0.5)
            except asyncio.TimeoutError:
                choice = '0'
            except:
                raise

            if choice == '1':
                writer.write("ROTATE|CROSS.".encode())
            if choice == '2':
                writer.write("ROTATE|STRAIGHT.".encode())

            try :
                message = await asyncio.wait_for(reader.readuntil(".".encode()),0.2)
                if len(message) > 0:
                    message = message.decode()
                    message.strip()
                    message = message[:-1]

                    await aioconsole.aprint(message,end=":")

                    message = message.split("|")
                    if 'STATE' in message[-1]:
                        await aioconsole.aprint(states[message[-1]])
            except asyncio.TimeoutError:
                pass
            except:
                raise
    except :
        print("lost connection")
        raise

async def main():
    server = await asyncio.start_server(Test_rover,ip,portno)
    addr = server.sockets[0].getsockname()
    print(f"serving om {addr}")
    async with server:
        await server.serve_forever()
try:
    asyncio.run(main())
except:
    print("program exiting")
