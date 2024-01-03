import serial
import os
import time
import msgpack
from datetime import datetime
from shutil import move
from ebyte import EbyteRaspberryPi, MODE_NORMAL

def send_file(serial_port, file_path):
    try:
        with open(file_path, "rb") as file:
            file_data = file.read()
        file_info = {
            "name": os.path.basename(file_path),
            "data": file_data
        }
        packed_data = msgpack.packb(file_info)
        serial_port.write(packed_data)
        print(f"Datei gesendet: {file_path}")
    except Exception as e:
        print(f"Fehler beim Senden der Datei {file_path}: {e}")

def check_for_messages_to_send(to_send_dir, sent_dir, serial_port):
    for filename in os.listdir(to_send_dir):
        filepath = os.path.join(to_send_dir, filename)
        send_file(serial_port, filepath)
        sent_filepath = os.path.join(sent_dir, filename)
        move(filepath, sent_filepath)

def receive_and_save_file(serial_port, save_dir):
    unpacker = msgpack.Unpacker()
    if serial_port.inWaiting() > 0:
        chunk = serial_port.read(serial_port.inWaiting())
        unpacker.feed(chunk)
        for unpacked_data in unpacker:
            if 'name' in unpacked_data and 'data' in unpacked_data:
                file_name = unpacked_data['name']
                file_data = unpacked_data['data']
                save_path = os.path.join(save_dir, file_name)
                with open(save_path, "wb") as file:
                    file.write(file_data)
                print(f"Datei empfangen und gespeichert: {save_path}")

def automatic_mode(ser, to_send_dir, received_dir):
    while True:
        check_for_messages_to_send(to_send_dir, received_dir, ser)
        receive_and_save_file(ser, received_dir)
        time.sleep(1)  # Kurze Pause, um andere Prozesse zu ermöglichen

def main():
    PIN_M0 = 23
    PIN_M1 = 24
    PIN_AUX = 25

    ser = serial.Serial('/dev/serial0')
    ebyte = EbyteRaspberryPi(ser, PIN_M0, PIN_M1, PIN_AUX)
    ebyte.set_mode(MODE_NORMAL)

    received_dir = "received"
    to_send_dir = "to_sent"
    sent_dir = "sent"
    os.makedirs(received_dir, exist_ok=True)
    os.makedirs(to_send_dir, exist_ok=True)
    os.makedirs(sent_dir, exist_ok=True)

    while True:
        print("\nWählen Sie einen Modus:")
        print("1: Automatik")
        print("2: Beenden")
        choice = input("Eingabe: ")

        if choice == '1':
            print("Automatikmodus gestartet. Zum Beenden Strg+C drücken.")
            automatic_mode(ser, to_send_dir, received_dir)
        elif choice == '2':
            break
        else:
            print("Ungültige Auswahl. Bitte wählen Sie 1 oder 2.")

if __name__ == '__main__':
    main()
