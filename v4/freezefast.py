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

        if "STATION" in splitmsg:
            (destination,message) = self.parse_station(splitmsg[2:]) 

        if "ROVER" in splitmsg:
            pass
        if "JUNCTION" in splitmsg:
            pass
        if "HMI" in splitmsg:
            pass
        if "ROVER" in splitmsg:
            pass

    def parse_station(self,msg:list):
        pass