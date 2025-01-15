# BA63USB
Python library for Nixdorf BA63 USB display


Allows displaying messages on a Wincor Nixdorf BA63 USB HID display.


Example usage:
```
from ba63usb import BA63USB
devs = BA63USB.get()
dev = BA63USB(devs[0]["path"])

dev.clear()
dev.set_charset(0x34) # Change to 858 codepage Latin1+€
dev.set_cursor(1,1)
dev.print("Test °äöü€#*\n\rCount")

for i in range(255):
    dev.set_cursor(2,7)
    dev.print(f"{i}".ljust(3))

```
