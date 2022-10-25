import machine, time

def hsl_to_rgb(h, s, l): # Hue, Saturation, Lightness
    c = (1 - abs((2 * l) - 1)) * s # Chroma
    hs = h / 60 # H'
    x = c * (1 - abs((hs % 2) - 1))
    r, g, b = (0, 0, 0)
    if hs >= 0 and hs < 1: r, g, b = (c, x, 0)
    elif hs >= 1 and hs < 2: r, g, b = (x, c, 0)
    elif hs >= 2 and hs < 3: r, g, b = (0, c, x)
    elif hs >= 3 and hs < 4: r, g, b = (0, x, c)
    elif hs >= 4 and hs < 5: r, g, b = (x, 0, c)
    elif hs >= 5 and hs < 6: r, g, b = (c, 0, x)
    m = l - (c / 2)
    return ((r+m)*255, (g+m)*255, (b+m)*255)

# Init HSL values once for faster access
_HSL_VALUES = []
for _ in range(360):
    _HSL_VALUES.append(hsl_to_rgb(_, 1, 0.5))

_LED_COUNT = 400
_DATA_OUT_PIN = machine.Pin(2, machine.Pin.OUT)
_DATA_IN_PIN = machine.Pin(4, machine.Pin.IN)
_CLOCK_IN_PIN = machine.Pin(12, machine.Pin.IN)
_MASTER_IN_PIN = machine.Pin(13, machine.Pin.IN)

_CLOCK_IN_PIN.irq(handler=lambda p: clock_tick(p))

data_in_stream = ""
volume = 0

def clock_tick(p: machine.Pin):
    global data_in_stream
    global volume

    #print("clock tick")

    if not _MASTER_IN_PIN.value():
        data_in_stream = "" # Reset data stream if master is low
        return

    #print("master is high")
    
    # Continue if master is high
    data_in_stream += str(_DATA_IN_PIN.value())

    #print(data_in_stream)

    if len(data_in_stream) == 12:
        parity_0 = data_in_stream[0]
        parity_1 = data_in_stream[-1]
        data = data_in_stream[1:-1]
        # parity, data, inv_par = data_in_stream[0], data_in_stream[1:-1], data_in_stream[-1]
        # true if odd number of 1's + high parity bit is given == if even number of 1's is given in data stream
        if (not data[:5].count("1") % 2 == int(parity_0)) or (not data[5:].count("1") % 2 == int(parity_1)):
            # print(parity_0 + " " + data + " " + parity_1 + " --- Invalid parity data. Skipping!")
            return
        
        volume = int(data, 2)
        # print(parity_0 + " " + data + " " + parity_1 + " --- Volume: " + str(volume))
        data_in_stream = ""
        return
    
    if len(data_in_stream) > 12:
        # print("resetting due to invalid length")
        data_in_stream = "" # Reset due to invalid data
        # data_in_stream = data_in_stream[-1] # Reset due to invalid data but keep newest received bit

def animate_rainbow():
    # Create buffer with given (rgbw->grbw) order and 3 Bits Per Pixel
    _BPP = 3
    _ORDER = (1, 0, 2, 3)
    buffer = bytearray(_LED_COUNT * _BPP)

    # Set up first rainbow with brightness 40%
    brightness = 0.4
    for i in range(_LED_COUNT):
        color = [int(x*brightness) for x in _HSL_VALUES[int(((i+1) / _LED_COUNT) * len(_HSL_VALUES)) % 360]]
        # color = [int(x) for x in _HSL_VALUES[int(i * (360 / _LED_COUNT)) % 360]]
        offset = i * _BPP
        for j in range(_BPP):
            buffer[offset + _ORDER[j]] = color[j]
    machine.bitstream(_DATA_OUT_PIN, 0, (400, 850, 800, 450), buffer)

    _SPEED = 1
    _BUF_SKIP = (2**(_SPEED-1))*3

    while True:
        buffer = buffer[_BUF_SKIP:] + buffer[:_BUF_SKIP] # Shift rainbow buffer
        machine.bitstream(_DATA_OUT_PIN, 0, (400, 850, 800, 450), buffer) # Write buffer to strip
        start = time.time_ns()
        while time.time_ns() - start < 1000*75:
            pass

def animate_volume():
    global volume

    # Create buffer with given (rgbw->grbw) order and 3 Bits Per Pixel
    _BPP = 3
    _ORDER = (1, 0, 2, 3)
    _EMPTY_BUFFER = bytearray(_LED_COUNT * _BPP)
    buffer = bytearray(_LED_COUNT * _BPP)

    # Clamp volume level from 0 to _LED_COUNT
    if volume < 0: volume = 0
    elif volume > _LED_COUNT: volume = _LED_COUNT
    """prev_volume = volume - 1

    while True:
        if prev_volume != volume:
            brightness = 0.4
            for i in range(volume): # I can probably speed up the buffer creation process by just showing ... (see below)
                color = [int(x*brightness) for x in _HSL_VALUES[int(((i+1) / _LED_COUNT) * len(_HSL_VALUES)) % 360]]
                # color = [int(x) for x in hsl_values[int(i * (360 / _LED_COUNT)) % 360]]
                offset = i * _BPP
                for j in range(_BPP):
                    buffer[offset + _ORDER[j]] = color[j]
        # ... the buffer from 0 to 3*volume and adding bytearray(max length - 3*volume)
        machine.bitstream(_DATA_OUT_PIN, 0, (400, 850, 800, 450), buffer) # Write buffer to strip
        start = time.time_ns()
        while time.time_ns() - start < 1000*75:
            pass"""
    
    """brightness = 0.4
    for i in range(volume):
        color = [int(x*brightness) for x in _HSL_VALUES[int(((i+1) / _LED_COUNT) * len(_HSL_VALUES)) % 360]]
        offset = i * _BPP
        for j in range(_BPP):
            buffer[offset + _ORDER[j]] = color[j]"""
    
    # Set up first rainbow with brightness 40%
    brightness = 0.4
    for i in range(_LED_COUNT):
        color = [int(x*brightness) for x in _HSL_VALUES[int(((i+1) / _LED_COUNT) * len(_HSL_VALUES)) % 360]]
        # color = [int(x) for x in _HSL_VALUES[int(i * (360 / _LED_COUNT)) % 360]]
        offset = i * _BPP
        for j in range(_BPP):
            buffer[offset + _ORDER[j]] = color[j]

    # _SPEED = 1
    # _BUF_SKIP = (2**(_SPEED-1))*3

    # Maybe save the peak level (for like 10s) to have a variable maximum instead of 300 (see below)

    # i = 0
    while True:
        # offset = (_BUF_SKIP * i) % (_LED_COUNT * _BPP)
        # out_buffer = _EMPTY_BUFFER[3*volume:] + buffer[offset:offset+(3*volume)] # This animation is still kinda glitchy
        out_vol = int((volume / 300) * _LED_COUNT)
        out_buffer = _EMPTY_BUFFER[3*out_vol:] + buffer[:3*out_vol]
        machine.bitstream(_DATA_OUT_PIN, 0, (400, 850, 800, 450), out_buffer) # Write modified buffer to strip
        # i += 1
        start = time.time_ns()
        while time.time_ns() - start < 1000*75:
            pass

#animate_rainbow()
animate_volume()
