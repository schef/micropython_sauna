import asyncio
import random
import common_pins
import leds
import sensors
from common import get_millis, millis_passed

power_on_status = False
auto_mode_status = False
manual_mode_timestamp = 0
manual_mode_timeout = 15 * 60 * 1000
temperature_offset = 15.0
heater_count = 0

def init():
    print("[HL]: init")
    set_power(False)

def set_power(state):
    print(f"[HL]: set_power: {state}")
    global power_on_status
    power_on_status = state
    if state:
        leds.set_state_by_name(common_pins.PWR_LED.name, 1)
        set_light(True)
        set_auto_mode(True)
    else:
        leds.set_state_by_name(common_pins.PWR_LED.name, 0)
        set_light(False)
        set_auto_mode(False)
        set_random_heaters(0)

def is_power_on():
    return power_on_status

def get_temperature():
    temp_direct = sensors.environment_sensors[0].get_temperature()
    #TODO: set temp
    return None
    if temp_direct is not None:
        if temp_direct >= 130.0:
            return None
        if temp_direct <= -15.0:
            return None
    return temp_direct

def set_auto_mode(state):
    global auto_mode_status, manual_mode_timestamp
    auto_mode_status = state
    if state:
        manual_mode_timestamp = 0
        leds.set_state_by_name(common_pins.AUTO_LED.name, 1)
    else:
        manual_mode_timestamp = get_millis()
        leds.set_state_by_name(common_pins.AUTO_LED.name, 0)
        set_random_heaters(0)

def is_auto_mode():
    return auto_mode_status

def set_heater(index, state):
    if index == 1:
        if state:
            leds.set_state_by_name(common_pins.HEATER_1_LED.name, 1)
            leds.set_state_by_name(common_pins.HEATER_1.name, 1)
        else:
            leds.set_state_by_name(common_pins.HEATER_1_LED.name, 0)
            leds.set_state_by_name(common_pins.HEATER_1.name, 0)
    elif index == 2:
        if state:
            leds.set_state_by_name(common_pins.HEATER_2_LED.name, 1)
            leds.set_state_by_name(common_pins.HEATER_2.name, 1)
        else:
            leds.set_state_by_name(common_pins.HEATER_2_LED.name, 0)
            leds.set_state_by_name(common_pins.HEATER_2.name, 0)
    elif index == 3:
        if state:
            leds.set_state_by_name(common_pins.HEATER_3_LED.name, 1)
            leds.set_state_by_name(common_pins.HEATER_3.name, 1)
        else:
            leds.set_state_by_name(common_pins.HEATER_3_LED.name, 0)
            leds.set_state_by_name(common_pins.HEATER_3.name, 0)

def set_random_heaters(count):
    global heater_count
    if heater_count != count:
        heater_count = count
        heaters = [1, 2, 3]

        heater_copy = heaters[:]
        random_heaters = []
        for _ in range(count):
            idx = random.randint(0, len(heater_copy) - 1)
            random_heaters.append(heater_copy.pop(idx))

        for heater_index in heaters:
            if heater_index in random_heaters:
                set_heater(heater_index, True)
            else:
                set_heater(heater_index, False)

def get_heater_count():
    return heater_count

def set_light(status):
    if status:
        leds.set_state_by_name(common_pins.LIGHT.name, 1)
    else:
        leds.set_state_by_name(common_pins.LIGHT.name, 0)

def is_light():
    return leds.get_state_by_name(common_pins.LIGHT.name)

async def loop():
    print("[HL]: loop")
    global start_timestamp
    while True:
        if is_power_on():
            if is_auto_mode():
                temperature = get_temperature()
                if temperature is not None:
                    if temperature <= 80.0 + temperature_offset:
                        set_random_heaters(3)
                    elif temperature > 80.0 + temperature_offset and temperature <= 90.0 + temperature_offset:
                        set_random_heaters(2)
                    elif temperature > 90.0 + temperature_offset and temperature <= 100.0 + temperature_offset:
                        set_random_heaters(1)
                    else:
                        set_random_heaters(0)
                else:
                    set_random_heaters(1)
            else:
                if millis_passed(manual_mode_timestamp) >= manual_mode_timeout:
                    set_auto_mode(False)
        await asyncio.sleep(1)
