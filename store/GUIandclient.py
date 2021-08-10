#! /home/asim/projects/RoverProject/.venv/bin/python

import asyncio
import PySimpleGUI as sg

sg.theme('BluePurple')
_size1 = (11,2)
_size = (7,4)
layout = [[sg.Button('CALL',size=_size1,key='-CALL-',pad=(5,5)),sg.Button('E-STOP',size=_size1),sg.Button('Restart',size=_size1)],
          [sg.Button('1',size=_size),sg.Button('2',size=_size),sg.Button('3',size=_size),sg.Button('4',size=_size)],
          [sg.Button('5',size=_size),sg.Button('6',size=_size),sg.Button('7',size=_size),sg.Button('8',size=_size),],
          [sg.Button('9',size=_size),sg.Button('10',size=_size),sg.Button('11',size=_size),sg.Button('12',size=_size)],
          [sg.Text('I should be updated when a messge comes in',key='-text_bottom-')]]

window = sg.Window('HHI test', layout)
async def HMI_loop():
    CALL_state = 'CALL'
    station_selected = 0
    try:
        reader,writer = await asyncio.open_connection('192.168.3.64',1234)
        writer.write("HMI|1|ON.".encode())
        await writer.drain()
        while True:


            event,values = window.read(timeout=100)
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
                    writer.write("STORE|CALL.".encode())
                    CALL_state ='GO'
                    window['-CALL-'].update(CALL_state,button_color='green')
                    station_selected = 0

                elif CALL_state == 'GO':
                    # Do stuff
                    # check which station has been highlighted
                    # Send Go message
                    if station_selected == 0:
                        sg.popup("No station selected")
                    else:
                        print(f"set the destination as : {station_selected}")
                        writer.write(f"HMI|GO|{station_selected}.".encode())
                        CALL_state ='CALL'
                        window['-CALL-'].update(CALL_state,button_color='blue')
                        station_selected = 0
            for btn in range(1,13):
                if event ==f"{btn}":
                    station_selected = event
                    print(f"{btn}: has been pressed")
            if station_selected !=0:
                window[station_selected].update(button_color='white')
            else:
                for btn in range(1,13):
                    window[f'{btn}'].update(button_color='blue')
                    #if event != sg.TIMEOUT_EVENT:
                        #msg = str(event)
                        #writer.write(msg.encode("utf8"))
                        #await writer.drain()
                    #print(event,values)
                    #print(msgin)
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


