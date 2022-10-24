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
    global_volume = "{:08b}".format(int(volume_norm))

mcp.GPIO_Init()
mcp.GPIO_1_OutputMode() # Clock
mcp.GPIO_2_OutputMode() # Master
mcp.GPIO_3_OutputMode() # Data

# Init all values to LOW
mcp.GPIO_0_Output(0)
mcp.GPIO_1_Output(0)
mcp.GPIO_3_Output(0)

with sd.Stream(callback=print_sound):
    try:
        while True:

            # Add parity bit at front; 1/HIGH if odd number of 1's => stb has even number of 1's
            parity = ("1" if global_volume.count("1") % 2 else "0")
            stb = parity + global_volume + ("1" if parity == "0" else "0") # Add inverted parity bit
            if len(stb) != 9: continue

            mcp.GPIO_1_Output(0) # Reset clock
            mcp.GPIO_2_Output(1) # Set master HIGH

            high = True # Start with a HIGH cycle for the clock because it was reset to LOW
            for char in stb:
                mcp.GPIO_3_Output(int(char)) # data HI/LO
                time.sleep(0.1)
                mcp.GPIO_1_Output(int(high)) # tick clock
                high = not high

            print(stb + " --- Volume:" + str(int(stb[1:-1], 2)))
            #print(stb)

            mcp.GPIO_2_Output(0) # Reset master to low

    except KeyboardInterrupt:
        print()
        print("Stop")
    #sd.sleep(10000)
