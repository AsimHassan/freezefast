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

class RoverStates():
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

class JunctionStates():
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
        self.rover_state = RoverStates.RESET
        self.junction_state = JunctionStates.IDLE

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
        #TODO Parse CALL
        if 'CALL' in msg:
            return self._parse_station_call(msg) # return list of tuple


        #TODO Parse GO
        if 'GO' in msg:
            return self._parse_station_go(msg) # return list of tuple


        #TODO Parse ROVERCROSS
        #TODO Parse SLOWDOWN
        if 'SLOWDOWN' in msg:
            return self._parse_station_slowdown(msg)
        #TODO Parse STOP
        if 'STOP' in msg:
            return self._parse_station_stop(msg) 
        #TODO Emergency STOP
        #TODO RESTART


    def _parse_station_call(self, msg):
        called_station = msg[1]
        self.callq.put(positions[called_station])
        msg_destination_station = "|".join(msg[:2])
        msg_call_ack = 'CALL|ACK'
        msg_priority = Msgpriority.ACK
        return [(msg_priority,msg_destination_station,msg_call_ack)]
    
    def _parse_station_go(self, msg):
        msg_destination_station = "|".join(msg[:2])
        msg_go_ack = 'GO|ACK'
        msg_priority = Msgpriority.ACK
        return [(4,self.ROVER,'FORWARD'),(msg_priority,msg_destination_station,msg_go_ack)]
    
    def _parse_station_slowdown(self,msg):
        to_station = (Msgpriority.ACK,"|".join(msg[:2],'SLOWDOWN|ACK'))
        to_rover = (Msgpriority.SLOWDOWN,self.ROVER,'SLOWDOWN')
        return[to_rover,to_station]
         
    def _parse_station_stop(self,msg):
        msg_destination_station = "|".join(msg[:2])
        msg_ack = 'STOP|ACK'
        msg_priority = Msgpriority.ACK
        to_station = (msg_priority,msg_destination_station,msg_ack)
        to_rover = (Msgpriority.STOP,self.ROVER,'STOP')
        return[to_rover,to_station]



    
    def parse_rover(self,msg:list):
        #TODO ACKS
        #TODO Updates
        pass
    def parse_junction(self,msg:list):
        #TODO UPDATES
        #TODO SLOWDOWN
        #TODO STOP
        #TODO ROTATION|DONE
        pass
    
    def parse_hmi(self,msg:list):
        #TODO CALL
        #TODO GO
        #TODO E_STOP
        #TODO RESTART
        #TODO UPDATES

        pass




