import network
import time
from neopixel import Neopixel
import socket
import dotenv
import os

from machine import Pin

dotenv.load_dotenv()

board_led = Pin("LED", Pin.OUT)

ssid = os.getenv("WIFI_SSID")
password = os.getenv("WIFI_PASS")

available_colors = {
    "BLUE": (0, 0, 255),
    "RED": (255, 0, 0),
    "GREEN": (0, 255, 0)
}

html = """<!DOCTYPE html>
<html>
    <head> <title>Pico W</title> </head>
    <body> <h1>Pico W</h1>
        <p>%s</p>
    </body>
</html>
"""

board_led.value(1)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# quick clear all
strip = Neopixel(999, 0, 0, "GRB")
strip.clear()
strip.show()

numpix = 50
K = 3

strip = Neopixel(numpix, 0, 0, "GRB")

red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)

strip.brightness(5)
strip.clear()
strip.show()


def switch_led(c):
    strip.fill(c)
    strip.show()


def turn_off_led():
    strip.clear()


max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)

if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('connected')
    status = wlan.ifconfig()
    print('ip = ' + status[0])

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)

print('listening on', addr)


def handle(request):
    if request.find('/light/blue') == 6:
        switch_led(available_colors['BLUE'])
    if request.find('/light/red') == 6:
        switch_led(available_colors['RED'])
    if request.find('/light/green') == 6:
        switch_led(available_colors['GREEN'])


board_led.off()

# Listen for connections
while True:
    try:
        cl, addr = s.accept()
        print('client connected from', addr)
        request = cl.recv(1024)
        rq = request.decode()
        print(rq)

        request = str(request)
        response = handle(request)

        response = html % response

        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.send(response)
        cl.close()

    except OSError as e:
        cl.close()
        print('connection closed')
