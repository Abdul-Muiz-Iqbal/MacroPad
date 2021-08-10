from automaton.core import Automaton, Key, Button, Peripheral, LockState
from enum import Enum
import evdev, os
import atexit

atexit.register(lambda: os.system("xset -led named 'Scroll Lock'"))

DEVICES: list[str] = ['/dev/input/event6', '/dev/input/event5']
SCROLL_LOCK_TOGGLE = False

class MacroPadState(Enum):
    Off     = 0
    PageOne = 1
    PageTwo = 2

    def get(app: Automaton) -> 'MacroPadState':
        states = [
            app.device.is_toggled(Key.NumLock),
            SCROLL_LOCK_TOGGLE
        ]
        if all(states):
            return MacroPadState.PageTwo
        elif (not states[0]) and states[1]:
            return MacroPadState.PageOne
        else:
            return MacroPadState.Off

app = Automaton.new(DEVICES)

# Dirty hack that gives me a visual indicator of when MacroPad is on or off
# Has to be used because Scroll Lock by default is not detected by Ubuntu.
@app.on([Key.ScrollLock])
def toggle():
    global SCROLL_LOCK_TOGGLE
    os.system(f"xset {'-' if SCROLL_LOCK_TOGGLE else ''}led named 'Scroll Lock'")
    SCROLL_LOCK_TOGGLE = not SCROLL_LOCK_TOGGLE

# Set ScrollLock and NumLock On by default
toggle()
app.device.set_state(Key.NumLock, LockState.On)


# Remaps, HotStrings, And HotKeys that activate only if ScrollLock is On and Numlock is Off
context = lambda: MacroPadState.get(app) is MacroPadState.PageOne

app.remap(Key.Numpad4, Button.LeftButton, context)
app.remap(Key.Numpad5, Button.MiddleButton, context)
app.remap(Key.Numpad6, Button.RightButton, context)
app.remap(Key.Numpad8, Key.ScrollUp, context)
app.remap(Key.Numpad2, Key.ScrollDown, context)

# Remaps, HotStrings, And HotKeys that activate only if ScrollLock is On and Numlock is On
context = lambda: MacroPadState.get(app) is MacroPadState.PageTwo

app.remap(Key.Numpad0, Key.PlayPause, context)
app.remap(Key.NumpadPeriod, Key.Mute, context)
app.remap(Key.NumpadPlus, Key.VolumeUp, context)
app.remap(Key.NumpadMinus, Key.VolumeDown, context)

# Remaps, HotStrings, And HotKeys that activate no matter what.
#@app.on([Key.Compose])
#def send_shift_enter():
#    app.device.press(Key.LShift)
#    app.device.tap(Key.Enter)
#    app.device.release(Key.LShift)

# HotStrings
app.on("]c")(lambda: "©")
app.on("]r")(lambda: "®")
app.on("]tm")(lambda: "™")

app.on("@@")(lambda: "parkermuiz0@gmail.com")
app.on("@@h")(lambda: "muizparker@hotmail.com")

def fmt(app: Automaton, txt: str):
    app.device.type_ascii(txt)
    app.device.tap(Key.Home)
    app.device.type_ascii(txt)
    app.device.tap(Key.End)

app.on("//b")(lambda: fmt(app, '*'))
app.on("//i")(lambda: fmt(app, '_'))
app.on("//u")(lambda: fmt(app, '~'))
app.on("//c")(lambda: fmt(app, '```'))

app.run()
