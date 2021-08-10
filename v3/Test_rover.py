import asyncio
import aioconsole
import rover
ip = '192.168.3.64'
portno = 1234
async def Test_rover(reader:asyncio.StreamReader,writer:asyncio.StreamWriter):
    data = await reader.read(100)
    message = data.decode()
    print(message)
    rover_obj = rover.Rover('1',0,0,writer,reader)

    print("Rover initialized")
    print("""
          1. Forward
          2. Reverse
          3. Slowdown
          4. Stop
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
                await rover_obj.move_forward()
            if choice == '2':
                await rover_obj.move_reverse()
            if choice == '3':
                await rover_obj.slow_down()
            if choice == '4':
                await rover_obj.stop()
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
