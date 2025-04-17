import asyncio
import heating_logic
import common_pins

advertise_state_callback = None

class Mode:
    POWER = "power"
    AUTO = "auto"
    LIGHT = "light"

def _set_power(state):
    if state:
        heating_logic.set_power(True)
        advertise_state(Mode.POWER.upper(), 1)
        advertise_state(Mode.AUTO.upper(), 1)
        advertise_state(Mode.LIGHT.upper(), 1)
    else:
        heating_logic.set_power(False)
        advertise_state(Mode.POWER.upper(), 0)
        advertise_state(Mode.AUTO.upper(), 0)
        advertise_state(Mode.LIGHT.upper(), 0)

def set_power(state):
    if state == 1:
        if heating_logic.is_power_on():
            print("ERROR: heating already in progress")
        else:
            _set_power(1)
    else:
        if heating_logic.is_power_on():
            _set_power(0)

def _set_auto(state):
    if state:
        heating_logic.set_auto_mode(True)
        advertise_state(Mode.AUTO.upper(), 1)
    else:
        heating_logic.set_auto_mode(False)
        advertise_state(Mode.AUTO.upper(), 0)

def set_auto(state):
    if heating_logic.is_power_on():
        if state == 1:
            if heating_logic.is_auto_mode():
                print("ERROR: auto mode already on")
            else:
                _set_auto(1)
        else:
            if heating_logic.is_auto_mode():
                _set_auto(0)

def set_light(state):
    if state:
        heating_logic.set_light(True)
        advertise_state(Mode.LIGHT.upper(), 1)
    else:
        heating_logic.set_light(False)
        advertise_state(Mode.LIGHT.upper(), 0)

def register_advertise_state_callback(callback):
    global advertise_state_callback
    advertise_state_callback = callback

def advertise_state(mode, state):
    if advertise_state_callback is not None:
        advertise_state_callback(mode, str(state))

def handle_request(thing):
    if thing.data == "request":
        state = None
        if state is not None:
            thing.data = state
            thing.dirty_out = True

def on_data_received(thing):
    handle_request(thing)

    if thing.path == Mode.POWER:
        if thing.data == "1":
            set_power(1)
        elif thing.data == "0":
            set_power(0)
    elif thing.path == Mode.AUTO:
        if thing.data == "1":
            set_auto(1)
        elif thing.data == "0":
            set_auto(0)
    elif thing.path == Mode.LIGHT:
        if thing.data == "1":
            set_light(1)
        elif thing.data == "0":
            set_light(0)

def handle_buttons(thing):
    if thing.alias == common_pins.PWR_BTN.name:
        if heating_logic.is_power_on():
            set_power(0)
        else:
            set_power(1)
    elif thing.alias == common_pins.AUTO_BTN.name:
        if heating_logic.is_auto_mode():
            set_auto(0)
        else:
            set_auto(1)
    elif thing.alias == common_pins.HEATER_1_BTN.name:
        if heating_logic.is_power_on() and not heating_logic.is_auto_mode():
            if heating_logic.get_heater_count() == 1:
                heating_logic.set_random_heaters(0)
            else:
                heating_logic.set_random_heaters(1)
    elif thing.alias == common_pins.HEATER_2_BTN.name:
        if heating_logic.is_power_on() and not heating_logic.is_auto_mode():
            if heating_logic.get_heater_count() == 2:
                heating_logic.set_random_heaters(0)
            else:
                heating_logic.set_random_heaters(2)
    elif thing.alias == common_pins.HEATER_3_BTN.name:
        if heating_logic.is_power_on() and not heating_logic.is_auto_mode():
            if heating_logic.get_heater_count() == 3:
                heating_logic.set_random_heaters(0)
            else:
                heating_logic.set_random_heaters(3)
        else:
            if heating_logic.is_light():
                heating_logic.set_light(False)
            else:
                heating_logic.set_light(True)


def init():
    print("[PHY]: init")

async def action():
    while True:
        await asyncio.sleep(0.1)
