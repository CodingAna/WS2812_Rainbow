import machine

_LED_COUNT = 400
_PIN_PORT = 2
_PIN = machine.Pin(_PIN_PORT, machine.Pin.OUT)

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

def animate():
    # Init HSL values once for faster access
    hsl_values = []
    for _ in range(360):
        hsl_values.append(hsl_to_rgb(_, 1, 0.5))
    
    # Create buffer with given (rgbw->grbw) order and 3 Bits Per Pixel
    _BPP = 3
    _ORDER = (1, 0, 2, 3)
    buffer = bytearray(_LED_COUNT * _BPP)

    # Init with no color
    for i in range(_LED_COUNT):
        color = (0, 0, 0)
        offset = i * _BPP
        for j in range(_BPP):
            buffer[offset + _ORDER[j]] = color[j]
    machine.bitstream(_PIN, 0, (400, 850, 800, 450), buffer)

    # Set up first rainbow
    for i in range(_LED_COUNT):
        color = [int(x) for x in hsl_values[int(i * (360 / _LED_COUNT)) % 360]]
        offset = i * _BPP
        for j in range(_BPP):
            buffer[offset + _ORDER[j]] = color[j]
    machine.bitstream(_PIN, 0, (400, 850, 800, 450), buffer)

    _SPEED = 1
    _BUF_SKIP = (2**(_SPEED-1))*3
    # step = 0

    while True:
        # _BUF_SKIP = int(step)*3
        buffer = buffer[_BUF_SKIP:] + buffer[:_BUF_SKIP] # Shift rainbow buffer
        machine.bitstream(_PIN, 0, (400, 850, 800, 450), buffer) # Write buffer to strip
        # step += _SPEED
        # if (step == int(step)): step = 0

animate()
