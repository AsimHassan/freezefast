import asyncio
import rover

callFlag = False

ip = '192.168.3.64'
portno = 1234
async def Test_station(reader:asyncio.StreamReader,writer:asyncio.StreamWriter):
    data = await reader.read(100)
    message = data.decode()
    print(message)
    try:
        while True:
            data = await reader.readuntil(".".encode())
            message = data.decode().strip('\n')
            message = message[:-1]
            print(message)
            splitmsg = message.split('|')
            if 'CALL' in splitmsg:
                writer.write('CALL|ACK.'.encode())
                callFlag = True
            if 'GO' in splitmsg:
                writer.write('GO|ACK.'.encode())
                callFlag = False
            if 'ROVERCROSSED' in splitmsg:
                if callFlag == True:
                    writer.write('CROSS|YES.'.encode())
                else:
                    writer.write('CROSS|NO.'.encode())
            if 'STOP' in splitmsg:
                writer.write('STOP|ACK.'.encode())
            if 'EMERGENCY' in splitmsg:
                writer.write('EMERGENCY|ACK.'.encode())

            await writer.drain()

            pass
    except :
        print("lost connection")

async def main():
    server = await asyncio.start_server(Test_station,ip,portno)
    addr = server.sockets[0].getsockname()
    print(f"serving om {addr}")
    async with server:
        await server.serve_forever()
try:
    asyncio.run(main())
except:
    print("program exiting")
