import asyncio
import common
import buttons
import leds
import phy_interface
import sensors
import heating_logic
import wlan
import mqtt
import heartbeat
import things
import version

async def process_time_measure(timeout=20):
    print("[RUNNER]: start process_time_measure")
    timestamp = common.get_millis()
    bigest = 0
    while True:
        await asyncio.sleep(0)
        timepassed = common.millis_passed(timestamp)
        if timepassed >= timeout:
            if timepassed > bigest:
                bigest = timepassed
            print("[RUNNER]: timeout warning %d ms with bigest %d" % (timepassed, bigest))
        timestamp = common.get_millis()

def send_on_boot():
    print("[RUNNER]: send_on_boot")
    t = things.get_thing_from_path("version")
    t.data = version.VERSION
    t.dirty_out = True

def init():
    print("[RUNNER]: init")

    buttons.init()
    buttons.action()
    leds.init()
    phy_interface.init()
    sensors.init()
    heating_logic.init()
    wlan.init()
    mqtt.init()
    things.init()
    leds.force_advertise_states()
    send_on_boot()

async def main():
    init()
    tasks = []
    tasks.append(asyncio.create_task(common.loop_async("BUTTONS", buttons.action)))
    tasks.append(asyncio.create_task(common.loop_async("LEDS", leds.action)))
    tasks.append(asyncio.create_task(phy_interface.action()))
    tasks.append(asyncio.create_task(sensors.realtime_sensors_action()))
    tasks.append(asyncio.create_task(sensors.environment_sensors_action()))
    tasks.append(asyncio.create_task(heating_logic.loop()))
    tasks.append(asyncio.create_task(wlan.loop()))
    tasks.append(asyncio.create_task(mqtt.loop_async()))
    tasks.append(asyncio.create_task(heartbeat.action()))
    tasks.append(asyncio.create_task(things.loop_async()))
    tasks.append(asyncio.create_task(process_time_measure()))
    for task in tasks:
        await task
    print("[RUNNER]: Error: loop task finished!")

def run():
    asyncio.run(main())
