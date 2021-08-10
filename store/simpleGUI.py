#! /home/asim/projects/RoverProject/.venv/bin/python
import PySimpleGUI as sg

"""


buttons looks okay, need to find a way to incorporate this into existing system
call button can reflect actual state ie 
before clicking : call
on click: calling 
on ack : Called
on rover reaching : GO
on GO: call


stations too can show some color to signfy its state
rover movement maybe shown  throuh colors

"""
CALL_state = 'CALL'
sg.theme('BluePurple')
_size1 = (11,2)
_size = (7,4)
layout = [[sg.Button('CALL',size=_size1,key='-CALL-',pad=(5,5)),sg.Button('E-STOP',size=_size1),sg.Button('Restart',size=_size1)],
          [sg.Button('1',size=_size),sg.Button('2',size=_size),sg.Button('3',size=_size),sg.Button('4',size=_size)],
          [sg.Button('5',size=_size),sg.Button('6',size=_size),sg.Button('7',size=_size),sg.Button('8',size=_size),],
          [sg.Button('9',size=_size),sg.Button('10',size=_size),sg.Button('11',size=_size),sg.Button('12',size=_size)]]

window = sg.Window('Pattern 2B', layout)

station_selected = 0

while True:  # Event Loop
    event, values = window.read()
    print(event, values)
    if event in [sg.WIN_CLOSED, 'Exit']:
        break
    if event == '-CALL-':
        # Update the "output" text element to be the value of "input" element
        print(f"CALL presses : state{CALL_state}")
        if CALL_state == 'CALL':
            # Do stuff
            #send call message
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
                CALL_state ='CALL'
                window['-CALL-'].update(CALL_state,button_color='blue')
                station_selected = 0
    for btn in range(1,13):
        if event ==f"{btn}":
            station_selected = event
            window[f'{btn}'].update(button_color='white')
            print(f"{btn}: has been pressed")
        else :
            window[f'{btn}'].update(button_color='blue')


window.close()
