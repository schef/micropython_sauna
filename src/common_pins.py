class Pin:
    def __init__(self, id, name):
        self.id = id
        self.name = name

ONEWIRE = Pin(28, "ONEWIRE")

LIGHT = Pin(21, "LIGHT")
HEATER_1 = Pin(20, "HEATER_1")
HEATER_2 = Pin(19, "HEATER_2")
HEATER_3 = Pin(18, "HEATER_3")

HEATER_3_LED = Pin(2, "HEATER_3_LED")
HEATER_3_BTN = Pin(3, "HEATER_3_BTN")
HEATER_2_LED = Pin(4, "HEATER_2_LED")
HEATER_2_BTN = Pin(5, "HEATER_2_BTN")
HEATER_1_LED = Pin(6, "HEATER_1_LED")
HEATER_1_BTN = Pin(7, "HEATER_1_BTN")
AUTO_LED = Pin(8, "AUTO_LED")
AUTO_BTN = Pin(9, "AUTO_BTN")
PWR_LED = Pin(10, "PWR_LED")
PWR_BTN = Pin(11, "PWR_BTN")
