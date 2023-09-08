import sys
# import inputs_lib as inputs
import inputs


print(inputs.devices.all_devices)

pads = inputs.devices.gamepads





if len(pads) == 0:
    raise Exception("Couldn't find any Gamepads!")




while True:

    events = inputs.get_gamepad()

    for event in events:

        print('event.ev_type', event.ev_type)
        print('event.code', event.code)
        print('event.state', event.state)

        if event.code == 'BTN_SOUTH' and event.state == 1:

            print('Celebrate!')


