#! /home/asim/projects/RoverProject/.venv/bin/python
import asyncio

async def handle_echo(reader, writer):
    try:
        while True:
            data = await reader.read(100)
            message = data.decode()
            if len(message) == 0:
                break

            addr = writer.get_extra_info('peername')

            print(f"Received {message!r} from {addr!r}")

            writer.write(data)
            await writer.drain()
            print(f"Send: {message!r}")
    except:
        print("Close the connection")
        writer.close()

async def main():
    server = await asyncio.start_server(
        handle_echo, '192.168.3.64', 1234)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()

asyncio.run(main())
