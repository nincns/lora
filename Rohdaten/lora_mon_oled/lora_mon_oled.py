import serial
import time
import subprocess
from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

# Funktion zum Lesen von Daten von der seriellen Schnittstelle
def receive_data(serial_port):
    if serial_port.inWaiting() > 0:
        return serial_port.read(serial_port.inWaiting()).decode()
    return None

# I2C- und Display-Setup
i2c = busio.I2C(SCL, SDA)
disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
disp.fill(0)
disp.show()
width = disp.width
height = disp.height
image = Image.new("1", (width, height))
draw = ImageDraw.Draw(image)
font = ImageFont.truetype('/home/shentsch/python-scripts/CONSOLA.TTF', 12)

# Serielle Schnittstelle einrichten
ser = serial.Serial('/dev/serial0')  # Ersetzen Sie dies durch den richtigen Port

while True:
    # Bildschirm löschen
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    # Daten von der seriellen Schnittstelle lesen
    data = receive_data(ser)
    if data:
        # Text auf dem Display anzeigen
        draw.text((0, 0), "Empfangene Daten:", font=font, fill=255)
        draw.text((0, 16), data, font=font, fill=255)
    else:
        # Meldung anzeigen, wenn keine Daten empfangen wurden
        draw.text((0, 0), "Warte auf Daten...", font=font, fill=255)

    # Bild anzeigen
    disp.image(image.rotate(180))
    disp.show()
    time.sleep(0.1)  # Aktualisierungsintervall
