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

# SD Card setup

The card should be formatted as VFAT and contain the following directories at
the top level:

    /80/  /81/  /82/  /83/  /84/  /85/  /86/  /87/  /88/  /89/

and then you need to place your mp3s within the appropriate directory. The program
doesn't do any kind of checking that an mp3 in the /86/ directory, for example, really
is from 1986. It's up to you to do the hard work beforehand!

In order for the LCD to display the Artist and Song Name correctly, the mp3 file
should have the following format:

    "Artist - Title.mp3"

either or both of those can contain spaces but the artist mustn't have a " - " (space-hyphen-space) as the code assumes everything up until the first occurrence of that string is the Artist Name, everything afterwards is the Song Name.

Examples:

    "Wham! - Freedom.mp3"
    "Frankie Goes to Hollywood - Two Tribes.mp3"

