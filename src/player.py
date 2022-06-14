import time
import board
import digitalio
import busio
import os
import adafruit_sdcard
import storage
import waveshare_LCD1602
import audioio, audiomp3
import random


PIN_PREV_YEAR = board.D10
PIN_NEXT_YEAR = board.D9
PIN_PAUSE = board.D11

PIN_SD_CD = board.D5
PIN_SD_CS = board.D13

PIN_SPKR = board.A0

switch_next_year = switch_prev_year = switch_pause = None

current_year = random.randrange(80, 90)
track_index = 0
paused = False

# Set up pins used for user-input switches
def initialise_board():
    global switch_next_year, switch_prev_year, switch_pause
    switch_next_year = digitalio.DigitalInOut(PIN_NEXT_YEAR)
    switch_prev_year = digitalio.DigitalInOut(PIN_PREV_YEAR)
    switch_pause = digitalio.DigitalInOut(PIN_PAUSE)
    switch_next_year.pull = digitalio.Pull.UP
    switch_prev_year.pull = digitalio.Pull.UP
    switch_pause.pull = digitalio.Pull.UP

# At the end of this routine there will be a filesystem mounted
# under /{mount_dir}}. It can then be accessed using standard
# Python file-access commands.
def init_sd_card(mount_dir="sd"):
    cd = digitalio.DigitalInOut(PIN_SD_CD)   # card-detect. We probably don't need to use this
    cs = digitalio.DigitalInOut(PIN_SD_CS)
    spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

    sdcard = adafruit_sdcard.SDCard(spi, cs)
    vfs = storage.VfsFat(sdcard)
    storage.mount(vfs, "/" + mount_dir)

# Create the LCD object and ensure it's in a sensible initial state
def init_lcd():
    i2c = board.I2C()

    lcd = waveshare_LCD1602.LCD1602(i2c, 16, 2)
    lcd.setRGB(0xB0, 0x80, 0x20)
    lcd.clear()
 
    return lcd

# We just need to tell the system which analog pin the amplifier is connected to
def init_player():
    return audioio.AudioOut(PIN_SPKR)



# Cycle through a few very 80s colours when we have a new year to display
def display_year(lcd):
    year = 1900 + current_year
    colours = [0xFF0000, 0x00FF00, 0xAA1155]

    for r in (0, 1):
        lcd.setCursor(0, r)
        lcd.printout("* " + str(year) + ' ** ' + str(year) + ' *')
    for c in colours * 3:
        lcd.setRGB(c >> 0x10, (c & 0xFF00) >> 8, c & 0xFF)
        time.sleep(0.2)
    lcd.setRGB(0xFF, 0xFF, 0xFF)

# Make sure the user know the player's been paused
def display_paused(lcd):
    year = 1900 + current_year

    lcd.clear()
    lcd.setCursor(0, 0)
    lcd.printout("* " + str(year) + ' ** ' + str(year) + ' *')
    lcd.setCursor(0, 1)
    lcd.printout(" PLAYER PAUSED ")
    lcd.setRGB(0xB0, 0x80, 0x20)

# Reset colours and display ready for the usual output again
def display_unpaused(lcd):
    lcd.setRGB(0xFF, 0xFF, 0xFF)
    lcd.clear()

# Return a list of integers from 0 to n, randomly shuffled
def shuffle(n):
    l = list(range(n))
    l2 = []
    while len(l) > 0:
        l2.append(l.pop(random.randrange(len(l))))
    return l2

# If the length of the string stored in text is shorter than line_len then display
# it as is.
# If the string is longer, truncate it at 16 characters and increment our offset
# counter, effectively creating a scrolling display for this string.
def wrap_text(text, line_len, offset):
    if len(text) < line_len:
        return offset, text

    offset += 1
    if offset > len(text) + 3:
        offset = 0

    new_text = (text + '   ' + text)[offset:offset + line_len]
    return offset, new_text

def year_up():
    global current_year
    current_year = min(current_year + 1, 89)

def year_down():
    global current_year
    current_year = max(current_year - 1, 80)

def toggle_pause():
    global paused
    paused = not(paused)

# A little explanation about the slightly odd way we handle track information.
# The obvious thing to do would be to read all the track names into an array and then
# randomly shuffle it. However most directories have up to 200 files in and I'm trying to
# keep memory usage low. So instead we just create a list of integers from 0..(number of files)
# and randomly shuffle that list. We can then select the nth track (as Python listdir always returns
# them in alphabetical order) and play that individually.

def get_track_count():
    return len(os.listdir("/sd/" + str(current_year)))

def get_track(track_ordering, nth_track):
    track_num = track_ordering[nth_track]
    tracks = os.listdir("/sd/" + str(current_year))
    track_filename = tracks[track_num]
    return track_filename

def play_track(player, track):
    data = open("/sd/" + str(current_year) + "/" + track, "rb")
    mp3 = audiomp3.MP3Decoder(data)
    player.play(mp3)

# This is where the main functionality lives.
# For a given year we create a random ordering of the tracks and start playing them. We periodically
# check for user input (switches pressed for Next Year, Previous Year, or Pause) and act appropriately.
# We also update the LCD display each time through the innermost loop.
def play_tracks_from_year(player, lcd_device):
    global track_index, paused

    print("Selecting music from 19{}".format(current_year))

    num_tracks = get_track_count()
    tracklist = shuffle(num_tracks)

    user_input = False

    while not(user_input):
        display_year(lcd_device)

        track = get_track(tracklist, track_index)
        
        artist, song = parse_track_name(track)
        a_offset = s_offset = 0

        print("Playing track {} ({} by {})".format(track, song, artist))
        play_track(player, track)
        lcd_device.clear()

        while player.playing and not(user_input):
            if switch_pressed(switch_pause):
                player.pause()
                print("PAUSED")
                paused = True
                display_paused(lcd_device)
                time.sleep(0.4) # debounce

            while paused:
                time.sleep(0.1)
                if switch_pressed(switch_pause):
                    player.resume()
                    print("UNPAUSED")
                    display_unpaused(lcd_device)
                    paused = False
                    time.sleep(0.5) # debounce

            # After checking for Pause as above, this is actually all that's involved in the
            # main inner loop, as the audiomp3 library very handily plays in a background thread
            # so we don't actually need to do anything other than update the display and check
            # user input.
            delay = time.monotonic()
            while (time.monotonic() - delay < 0.4) and not(user_input):
                user_input = check_switches()
            a_offset, s_offset = display_now_playing(lcd_device, artist, song, a_offset, s_offset)
        
        track_index += 1
        if track_index >= num_tracks:
            tracklist = shuffle(num_tracks)
            track_index = 0

    if player.playing:
        player.stop()

# Output the artist & song on the Waveshare LCD
def display_now_playing(lcd_device, artist, song, a_offset, s_offset):
    new_a_offset, a_display = wrap_text(artist, 16, a_offset)
    new_s_offset, s_display = wrap_text(song, 16, s_offset)
    lcd_device.setCursor(0, 0)
    lcd_device.printout(a_display)
    lcd_device.setCursor(0, 1)
    lcd_device.printout(s_display)

    return new_a_offset, new_s_offset

# everything before the first hyphen will be the artist name
# everything after will be the track name, with a .mp3 suffix that we strip out
def parse_track_name(track):
    return track.split(" - ")[0], "".join((track.split(" - ")[1:]))[:-4]

def switch_pressed(switch):
    return not(switch.value)

def check_switches():
    if switch_pressed(switch_next_year):
        year_up()
        return True
    elif switch_pressed(switch_prev_year):
        year_down()
        return True

    return False


# As well as calling the relevant routines to initialise external hardware/shields,
# this returns references to the LCD and Audio Player objects, as we'll need to
# make use of these references later on.
def initialise_devices():
    init_sd_card()
    lcd_device = init_lcd()
    player = init_player()

    return lcd_device, player

def main():
    initialise_board()
    lcd_device, player = initialise_devices()
    while True:
        play_tracks_from_year(player, lcd_device)

main()
