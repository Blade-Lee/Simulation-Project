import GlobalVar
import json
import sys, os
import math
import random


'''
    default option: half the size each time proceeding to the next layer

    length:     seconds
    size:       Byte
'''

def divide_video():
    load_file_path = os.path.join(sys.path[0], "..\data\Video_data")
    store_file_path = os.path.join(sys.path[0], "..\data\Quality_Video_data")

    raw_len = []

    with open(load_file_path, "r") as read_data:
        for line in read_data.readlines():
            raw_len.append(float(line.strip()))

    raw_size = [GlobalVar.BIT_RATE * length / 8 for length in raw_len]

    quality_size = []

    for item in raw_size:
        quality_check = math.log(item, 4)
        temp_store = []
        if quality_check >= GlobalVar.K:
            temp_size = item
            for index in range(0, GlobalVar.K):
                temp_size = int(temp_size/4) + int(temp_size % 4)

                disturbance = random.randint(temp_size/10, temp_size/5)
                if random.randint(0, 1) == 1:
                    temp_size += disturbance
                else:
                    temp_size -= disturbance

                temp_store.append(temp_size)
        if len(temp_store) > 0:
            quality_size.append(temp_store)

    with open(store_file_path, "w") as write_data:
        write_data.write(json.dumps(quality_size))
    
