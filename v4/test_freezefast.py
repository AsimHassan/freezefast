from os import stat
from freezefast import *


#TODO Test Station CALLS
"""
test operation of station call function

11 stations + 1 store has call capability
I/P msg format : "STATION|number|CALL"A
STORE uses different identifier exclude from test
expected output: [(8,'STATION|number','CALL|ACK)]A
call queue should have all in correct order

"""
def test_call_station():

    obj = Freezefast()
    for stations in positions:
        retval = obj.parse_message(f"STATION|{stations}|CALL")
        assert retval == [(Msgpriority.ACK,f'STATION|{stations}','CALL|ACK')]
    for stations in positions:
        while not obj.callq.empty:
            assert positions[stations] == obj.callq.get()


#TODO Test Station Go
"""
Test GO messages from the stations
all positions have go capability
messages from store are parsed differently
I/P msg format : "STATION|number|GO"
should give direction from current position to junction
expected O/P :[(5,'ROVER|1',"FORWARD/REVERSE"),(8,'STATION|number','GO|ACK')]

"""
def test_go_station():
    obj = Freezefast()
    for stations in range(1,12):
        if stations == 5:
            continue
        if stations < 5 :
            direction = 'FORWARD'
        if stations > 5 :
            direction = 'REVERSE'
        obj.rover_position = stations 
        retval = obj.parse_message(f"STATION|{stations}|GO")
        assert retval == [(Msgpriority.GO,obj.ROVER,direction),(Msgpriority.ACK,f"STATION|{stations}","GO|ACK")]
        


#TODO Test STATION ROVERCROSS
"""
all stations can send rovercross message to see if rover is coming to stop at that station 
I/P msg format : "STATION|number|ROVERCROSS"
expected O/P :
    1. if the rover should stop: [(3,"ROVER|1","SLOWDOWN"),(3,"STATION|number","CROSS|YES")]
    2. if rover doesnt stop : [(8,"STATION|number","CROSS|NO")]

"""
def test_station_rovercross():
    obj = Freezefast()
    for station in range(1,12):
        if station == 5:
            continue
        obj.rover_destination = station
        retval = obj.parse_message(f"STATION|{station}|ROVERCROSS")
        assert retval == [(Msgpriority.SLOWDOWN,obj.ROVER,"SLOWDOWN"),(Msgpriority.SLOWDOWN,f"STATION|{station}","CROSS|YES")]
        obj.rover_destination = station+1
        retval = obj.parse_message(f"STATION|{station}|ROVERCROSS")
        assert retval == [(Msgpriority.ACK,f"STATION|{station}","CROSS|NO")]
        assert obj.rover_position == station



#TODO Test station stop
"""
I/P msg format : "STATION|number|STOP"
expected O/P : [(2,"ROVER|1","STOP),(8,"STATION|number","STOP|ACK)]


"""
def test_station_stop():
    obj = Freezefast()
    for station in range(1,12):
        if station == 5:
            continue
        retval = obj.parse_message(f"STATION|{station}|STOP")
        assert retval == [(Msgpriority.STOP,obj.ROVER,"STOP"),(Msgpriority.ACK,f"STATION|{station}","STOP|ACK")]

#TODO Test station emergency
"""
parse emergency stop from stations 

I/P msg format : "STATION|number|EMERGENCY"
o/P msg formta : [(Msgpriority.STOP,"ROVER|1","EMERGENCY|STOP")(Msgpriority.STOP,"HMI|1","EMERGENCY-STOP"),(Msgpriority.STOP,"STATION|number","EMERGENCY-ACK")]
"""
#TODO Test rover ACK
#TODO Test rover state update
#TODO Test junction roverhere
#TODO Test junction slowdonwn
#TODO Test junction stop
#TODO Test juncion done
#TODO Test HMI CALL
#TODO Test HMI GO
#TODO Test HMI EMERGENCY
#TODO Test HMI RESTART
#TODO Test HMI UPDATE