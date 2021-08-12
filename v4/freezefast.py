import queue
from enum import Enum, auto
positions = {
    "1":1,
    "2":2,
    "3":3,
    "4":4,
    "STORE":5.1,
    "COLDROOM":5.2,
    "JUNCTION":5,
    "6":6,
    "7":7,
    "8":8
}
class Msgpriority:
    STOP = 2
    SLOWDOWN = 3
    CALL = 5
    GO = 5
    ACK = 8

class RoverStates(Enum):
    RESET = 0
    RESTING = 1
    SLOWDOWN = 2
    STOPPED = 3
    BUZZER = 4
    MOVING = 5
    OBSTACLE = 6
    EMERGENCY_STOP = 7
    REVERSE = 9
    FORWARD = 8
    BLOCKED_TILL_UPDATE = 99

class JunctionStates(Enum):
    IDLE = 0
    ROVER_CROSS = 1
    ROVER_CROSS_INTER = 2
    ROVER_CROSS2 = 3
    ROVER_HERE = 4
    ROTATE = 5
    ROVER_READY_TO_LEAVE = 6
    ROVER_LEAVING = 7
    ROVER_LEAVING2 = 8
    ROVER_LEFT = 9
    JUNCTION_ERROR = 10

class StationStates():
    RESET = 0
    RESTING = 1
    SLOWDOWN = 2
    STOPPED = 3
    BUZZER = 4
    MOVING = 5
    OBSTACLE = 6
    EMERGENCY_STOP = 7
    FORWARD = 8
    REVERSE = 9

def get_direction(position, destination):
    if destination - position > 0:
        return "FORWARD"
    elif destination - position < 0:
        return "REVERSE"
    else:
        return "STOP"



class Freezefast:

    def __init__(self) -> None:
        self.ROVER="ROVER|1"
        self.station={}
        self.JUNCTION="JUNCTION|1"
        self.HMI = "HMI|1"
        self.STORE = "STORE"
        self.COLDROOM = "COLDROOM"
        self.callq = queue.Queue()
        self.rover_position = positions["1"]
        self.rover_destination = positions["1"]
        self.rover_state = RoverStates.RESET.value
        self.junction_state = JunctionStates.IDLE.value
        self.junction_position = 'STRAIGHT'

    def handle_call_queue(self):
        if self.rover_state == RoverStates.RESTING.value:
            if not self.callq.empty():
                destination = self.callq.get()
                if int(destination) != positions["JUNCTION"]:
                    direction = get_direction(self.rover_position,destination)
                    return [(Msgpriority.GO,self.ROVER,direction)]
                else:
                    #TODO Junction logicj
                    pass
                
        return []


    def parse_message(self,msg:str):
        splitmsg = msg.split('|')
        list_returns = [] # store list of tuples with (priority,destination,data)
        if "STATION" in splitmsg:
            return self.parse_station(splitmsg)  # return list of tuple

        if "ROVER" in splitmsg:
            (destination,message) = self.parse_rover(splitmsg[2:]) 
        if "JUNCTION" in splitmsg:
            (destination,message) = self.parse_junction(splitmsg[2:]) 
        if "HMI" in splitmsg:
            (destination,message) = self.parse_hmi(splitmsg[2:]) 

    def parse_station(self,msg:list):
        sendbackaddr = "|".join(msg[:2])
        #TODO Parse CALL
        if 'CALL' in msg:
            return self._parse_station_call(msg,sendbackaddr) # return list of tuple


        #TODO Parse GO
        if 'GO' in msg:
            return self._parse_station_go(msg,sendbackaddr) # return list of tuple


        #TODO Parse ROVERCROSS
        if 'ROVERCROSS' in msg:
            return self._parse_station_rovercross(msg,sendbackaddr)
        #TODO Parse SLOWDOWN
        if 'SLOWDOWN' in msg:
            return self._parse_station_slowdown(msg,sendbackaddr)
        #TODO Parse STOP
        if 'STOP' in msg:
            return self._parse_station_stop(msg,sendbackaddr) 
        #TODO Emergency STOP
        #TODO RESTART


    def _parse_station_call(self, msg,sendbackaddr):
        called_station = msg[1]
        self.callq.put(positions[called_station])
        msg_call_ack = 'CALL|ACK'
        msg_priority = Msgpriority.ACK
        return [(msg_priority,sendbackaddr,msg_call_ack)]
    
    def _parse_station_go(self, msg,sendbackaddr):
        msg_go_ack = 'GO|ACK'
        self.rover_destination = positions["COLDROOM"]
        direction = get_direction(self.rover_position,self.rover_destination)
        to_rover = (Msgpriority.GO,self.ROVER,direction)
        to_station = (Msgpriority.ACK,sendbackaddr,msg_go_ack)
        return [to_rover,to_station]
    
    def _parse_station_slowdown(self,msg,sendbackaddr):
        to_station = (Msgpriority.ACK,sendbackaddr,'SLOWDOWN|ACK')
        to_rover = (Msgpriority.SLOWDOWN,self.ROVER,'SLOWDOWN')
        return[to_rover,to_station]
         
    def _parse_station_stop(self,msg,sendbackaddr):
        self.rover_position = positions[msg[1]]
        msg_ack = 'STOP|ACK'
        msg_priority = Msgpriority.ACK
        to_station = (msg_priority,sendbackaddr,msg_ack)
        to_rover = (Msgpriority.STOP,self.ROVER,'STOP')
        return[to_rover,to_station]

    def _parse_station_rovercross(self,msg,sendbackaddr):
        self.rover_position = positions[msg[1]]
        if self.rover_destination == self.rover_position :
            to_rover = (Msgpriority.SLOWDOWN,self.ROVER,'SLOWDOWN')
            to_station = (Msgpriority.SLOWDOWN,sendbackaddr,"CROSS|YES")
            return [to_rover,to_station]
        else:
            to_station = (Msgpriority.ACK,sendbackaddr,"CROSS|NO")
            return [to_station]



    
    def parse_rover(self,msg:list):
        #TODO ACKS
        if 'ACK' in msg:
            print(" ".join(msg))
        #TODO Updates
        if 'STATE' in msg[-1]:
            [_,state] = msg[-1].split(':')
            state = int(state)
            self.rover_state = RoverStates(state).value
            print("rover State:" + RoverStates(state).name)


    def parse_junction(self,msg:list):
        #TODO UPDATES
        state = int(msg[-1])
        self.junction_state =  JunctionStates(state).value
        print("JUNCTION: "+ JunctionStates(state).name)

        if state == JunctionStates.ROVER_HERE.value:
            if self.junction_position == 'STRAIGHT':
                to_junction= (Msgpriority.GO,self.JUNCTION,"ROTATE|CROSS")
            else :
                to_junction= (Msgpriority.GO,self.JUNCTION,"ROTATE|STRAIGHT")
            return [to_junction]

        
        #TODO SLOWDOWN
        if 'SLOWDOWN' in msg:
            to_rover = (Msgpriority.SLOWDOWN, self.ROVER,"SLOWDOWN")
            return [to_rover]
        #TODO STOP
        if 'STOP' in msg:
            to_rover = (Msgpriority.STOP,self.ROVER,"STOP")
            return [to_rover]
        #TODO ROTATION|DONE
        if 'DONE' in msg:
            if self.junction_position == 'STRAIGHT':
                self.junction_position = "CROSS"
            else:
                self.junction_position = 'STRAIGHT'

            if int(self.rover_destination) == 5:
                if self.rover_destination == 5.1:
                    to_rover = (Msgpriority.GO,self.ROVER,"FORWARD")
                elif self.rover_destination == 5.2:
                    to_rover = (Msgpriority.GO,self.ROVER,"REVERSE")
            else:
                direction = get_direction(5,self.rover_destination)
                to_rover = (Msgpriority.GO,self.ROVER,direction)

            return [to_rover]    
                

    
    def parse_hmi(self,msg:list):
        #TODO CALL
        if 'CALL' in msg:
            called_station = msg[0]
            self.callq.put(positions[called_station])
            msg_call_ack = 'CALL|ACK'
            msg_priority = Msgpriority.ACK
            return [(msg_priority,self.HMI,msg_call_ack)]
        #TODO GO
        #TODO E_STOP
        #TODO RESTART
        #TODO UPDATES





