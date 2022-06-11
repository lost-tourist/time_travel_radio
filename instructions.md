# Assembly

## Notes

These instructions will be aided with Fritzing images and schematics at
some point in the (hopefully near) future. Until then a textual description
will be better than nothing.

## Choice of microcontroller board

Decoding of mp3 files requires significant amounts of processor power and
memory (significant for microcontrollers, at least). The current crop of
SAMD51-based boards should be able to cope, and although I haven't fully tested
it I suspect many of the RP2040-based boards will be fine.

You won't have any luck using older ATMega based boards such as classic
Arduino Uno or Micro boards.

Whichever board you select, as well as a powerful processor and a decent amount
of SRAM, it will need to have pins for I2C, SPI, and analog out, and be
well supported by CircuitPython.

My choice of board was the Sparkfun Thing Plus SAMD51.

## Thing Plus Wiring

| pin | connection |
| --- | ---------- |
| SDA | LCD SDA |
| SCL | LCD SCL |
| D5 | micro-sd CD |
| D6 | *unused* |
| D9 | YRNXT push-button switch |
| D10 | YRPRV push-button switch |
| D11 | *unused* |
| D12 | *unused* |
| D13 | micro-sd CS |
| VUSB | *unused* |
| EN | *unused* |
| VBAT | *unused* |

| pin | connection |
| --- | ---------- |
| D4 | *unused* |
| D1 | *unused* |
| D0 | *unused* |
| MISO | sd-card DO |
| MOSI | sd-card DI |
| SCK | sd-card CLK |
| A5 | *unused* |
| A4 | *unused* |
| A3 | *unused* |
| A2 | *unused* |
| A1 | *unused* |
| A0 | PAM8302 A+ |
| GND | GND busbar |
| NC | *unused* |
| 3V3 | VCC busbar |
| RESET | *unused* |

## Other connections

* VCC and GND to each of LCD1602, sd-card breakout module, PAM8302 amplifier
* 10k pull-up resistor betwee VCC and sd-card CS
* GND to each of the three push-button switches
