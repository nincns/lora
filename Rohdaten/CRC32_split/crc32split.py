import zlib
import os
import sys

# Globale Variable für die Paketgröße
PAKET_GROESSE = 128

# Pfad, in dem die aufgeteilten Dateiteile gespeichert werden sollen
AUSGABE_VERZEICHNIS = 'split_files'

def crc32_checksum(data):
    return format(zlib.crc32(data) & 0xFFFFFFFF, '08x')

def berechne_gesamtteile(file_size, header_size):
    return (file_size + PAKET_GROESSE - header_size - 1) // (PAKET_GROESSE - header_size)

def teile_datei(filename, zieldatei_basename):
    # Extrahieren von Dateinamen und Endung
    dateiname, dateiendung = os.path.splitext(os.path.basename(filename))
    # Begrenzung des Dateinamens (ohne Endung) auf 8 Zeichen
    begrenzter_dateiname = dateiname[:8] + dateiendung

    with open(filename, 'rb') as file:
        file_size = os.path.getsize(filename)
        header_size = len(begrenzter_dateiname) + 1 + 8 + 1 + 9  # Berechnung der Header-Größe
        gesamtteile = berechne_gesamtteile(file_size, header_size)
        teil_nummer = 1
        while True:
            daten = file.read(PAKET_GROESSE - header_size)
            if not daten:
                break
            checksum = crc32_checksum(daten)
            teil_nummer_str = f"{teil_nummer:04d}-{gesamtteile:04d}"
            header = f"{begrenzter_dateiname}|{checksum}|{teil_nummer_str}|".encode()

            # Erstellen des Dateinamens für das Paket
            zieldatei = os.path.join(AUSGABE_VERZEICHNIS, f"{zieldatei_basename}-{teil_nummer:04d}.part")

            # Schreiben des Headers und der Daten in die Teil-Datei
            with open(zieldatei, 'wb') as ziel:
                ziel.write(header)
                ziel.write(daten)

            print(f"{zieldatei};{checksum};{teil_nummer_str}")
            teil_nummer += 1

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python md5split.py [Dateiname]")
        sys.exit(1)

    eingabe_datei = sys.argv[1]
    zieldatei_basename = os.path.splitext(os.path.basename(eingabe_datei))[0]
    teile_datei(eingabe_datei, zieldatei_basename)
