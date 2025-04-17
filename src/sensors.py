import asyncio
import common
import common_pins
import struct
import machine, onewire, ds18x20

environment_sensors = []
realtime_sensors = []
on_state_change_cb = None

alias = {
    "28a42f54000000df": "temp_direct",
#    "28bb3749f6c73cdc": "temp_indirect",
#    "28bb3749f6c73cdc": "temp_outside",
}

class DsTempReader:
    def __init__(self, ds_pin, alias):
        self.ds_pin = ds_pin
        self.alias = alias
        self.ds_sensor = ds18x20.DS18X20(onewire.OneWire(machine.Pin(self.ds_pin)))
        self.dirty = False
        self.data = {}
        self.error_msg = None
        self.timestamp = None
        self.timeout = 10 * 1000

    def get_name(self, rom):
        return ''.join(struct.pack('B', x).hex() for x in rom)

    async def action(self):
        try:
            roms = self.ds_sensor.scan()
            self.ds_sensor.convert_temp()
            await asyncio.sleep_ms(750)
            for rom in roms:
                name = self.get_name(rom)
                temp = self.ds_sensor.read_temp(rom)
                self.data[alias.get(name, name)] = temp
                self.dirty = True
        except Exception as e:
            print("[SENSORS]: ERROR @ %s read with %s" % (self.alias, e))
            self.error_msg = e

    def get_temperature(self):
        return self.data

def register_on_state_change_callback(cb):
    global on_state_change_cb
    print("[SENSORS]: register on state change cb")
    on_state_change_cb = cb

def init():
    print("[SENSORS]: init")
    global environment_sensors, realtime_sensors
    environment_sensors.append(DsTempReader(common_pins.ONEWIRE.id, alias="DSTEMP"))

async def environment_sensors_action():
    print("[SENSORS]: environment_sensors_action")
    while True:
        for sensor in environment_sensors:
            if sensor.timestamp is None or common.millis_passed(sensor.timestamp) >= sensor.timeout:
                sensor.timestamp = common.get_millis()
                await sensor.action()
                if sensor.dirty:
                    sensor.dirty = False
                    if on_state_change_cb is not None:
                        if sensor.alias == "DSTEMP":
                            for sensor_name in sensor.data.items():
                                if sensor_name in alias.items():
                                    on_state_change_cb("temp_direct", sensor.data.get("temp_direct"))
                                    on_state_change_cb("temp_indirect", sensor.data.get("temp_indirect"))
                                    on_state_change_cb("temp_outside", sensor.data.get("temp_outside"))
                                else:
                                    on_state_change_cb(sensor.alias, sensor.data)
                        else:
                            on_state_change_cb(sensor.alias, sensor.data)

            if sensor.error_msg is not None:
                if on_state_change_cb is not None:
                    on_state_change_cb(f"{sensor.alias}_ERROR", sensor.error_msg)
                sensor.error_msg = None
            await asyncio.sleep_ms(0)

async def realtime_sensors_action():
    print("[SENSORS]: realtime_sensors_action")
    while True:
        for sensor in realtime_sensors:
            sensor.action()
            if sensor.dirty:
                sensor.dirty = False
                if on_state_change_cb is not None:
                    on_state_change_cb(sensor.alias, sensor.data)
        await asyncio.sleep_ms(0)

def on_data_request(thing):
    print("[SENSORS]: on_data_request[%s][%s]" % (thing.alias, thing.data))
    for sensor in environment_sensors:
        if sensor.alias == thing.alias:
            if thing.data == "request":
                print(f"[SENSORS]: request {sensor.alias} data")
                sensor.timestamp = None
            elif "timeout" in thing.data:
                try:
                    sensor.timeout = int(thing.data.split(" ")[1])
                except Exception as e:
                    print("[SENSORS]: Error: timeout with %s" % (e))

def test_print(alias, data):
    print("[SENSORS]: CB -- alias[%s], data[%s]" % (alias, data))

async def test_add_tasks():
    print("[SENSORS]: test_add_tasks")
    tasks = []
    tasks.append(asyncio.create_task(realtime_sensors_action()))
    tasks.append(asyncio.create_task(environment_sensors_action()))
    for task in tasks:
        await task
        print("[SENSORS]: Error: loop task finished!")

def test_start():
    print("[SENSORS]: test_start")
    init()
    register_on_state_change_callback(test_print)
    asyncio.run(test_add_tasks())
