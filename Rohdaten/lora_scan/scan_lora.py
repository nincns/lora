import serial
import time
from ebyte import EbyteRaspberryPi, MODE_NORMAL

def receive_data(serial_port):
    data = ""
    if serial_port.inWaiting() > 0:
        data = serial_port.read(serial_port.inWaiting()).decode()
    return data

def main():
    PIN_M0 = 23
    PIN_M1 = 24
    PIN_AUX = 25

    ser = serial.Serial('/dev/serial0')
    ebyte = EbyteRaspberryPi(ser, PIN_M0, PIN_M1, PIN_AUX)
    ebyte.set_mode(MODE_NORMAL)

    print("Wechsel durch die Kanäle...")
    while True:
        for chan in range(32):  # Durchläuft alle 32 Kanäle (0 bis 31)
            ebyte.chan = chan  # Setzt den aktuellen Kanal
            print(f"Aktueller Kanal: {chan}")
            time.sleep(20)  # Warte 20 Sekunden

            incoming_message = receive_data(ser)
            if incoming_message:
                print(f"Empfangene Nachricht auf Kanal {chan}: {incoming_message}")

if __name__ == '__main__':
    main()
