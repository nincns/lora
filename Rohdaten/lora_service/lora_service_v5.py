#!/usr/local/bin/python
# content of lora_service_v5.py
import serial
import os
import time
import hashlib
import logging
from datetime import datetime
from shutil import move
from ebyte import EbyteRaspberryPi, MODE_NORMAL

# Global constants for the pin configuration and packet size
PIN_M0 = 23
PIN_M1 = 24
PIN_AUX = 25
PACKET_SIZE = 64  # Packet size should be in the range of 32 and 192


def setup_logging():
    # Sets up the logging configuration.
    log_file_path = 'app.log'
    logging.basicConfig(filename=log_file_path, filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

def calculate_md5(file_path):
    # Calculates and returns the MD5 hash of a file.
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def calculate_md5_from_bytes(byte_content):
    # Calculates and returns the MD5 hash of byte content.
    hash_md5 = hashlib.md5()
    hash_md5.update(byte_content)
    return hash_md5.hexdigest()

def send_file(serial_port, file_path, packet_size=PACKET_SIZE):
    # Sends a file over the serial port.
    try:
        file_hash = calculate_md5(file_path)
        file_name = os.path.basename(file_path)
        serial_port.write(f"{file_hash};{file_name};BTM;".encode())

        with open(file_path, "rb") as file:
            while True:
                file_data = file.read(packet_size)
                if not file_data:
                    break
                serial_port.write(file_data)
                time.sleep(0.5)

        serial_port.write(f";EOF".encode())
        logging.info(f"File sent: {file_path}")
    except Exception as e:
        logging.error(f"Error sending file {file_path}: {e}")

def send_status(serial_port, status_code):
    """
    Send a status code via the serial port.
    
    :param serial_port: The serial port object for communication.
    :param status_code: The status code to send.
    """
    try:
        # Konvertiert den Statuscode in eine Zeichenkette und kodiert ihn
        status_message = str(status_code).encode()

        # Sendet die Nachricht über den seriellen Port
        serial_port.write(status_message)

        logging.info(f"Status code sent: {status_code}")
    except Exception as e:
        logging.error(f"Error sending status code {status_code}: {e}")

def check_for_messages_to_send(to_send_dir, sent_dir, serial_port):
    # Checks for messages to be sent and moves them to the sent directory after sending.
    for filename in os.listdir(to_send_dir):
        filepath = os.path.join(to_send_dir, filename)
        send_file(serial_port, filepath)
        sent_filepath = os.path.join(sent_dir, filename)
        move(filepath, sent_filepath)
        logging.info(f"Message moved from {to_send_dir} to {sent_dir}: {filename}")

def generate_filename(base_dir, suffix):
    # Generates a unique filename with a timestamp.
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d_%H-%M-%S-%f")
    return os.path.join(base_dir, f"{date_str}_{suffix}.bin")

def receive_and_save_file(serial_port, save_dir):
    # Receives data from the serial port and saves it as a file.
    if serial_port.inWaiting() > 0:
        file_data = serial_port.read(serial_port.inWaiting())
        file_name = generate_filename(save_dir, "received")
        with open(file_name, "wb") as file:
            file.write(file_data)
        logging.info(f"File received and saved: {file_name}")

def build_file(serial_port, received_dir):
    received_files = sorted([f for f in os.listdir(received_dir) if f.endswith('.bin')])

    if not received_files:
        return False

    # Überprüfen, ob die erste Datei den BTM-Marker und die letzte Datei den EOF-Marker enthält
    with open(os.path.join(received_dir, received_files[0]), "rb") as first_file:
        first_file_content = first_file.read()
        if b";BTM;" not in first_file_content:
            return False

    with open(os.path.join(received_dir, received_files[-1]), "rb") as last_file:
        last_file_content = last_file.read()
        if b";EOF" not in last_file_content:
            return False

    file_data_parts = []
    file_name = None
    expected_hash = None
    eof_found = False

    for i, file in enumerate(received_files):
        with open(os.path.join(received_dir, file), "rb") as f:
            content = f.read()

        # Verarbeiten des Headers im ersten Teil
        if i == 0:
            header_parts = content.split(b";BTM;")
            if len(header_parts) > 1:
                header, content = header_parts
                try:
                    expected_hash, file_name = header.rsplit(b";", 1)
                    logging.info(f"Header extracted: Hash={expected_hash}, Filename={file_name}")
                except ValueError:
                    logging.error("Hash and filename not found in the header.")
                    return False
            else:
                logging.error("Header format is incorrect.")
                return False

        # Verarbeiten des EOF-Markers im letzten Teil
        if i == len(received_files) - 1:
            eof_parts = content.split(b";EOF")
            if len(eof_parts) > 1:
                content = eof_parts[0]
                eof_found = True

        file_data_parts.append(content)

    file_data = b''.join(file_data_parts)

    if file_name and eof_found:
        full_file_path = os.path.join(received_dir, file_name.decode())
        with open(full_file_path, "wb") as f:
            f.write(file_data)

        if expected_hash and calculate_md5(full_file_path) == expected_hash.decode():
            logging.info(f"Complete file received and saved: {full_file_path}")
            send_status(serial_port, 200)
            for file in received_files:
                os.remove(os.path.join(received_dir, file))
            return True
        else:
            logging.warning(f"Received file is corrupt: {full_file_path}")
            return False
    elif not eof_found:
        logging.warning("Transmission failed: EOF marker not found.")
        return False

def automatic_mode(ser, to_send_dir, received_dir):
    # Runs the automatic send/receive mode.
    idle_counter = 0

    while True:
        messages_sent = check_for_messages_to_send(to_send_dir, received_dir, ser)
        messages_received = receive_and_save_file(ser, received_dir)

        if not messages_sent and not messages_received:
            idle_counter += 1
        else:
            idle_counter = 0

        if idle_counter >= 10:
            if check_for_start_and_end_markers(received_dir):
                eof_found = build_file(ser, received_dir)
                if eof_found:
                    idle_counter = 0
                else:
                    idle_counter = 9

        time.sleep(0.5)

def check_for_start_and_end_markers(received_dir):
    received_files = sorted([f for f in os.listdir(received_dir) if f.endswith('.bin')])
    if not received_files:
        return False

    with open(os.path.join(received_dir, received_files[0]), "rb") as first_file:
        first_file_content = first_file.read()
        if b";BTM;" not in first_file_content:
            return False

    with open(os.path.join(received_dir, received_files[-1]), "rb") as last_file:
        last_file_content = last_file.read()
        if b";EOF" not in last_file_content:
            return False

    return True

def main():
    # Main function to set up and run the service.
    ser = serial.Serial('/dev/serial0')
    ebyte = EbyteRaspberryPi(ser, PIN_M0, PIN_M1, PIN_AUX)
    ebyte.set_mode(MODE_NORMAL)

    received_dir = "received"
    to_send_dir = "to_sent"
    sent_dir = "sent"
    os.makedirs(received_dir, exist_ok=True)
    os.makedirs(to_send_dir, exist_ok=True)
    os.makedirs(sent_dir, exist_ok=True)

    logging.info("Automatic mode started.")
    automatic_mode(ser, to_send_dir, received_dir)
    setup_logging()

if __name__ == '__main__':
    main()
