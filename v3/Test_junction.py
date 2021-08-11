import asyncio
import aioconsole
import rover
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
            try:
                choice = await asyncio.wait_for(aioconsole.ainput(),0.5)
            except asyncio.TimeoutError:
                choice = '0'
            except:
                raise

            if choice == '1':
                await writer.write("ROTATE|CROSS")
            if choice == '2':
                await writer.write("ROTATE|STRAIGHT")
            try :
                message = await asyncio.wait_for(rover_obj.update_state(),0.5)
                if message:
                    message = message.decode()
                    print(message)
            except asyncio.TimeoutError:
                pass
            except:
                raise
    except :
        print("lost connection")

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
