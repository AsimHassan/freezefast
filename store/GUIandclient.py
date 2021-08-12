#! /home/asim/projects/RoverProject/.venv/bin/python

import asyncio
from tkinter.constants import FALSE
import PySimpleGUI as sg
from PySimpleGUI.PySimpleGUI import button_color_to_tuple

sg.theme('BluePurple')
_size1 = (31,7)
_size = (22,7)
layout = [[sg.Button('CALL',size=_size1,key='-CALL-',pad=(5,5)),sg.Button('E-STOP',size=_size1,key = '-ESTOP-'),sg.Button('Restart',size=_size1,key='-RESTART-')],
          [sg.Button('1',size=_size),sg.Button('2',size=_size),sg.Button('3',size=_size),sg.Button('4',size=_size)],
          [sg.Button('5',size=_size),sg.Button('6',size=_size),sg.Button('7',size=_size),sg.Button('8',size=_size),],
          [sg.Button('9',size=_size),sg.Button('10',size=_size),sg.Button('11',size=_size),sg.Button('12',size=_size)],
          [sg.Text('I should be updated when a messge comes in',key='-text_bottom-')]]

window = sg.Window('HMI test', layout = layout,location = (800,100),size=(800,480),no_titlebar=True,element_justification='center',keep_on_top=False)

EMERGENCY_STATE = False

def restart_triggered(writer):
    global EMERGENCY_STATE
    writer.write('HMI|1|RESTART'.encode())
    window['-ESTOP-'].update(button_color=('#ffffff','#303952'))
    EMERGENCY_STATE = False

def estop_triggered(writer):
    global EMERGENCY_STATE
    print("Estop- Pressed")
    writer.write("HMI|1|EMERGENCY".encode())
    window['-ESTOP-'].update(button_color='red')
    EMERGENCY_STATE = True

def sendGo(writer,station_selected,CALL_state):
    print(f"set the destination as : {station_selected}")
    writer.write(f"HMI|1|GO|{station_selected}.".encode())
    window['-CALL-'].update(CALL_state,button_color=('#ffffff','#303952'))

def sendCall(writer,CALL_state):
    writer.write("HMI|CALL.".encode())
    window['-CALL-'].update(CALL_state,button_color='green')



async def HMI_loop():
    CALL_state = 'CALL'
    station_selected = 0
    try:
        reader,writer = await asyncio.open_connection('192.168.3.64',1234)
        writer.write("HMI|1|ON.".encode())
        await writer.drain()
        while True:


            event,values = window.read(timeout=50)
            try:
                msgin = await asyncio.wait_for(reader.read(32),0.1)
            except asyncio.TimeoutError:
                msgin = ""

            if event in [sg.WIN_CLOSED, 'Exit']:
                break
            if len(msgin) > 0:
                print(msgin.decode())
                window['-text_bottom-'].update(msgin.decode())
            if event == '-CALL-':
                # Update the "output" text element to be the value of "input" element
                print(f"CALL presses : state{CALL_state}")
                if CALL_state == 'CALL':
                    # Do stuff
                    #send call message
                    sendCall(writer,CALL_state) 
                    CALL_state ='GO'
                    station_selected = 0

                elif CALL_state == 'GO':
                    # Do stuff
                    # check which station has been highlighted
                    # Send Go message
                    if station_selected == 0:
                        sg.popup("No station selected")
                    else:
                        sendGo(writer,station_selected,CALL_state)
                        CALL_state ='CALL'
                        station_selected = 0

            if event == '-ESTOP-':
                estop_triggered(writer)

            if event == '-RESTART-':
                print("Restart Pressed")
                if EMERGENCY_STATE:
                    restart_triggered(writer)
            for btn in range(1,13):
                if event ==str(btn):
                    station_selected = event
                    print(f"{btn}: has been pressed")
            if station_selected !=0:
                window[station_selected].update(button_color='white')
            else:
                for btn in range(1,13):
                    window[f'{btn}'].update(button_color='blue')

    except KeyboardInterrupt:
        #writer.close()
        print("exiting....")
    except:
        raise



try:
    asyncio.run(HMI_loop())
except KeyboardInterrupt:
    print("....")
except:
    raise


