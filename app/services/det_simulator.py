import asyncio
import aiohttp
import json
from app.utils import generate_pattern, on_off_time
import logging
from app.services.simulation_state import set_simulation_status
from flask import flash

# Assuming bit group size is 8 (detectors 1-8, 9-16, etc.)
BIT_GROUP_SIZE = 8

# This will store the current state of each bit group and a lock for each group
bit_group_state = {}
bit_group_locks = {}

# Event to signal when to stop the simulation
stop_event = asyncio.Event()

total_requests = 0
successful_requests = 0
failed_requests = 0

def get_bit_group(detnumber):
    return (detnumber - 1) // BIT_GROUP_SIZE

async def update_bit_group_state(hostname, bit_group, detnumber, state):
    key = (hostname, bit_group)

    if key not in bit_group_state:
        bit_group_state[key] = 0
        bit_group_locks[key] = asyncio.Lock()
        print('if key not in bit_group_state')
    
    async with bit_group_locks[key]:
        if state:
            # Turn on the bit corresponding to detnumber
            bit_group_state[key] |= (1 << ((detnumber - 1) % BIT_GROUP_SIZE))
        else:
            # Turn off the bit corresponding to detnumber
            bit_group_state[key] &= ~(1 << ((detnumber - 1) % BIT_GROUP_SIZE))

def generate_masked_pattern(hostname, bit_group):
    key = (hostname, bit_group)
    base = bit_group + 1  # Bit group base (1-indexed for this example)
    return {base: bit_group_state[key]}

async def post_data(session, uri, data):
    global total_requests, successful_requests, failed_requests
    total_requests += 1 

    # print(f"Making POST request #{total_requests} to URI: {uri}")
    # print(f"Post Data: {data}")

    try:
        async with session.post(uri, json=data) as response:
            if response.status == 200:
                successful_requests += 1
                set_simulation_status(True, total_requests, successful_requests, failed_requests)
            else:
                failed_requests += 1
                set_simulation_status(True, total_requests, successful_requests, failed_requests)
            return await response.text()
    except aiohttp.ClientError as e:
        set_simulation_status(True, total_requests, successful_requests, failed_requests)
        failed_requests += 1
        print("Simulation is Inactive due to an error:", e)

async def run_detector(session, hostname, detector):
    detnumber = detector['detnumber']
    sequences = detector['sequences']  
    print(f'Running detector {detnumber} for device {hostname}')
    url = f"http://{hostname}/some_endpoint/{detnumber}"
    print(f"Posting to {url} for detector {detnumber}")
    bit_group = get_bit_group(detnumber)

    print(f'The bit group for the current detector {detnumber} is {bit_group}')

    uri = f"http://{hostname}/maxtime/api/mibs"

    while not stop_event.is_set():  # Continue until the stop event is set
        for sequence in sequences:
            volume = sequence['volume']
            occupancy = sequence['occupancy']
            frequency = sequence['frequency']
            cycles = sequence['cycles']
            duration = frequency * cycles

            percall_on_time, percall_off_time = on_off_time(volume, occupancy, frequency)
            print(f'Running sequence with volume: {volume}, occupancy: {occupancy}, frequency: {frequency}, duration: {duration}')

            # Run the sequence for the specified duration
            end_time = asyncio.get_event_loop().time() + duration
            while asyncio.get_event_loop().time() < end_time:
                if stop_event.is_set():
                    break

                # Turn the detector on
                await update_bit_group_state(hostname, bit_group, detnumber, True)
                pattern_on = generate_masked_pattern(hostname, bit_group)
                print(pattern_on)
                post_on = {'data': [{'name': f'vehicleDetectorControlGroupActuation', 'data': pattern_on}], 'noChangeLog': True, 'username': 'Admin'}
                await post_data(session, uri, post_on)

                await asyncio.sleep(percall_on_time)

                # Turn the detector off
                await update_bit_group_state(hostname, bit_group, detnumber, False)
                pattern_off = generate_masked_pattern(hostname, bit_group)
                post_off = {'data': [{'name': f'vehicleDetectorControlGroupActuation', 'data': pattern_off}], 'noChangeLog': True, 'username': 'Admin'}
                await post_data(session, uri, post_off)

                await asyncio.sleep(percall_off_time)

            if stop_event.is_set():
                break

        # Loop back to the first sequence after all sequences are completed
        if not stop_event.is_set():
            print(f'Completed all sequences for detector {detnumber}. Looping back to the first sequence.')




async def print_request_stats(interval=10):
    while not stop_event.is_set():
        await asyncio.sleep(interval)  # Wait for the specified interval

async def run_simulation(config):
    global total_requests, successful_requests, failed_requests
    total_requests = 0
    successful_requests = 0
    failed_requests = 0
    try:
        stop_event.clear()  # Clear the stop event at the start of the simulation
        set_simulation_status(True, 0, 0, 0)
        async with aiohttp.ClientSession() as session:
            tasks = []
            tasks.append(asyncio.create_task(print_request_stats()))
            for device in config['devices']:
                hostname = device['hostname']
                for detector in device['detectors']:
                    print(f'Processing hostname: {hostname}, detector number: {detector["detnumber"]}')
                    task = run_detector(session, hostname, detector)
                    tasks.append(task)
            await asyncio.gather(*tasks)
            pass
    finally:
        set_simulation_status(False, total_requests, successful_requests, failed_requests)
        print(f"Total requests: {total_requests}")
        print(f"Successful requests: {successful_requests}")
        print(f"Failed requests: {failed_requests}")

def stop_simulation():
    stop_event.set()  # Set the stop event to signal all tasks to stop
