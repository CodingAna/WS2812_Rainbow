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
    # TODO: Make this at least 9bit because the volume gets above 255. Maybe even 10bit? == 12bit in total?
    global_volume = "{:010b}".format(int(volume_norm))

mcp.GPIO_Init()
mcp.GPIO_1_OutputMode() # Clock
mcp.GPIO_2_OutputMode() # Master
mcp.GPIO_3_OutputMode() # Data

# Init all values to LOW
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

            # Add parity bit at front; 1/HIGH if odd number of 1's => stb has even number of 1's
            # parity = ("1" if global_volume.count("1") % 2 else "0")
            # stb = parity + global_volume + ("1" if parity == "0" else "0") # Add inverted parity bit
            if len(global_volume) != 10: continue

            parity_0 = "1" if global_volume[:5].count("1") % 2 else "0"
            parity_1 = "1" if global_volume[5:].count("1") % 2 else "0"
            stb = parity_0 + global_volume + parity_1

            mcp.GPIO_1_Output(0) # Reset clock
            sleep_for_us(1000)
            mcp.GPIO_2_Output(1) # Set master HIGH

            high = True # Start with a HIGH cycle for the clock because it was reset to LOW
            for char in stb: # sleep for a total of 2*15*10=300ms
                sleep_for_us(15000) # 15ms
                mcp.GPIO_3_Output(int(char)) # data HI/LO
                sleep_for_us(15000) # 15ms
                mcp.GPIO_1_Output(int(high)) # tick clock
                high = not high

            print(parity_0 + " " + global_volume + " " + parity_1 + " --- Volume:" + str(int(stb[1:-1], 2)))

            sleep_for_us(10000) # 10ms
            # total sleep time = 311ms
            mcp.GPIO_2_Output(0) # Reset master to low

    except KeyboardInterrupt: 
        print()
        print("Stop")
    #sd.sleep(10000)
