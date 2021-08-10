"""
A module to take care of the rover and its functions
"""
import asyncio

class MyQueue:
    """
    An Implementation of Queue for holding the next element in call

    """

    def __init__(self):
        """
        inintialize the queue
        """
        self.holder = []

    def enqueue(self,val):
        """
        add items to queue
        """
        self.holder.append(val)

    def dequeue(self):
        """
        take out items from the queue
        """
        val = None
        try:
            val = self.holder[0]
            self.holder = [] if len(self.holder) == 1 else self.holder[1:]
        except IndexError:
            print("Nothing in queue")

        return val

    def is_empty(self):
        """
        return true if the queue is empty
        """
        result = False
        if len(self.holder) == 0:
            result = True
        return result

    def peek(self):
        """
        returns the element on top does not remove it from the queue
        """
        if len(self.holder) == 0:
            return None
        return self.holder[0]


class Rover:
    """
    class to handle all things rover
    """
    def __init__(self,
                 rover_id,
                 position,
                 state,
                 writer:asyncio.StreamWriter,
                 reader:asyncio.StreamReader):

        """ inintialize the rovers """
        self.rover_id = rover_id
        self.position = position
        self.state = state
        self.writer = writer
        self.reader = reader
        self.callq = MyQueue()
        self.destination = position
        self._last_debug_msg = ""

    async def move_forward(self):
        """
        send a comman to move forward
        """
        self.writer.write("ROVER|FORWARD.".encode("utf8"))
        await self.writer.drain()
        #ack = await self.reader.readuntil(".".encode("utf8"))
        #if ack.decode("utf8") == "FORWARD|ACK." :
        #    print("move_forward :success")

    async def move_reverse(self):
        """
        send a message to move reverse
        """
        self.writer.write("ROVER|REVERSE.".encode("utf8"))
        await self.writer.drain()
        #ack = await self.reader.readuntil(".".encode("utf8"))
        #if ack.decode("utf8") == "REVERSE|ACK.":
        #    print("move_reverse :success")

    async def move(self):
        """
        send a move signal, blocks the rover from doing anything with athe queue
        """
        self.writer.write("ROVER|START.".encode("utf8"))
        await self.writer.drain()
        #ack = await self.reader.readuntil(".".encode("utf8"))
        #if ack.decode("utf8") == "START|ACK." :
        #    print("move :success")

    async def slow_down(self):
        """
        send a slowdown signal to the rover
        """
        self.writer.write("ROVER|SLOWDOWN.".encode("utf8"))
        await self.writer.drain()
        #ack = await self.reader.readuntil(".".encode("utf8"))
        #if ack.decode("utf8") == "SLOWDOWN|ACK." :
        #    print("slowdown :success")

    async def stop(self):
        """
        send a stop signal to rover
        """
        self.writer.write("ROVER|STOP.".encode("utf8"))
        await self.writer.drain()
        #ack = await self.reader.readuntil(".".encode("utf8"))
        #if ack.decode("utf8") == "STOP|ACK":
        #    print("Stop :success")
    async def update_state(self):
        """
        updates the state of rover
        """
        msg = await self.reader.readuntil('.'.encode("utf8"))

        msg = msg.decode("utf8")
        msg = msg[:-1]
        print(msg)

        splitmsg = msg.split('|')
        if "ACK" in splitmsg:
            print(f"Acknowledge message in : {splitmsg[0]}")
        elif "OBSTACLE" in splitmsg:
            print("hit an obstacle ")
        else:
            self.state = splitmsg[2]


    def get_direction(self, destination:int):
        """
        figure out the direction of travel from the destination and current positon
        """
        if int(destination) - int(self.position) > 0 :
            return "forward"
        if int(destination) - int(self.position) < 0 :
            return "reverse"
        return "stop"

    async def work_on_queue(self):
        """
        works on the queue if the rover is in idle or resting state
        return a string:
            busy if the rover is in state other than mentioned above

            need to check if its in emergency mode

        """
        if self.state not in ["STATE:0", "STATE:1"]:
            return 0
        if not self.callq.is_empty():
            next_destination = int(self.callq.dequeue())
            self.destination = next_destination
            direction = self.get_direction(next_destination)
            if direction == "forward":
                await self.move_forward()
            elif direction == "reverse":
                await self.move_reverse()
            else:
                await self.stop()
            return 2
        return 1

    async def debug(self):
        debug_msg = f"Rover:ID:{self.rover_id} | callq:{self.callq.holder}|state: {self.state}|"+\
                    f"Destination: {self.destination}| position: {self.position}"
        if debug_msg != self._last_debug_msg:
            print(debug_msg)
            self._last_debug_msg = debug_msg
        await asyncio.sleep(1)
