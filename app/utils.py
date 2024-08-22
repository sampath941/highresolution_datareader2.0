import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


import math

def generate_pattern(detnumber):
    if detnumber < 1:
        raise ValueError("detNumber must be greater than or equal to 1.")
    
    base = 1
    power = 1
    
    if detnumber <= 8:
        base = 1
        power = 2 ** (detnumber - 1)
    else:
        base = (detnumber - 1) // 8 + 1
        power_index = (detnumber - 1) % 8
        power = 2 ** power_index
    
    return {base: power}

def on_off_time(vol, occ, freq):
    total_det_on_time = (occ / 100) * freq
    percall_on_time = total_det_on_time / vol
    total_det_off_time = freq - total_det_on_time
    percall_off_time = total_det_off_time / vol
    return percall_on_time, percall_off_time
