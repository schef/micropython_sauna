import asyncio
import time
import common
import common_pins

relays = []
leds = []

relay_pins = [
    common_pins.LIGHT,
    common_pins.HEATER_1,
    common_pins.HEATER_2,
    common_pins.HEATER_3
]

led_pins = [
    common_pins.HEATER_3_LED,
    common_pins.HEATER_2_LED,
    common_pins.HEATER_1_LED,
    common_pins.AUTO_LED,
    common_pins.PWR_LED
]

class Led:
    def __init__(self, id, name, active_high=False):
        self.output = common.create_output(id)
        self.active_high = active_high
        self.state = None
        self.set_state(0)
        self.name = name

    def set_state(self, state):
        if advertise_state_callback is not None:
            advertise_state_callback(self.name, state)
        if self.active_high:
            if state:
                self.output.off()
            else:
                self.output.on()
        else:
            if state:
                self.output.on()
            else:
                self.output.off()
        self.state = state

    def get_state(self):
        return self.state

advertise_state_callback = None

def register_advertise_state_callback(callback):
    global advertise_state_callback
    advertise_state_callback = callback

def set_state_by_name(name, state):
    print("[LEDS]: set_state_by_name(%s, %s)" % (name, state))
    for relay in relays:
        if relay.name == name:
            relay.set_state(state)
    for led in leds:
        if led.name == name:
            led.set_state(state)

def get_state_by_name(name):
    for relay in relays:
        if relay.name == name:
            return relay.state
    for led in leds:
        if led.name == name:
            return led.state
    return None

def get_led_by_name(name):
    for relay in relays:
        if relay.name == name:
            return relay
    for led in leds:
        if led.name == name:
            return led
    return None

def on_relay_direct(thing):
    state = int(thing.data) if thing.data in ("0", "1", 0, 1) else None
    if state is not None:
        led = get_led_by_name(thing.alias)
        if led is not None:
            if led.state != state:
                led.set_state(state)
    if thing.data == "request":
        state = get_state_by_name(thing.alias)
        print(thing.alias, thing.data)
        if state is not None:
            thing.data = state
            thing.dirty_out = True

def test_relays():
    global relays
    relays = []
    init_relays()
    for relay in relays:
        print("[LEDS]: testing %s" % (relay.name))
        relay.set_state(1)
        time.sleep_ms(1000)
        relay.set_state(0)
        time.sleep_ms(1000)

def test_leds():
    global leds
    leds = []
    init_leds()
    for led in leds:
        print("[LEDS]: testing %s" % (led.name))
        led.set_state(1)
        time.sleep_ms(1000)
        led.set_state(0)
        time.sleep_ms(1000)

def init_relays():
    for pin in relay_pins:
        relays.append(Led(pin.id, pin.name, active_high = True))

def init_leds():
    for pin in led_pins:
        leds.append(Led(pin.id, pin.name, active_high = False))

def force_advertise_states():
    if advertise_state_callback is not None:
        for led in leds:
            advertise_state_callback(led.name, led.get_state())
        for relay in relays:
            advertise_state_callback(relay.name, relay.get_state())

def init():
    print("[LEDS]: init")
    init_relays()
    init_leds()
    action()

def action():
    pass

def test():
    print("[LEDS]: test")
    init()
    while True:
        action()

def test_async():
    print("[LEDS]: test_async")
    init()
    asyncio.run(common.loop_async("LEDS", action))
