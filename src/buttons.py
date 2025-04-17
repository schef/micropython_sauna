from machine import Pin
import common_pins

on_state_change_cb = None
buttons = []
button_pins = [
    common_pins.HEATER_3_BTN,
    common_pins.HEATER_2_BTN,
    common_pins.HEATER_1_BTN,
    common_pins.AUTO_BTN,
    common_pins.PWR_BTN
               ]

class Button:
    def __init__(self, pin, active_high = False):
        self.input = Pin(pin.id, Pin.IN, Pin.PULL_UP)
        self.name = pin.name
        self.state = None
        self.active_high = active_high

    def check(self):
        state = self.input.value()
        if self.active_high:
            state = int(not state)
        if state != self.state:
            self.state = state
            print("[BUTTONS]: %s -> %d" % (self.name, self.state))
            if on_state_change_cb is not None:
                on_state_change_cb(self.name, self.state)

def register_on_state_change_callback(cb):
    print("[BUTTONS]: register on state change cb")
    global on_state_change_cb
    on_state_change_cb = cb

def init():
    print("[BUTTONS]: init")
    for pin in button_pins:
        buttons.append(Button(pin, active_high = True))

def action():
    for button in buttons:
        button.check()

def test():
    print("[BUTTONS]: test")
    init()
    while True:
        action()
