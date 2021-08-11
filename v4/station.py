"""
module to handle the station functions
"""
import asyncio
import rover
#handleCall
#handleGo
#handleCrossing
#handleEmergency
# Need to develop better way to identify and send rover to coldroom and store
COLDROOM = 5
STORE = 5
class Station:
    """
    Class to handle the station functions
    """
    def __init__(
            self,
            station_id,
            state,
            rover_obj:rover.Rover,
            reader:asyncio.StreamReader,
            writer:asyncio.StreamWriter):

        self.rover_obj = rover_obj
        self.state = state
        self.station_id = station_id
        self.reader = reader
        self.writer = writer
        self._previous_state=0


    async def station_read(self):
        """
        functions read from the socket and sends the messages as required
        """
        msg = await self.reader.readuntil('.'.encode("utf8"))
        msg = msg.decode("utf8")
        msg = msg[:-1]
        print(msg)
        msg = msg.split('|')
        print("msgtype = " + msg[2])
        msgtype = msg[2]
        print(msg)
        if msgtype == "STATE":
            statemsg =  msg[2].split(":")
            self.state = statemsg
        if (
            msgtype == "CALL"
            and self.station_id not in self.rover_obj.callq.holder
        ):
            self.rover_obj.callq.enqueue(self.station_id)
            self.writer.write("CALL|ACK.".encode("utf8"))
        if msgtype == "GO" and self.rover_obj.state in ["STATE:0", "STATE:1"]:
            if self.rover_obj.position != self.station_id:
                print("not for you dummy, wait")
                return
            if self.rover_obj.position == self.station_id:
                print("sending the go signal now")
                self.rover_obj.destination = COLDROOM
                direction = self.rover_obj.get_direction(self.rover_obj.destination)
                if direction == "forward":
                    await self.rover_obj.move_forward()
                elif direction == "reverse":
                    await self.rover_obj.move_reverse()
                else:
                    await self.rover_obj.stop()
                self.writer.write("GO|ACK.".encode("utf8"))
        if msgtype == "STOP":
            await self.rover_obj.stop()
            print("send Stop")

        if msgtype == "ROVERCROSSED" :
            print(f"ROVERCROSSED||id:{type(self.station_id)}||roverdes:{type(self.rover_obj.destination)}")
            if int(self.rover_obj.destination) == int(self.station_id) :
                await self.rover_obj.slow_down()
                self.writer.write("CROSS|YES.".encode("utf8"))
                self.rover_obj.position = self.station_id
            else :
                self.rover_obj.position = self.station_id
                self.writer.write("CROSS|NO.".encode("utf8"))
        if msgtype == "EMERGENCY":
            await self.rover_obj.stop()

    async def debug(self):
        if self._previous_state != self.state:
            print(f"STATION:ID:{self.station_id}|state: {self.state}|")
            self._previous_state = self.state

        await asyncio.sleep(1)

    def update_rover_object(self,new_rover_obj:rover.Rover):
        self.rover_obj = new_rover_obj

        pass

"""
HMI requiremenets
inputs(parameters)?:
    reader
    writer
    ID
    rover

Call the rover - no change in priority just add to queue HMI -> Rover
Ability to select a destination location HMI -> Rover
Send Go command HMI -> Rover
Actiave EMERGENCY stop HMI -> Rover
deactivate EMERGENCY stop HMI -> Rover
status update on rover rover -> HMI

"""
class HMI(Station):
    def __init__(self,
                 reader:asyncio.StreamReader,
                 writer:asyncio.StreamWriter,
                 rover_obj:rover.Rover,
                 HMI_ID: str):

        self.reader = reader
        self.writer = writer
        self.rover_obj = rover_obj
        self.HMI_ID =HMI_ID

    async def sendupdate(self):
        msg = f"Rover|{self.rover_obj.rover_id}"+\
                f"|{self.rover_obj.position}"+\
                f"|{self.rover_obj.destination}."
        self.writer.write(msg.encode("utf8"))
        await self.writer.drain()
        await asyncio.sleep(1)

    async def get_message(self):
        msg = await self.reader.readuntil('.'.encode())
        msg = msg.decode()
        msg = msg[:-1]
        splitmsg = msg.split('|')
        if "CALL" in splitmsg:
            self.rover_obj.callq.enqueue(STORE)
            self.writer.write("Update|Call successfully added to queue.".encode())

        if "GO" in splitmsg:

            if self.rover_obj.position == str(STORE):
                destination = splitmsg[2]
                direction = self.rover_obj.get_direction(int(destination))
                self.rover_obj.destination = destination
                if direction == "forward":
                    await self.rover_obj.move_forward()
                elif direction == "reverse":
                    await self.rover_obj.move_reverse()
                else:
                    await self.rover_obj.stop()
                self.writer.write("Update|Go send to Rover".encode())
            else:
                self.writer.write("Rover not at store.".encode())
                print("rover not in store")

        if 'EMERGENCY' in splitmsg:
            self.rover_obj.stop()

        if 'RESTART' in splitmsg:
            direction = self.rover_obj.get_direction(self.rover_obj.destination)
            if direction == "forward":
                await self.rover_obj.move_forward()
            elif direction == "reverse":
                await self.rover_obj.move_reverse()
            else:
                await self.rover_obj.stop()
            self.writer.write("Update|Sent direction to rover".encode())

    async def runHMI(self):
        await asyncio.wait_for(self.get_message(),0.2)
        await self.sendupdate()




