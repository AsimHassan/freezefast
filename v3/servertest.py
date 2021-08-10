"""module to handle incomming connections asynchronously""" 
import asyncio
import rover
import station

rover_list = []
station_list = []
async def handle_connection(
        reader:asyncio.StreamReader,
        writer:asyncio.StreamWriter):
    """async function to deal with connections"""
    msgin = await reader.readuntil('.'.encode("utf8")) # get message if any on initial connection
    msgin = msgin.decode("utf8")
    msgin = msgin.split('|')
    client = None
    client_type = None
    ''' first message sent by client will have its type and status'''
    if "ROVER" in msgin:
        client = rover.Rover(msgin[1],0,1,writer,reader)
        rover_list.append(client)
        client_type = "rover"
    if "STATION" in msgin:
        if len(rover_list) == 0: # check if any rovers have been connected
            print (" no rover connected ")
            return
        else:
            client = station.Station(
                    msgin[1],
                    1,
                    rover_list[0],
                    reader,
                    writer)

            station_list.append(client)
        client_type = "station"
    if "HMI" in msgin:
        client = station.HMI(reader,writer,rover_list[0],'1')
        client_type = 'HMI'

    print("Station list:  ", end="")
    print(station_list)
    print("Rover list:  ", end="")
    print(rover_list)
    # main server loop continous lt await the clients messages
    while True:
        retval = 0
        queue_status = 0
        try:
            # HMI client 
            if client_type == 'HMI':
                try:
                    await asyncio.wait_for(client.get_message(),0.2)
                except asyncio.TimeoutError:
                    pass
                except :
                    raise
                await client.sendupdate()
                # Rover client
            elif client_type == "rover":
                retval = await client.update_state()
                queue_status = await client.work_on_queue()
                await client.debug()
                # Station client
            elif client_type == "station":
                retval = await client.station_read()
                await client.debug()
        except asyncio.IncompleteReadError:
            print("Client disconnected ")
            break
        except Exception as ex: # triggered mainly by disconnection of client catch it and remove client from list
            print(ex)
            if client_type == "rover":
                rover_list.remove(client)

            elif client_type == "station":
                station_list.remove(client)
            print("exception happened",ex)
            raise

async def main():
    server = None
    try :
        server = await asyncio.start_server(
                handle_connection,
                '192.168.3.64',
                1234)
        print("Server Running")
        async with server:
            await server.serve_forever()
    except KeyboardInterrupt:
        server.close()

# the main loop starts here
try:
    asyncio.run(main())
except KeyboardInterrupt: # catches ctrl+c and exits
    print()
    print("exiting......")
