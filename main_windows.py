from PyMCP2221A import PyMCP2221A
import time
import sounddevice as sd
import numpy as np

mcp = PyMCP2221A.PyMCP2221A()
mcp.Reset()
mcp = PyMCP2221A.PyMCP2221A()

global_volume = ""

def print_sound(indata, outdata, frames, time, status):
    global global_volume

    volume_norm = np.linalg.norm(indata)*10
    global_volume = "{:010b}".format(int(volume_norm))

mcp.GPIO_Init()
mcp.GPIO_1_OutputMode() # Clock
mcp.GPIO_2_OutputMode() # Master
mcp.GPIO_3_OutputMode() # Data

# Init all ports to LOW
mcp.GPIO_1_Output(0)
mcp.GPIO_2_Output(0)
mcp.GPIO_3_Output(0)


def sleep_for_us(us: int):
    start = time.time_ns()
    while time.time_ns() - start < us*1000:
        pass

sleep_for_us(1000*1000)

with sd.Stream(callback=print_sound):
    try:
        while True:
            if len(global_volume) != 10: continue

            # Parity: Must have even number of 1's in first (:5) and second half (5:), parity bits are 0 if even, else 1 to make even number
            parity_0 = "1" if global_volume[:5].count("1") % 2 else "0"
            parity_1 = "1" if global_volume[5:].count("1") % 2 else "0"
            stb = parity_0 + global_volume + parity_1

            mcp.GPIO_1_Output(0) # Reset clock
            sleep_for_us(1000) # Wait 1ms just for safety
            mcp.GPIO_2_Output(1) # Set master HIGH

            high = True # Start with a HIGH cycle for the clock because it was reset to LOW
            for char in stb: # 12x cycles
                sleep_for_us(15000) # 15ms
                mcp.GPIO_3_Output(int(char)) # data
                sleep_for_us(15000) # 15ms
                mcp.GPIO_1_Output(int(high)) # clock
                high = not high

            print(stb[0] + "-" + stb[1:-1] + "-" + stb[-1] + " --- Volume:" + str(int(stb[1:-1], 2)))

            sleep_for_us(10000) # 10ms
            # total sleep time = (1+12*30+10)ms = 371ms
            mcp.GPIO_2_Output(0) # Reset master to low

    except KeyboardInterrupt: 
        print()
        print("Stop")
