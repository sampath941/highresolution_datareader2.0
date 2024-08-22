import asyncio
import aiohttp
import json
from app.utils import generate_pattern, on_off_time
import logging

# Assuming bit group size is 8 (detectors 1-8, 9-16, etc.)
BIT_GROUP_SIZE = 8

# This will store the current state of each bit group and a lock for each group
bit_group_state = {}
bit_group_locks = {}

# Event to signal when to stop the simulation
stop_event = asyncio.Event()

def get_bit_group(detnumber):
    return (detnumber - 1) // BIT_GROUP_SIZE

async def update_bit_group_state(bit_group, detnumber, state):
    if bit_group not in bit_group_state:
        bit_group_state[bit_group] = 0
        bit_group_locks[bit_group] = asyncio.Lock()
        print('if bit_group not in bit_group_state')
    
    async with bit_group_locks[bit_group]:
        if state:
            # Turn on the bit corresponding to detnumber
            bit_group_state[bit_group] |= (1 << ((detnumber - 1) % BIT_GROUP_SIZE))
        else:
            # Turn off the bit corresponding to detnumber
            bit_group_state[bit_group] &= ~(1 << ((detnumber - 1) % BIT_GROUP_SIZE))

def generate_masked_pattern(bit_group):
    base = bit_group + 1  # Bit group base (1-indexed for this example)
    return {base: bit_group_state[bit_group]}

async def post_data(session, uri, data):
    async with session.post(uri, json=data) as response:
        return await response.text()

async def run_detector(session, hostname, detector):
    detnumber = detector['detnumber']
    volume = detector['volume']
    occupancy = detector['occupancy']
    frequency = detector['frequency']

    bit_group = get_bit_group(detnumber)
    print('The bit group for the current detector is', bit_group)
    percall_on_time, percall_off_time = on_off_time(volume, occupancy, frequency)
    print('This is for detector Number', detnumber)
    print('Here is the per_call_ontime', percall_on_time)
    print('Here is the per_call_offtime', percall_off_time)

    # Construct the URI for this detector
    uri = f"http://{hostname}/maxtime/api/mibs"

    while not stop_event.is_set():  # Continue until the stop event is set
        # Turn the detector on
        await update_bit_group_state(bit_group, detnumber, True)
        pattern_on = generate_masked_pattern(bit_group)
        post_on = {'data': [{'name': f'inputPointGroupControl-1', 'data': pattern_on}], 'noChangeLog': True, 'username': 'Admin'}
        await post_data(session, uri, post_on)

        await asyncio.sleep(percall_on_time)

        # Turn the detector off
        await update_bit_group_state(bit_group, detnumber, False)
        pattern_off = generate_masked_pattern(bit_group)
        post_off = {'data': [{'name': f'inputPointGroupControl-1', 'data': pattern_off}], 'noChangeLog': True, 'username': 'Admin'}
        await post_data(session, uri, post_off)

        await asyncio.sleep(percall_off_time)

async def run_simulation(config):
    stop_event.clear()  # Clear the stop event at the start of the simulation
    async with aiohttp.ClientSession() as session:
        tasks = []
        for device in config['devices']:
            hostname = device['hostname']
            for detector in device['detectors']:
                task = run_detector(session, hostname, detector)
                tasks.append(task)
        await asyncio.gather(*tasks)

def stop_simulation():
    stop_event.set()  # Set the stop event to signal all tasks to stop

