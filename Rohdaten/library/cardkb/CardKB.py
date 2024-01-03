class CardKB:
    def __init__(self, i2c, addr=0x5F):
        self.i2c = i2c
        self.addr = addr
        self.key_map = self._create_key_map()

    def _create_key_map(self):
        key_map = {
            # number row
            0x1B: "ESC",
            0x31: "1",
            0x32: "2",
            0x33: "3",
            0x34: "4",
            0x35: "5",
            0x36: "6",
            0x37: "7",
            0x38: "8",
            0x39: "9",
            0x30: "0",
            0x08: "BACKSPACE",

            # top row
            0x09: "TAB",
            0x71: "Q",
            0x77: "W",
            0x65: "E",
            0x72: "R",
            0x74: "T",
            0x79: "Y",
            0x75: "U",
            0x69: "I",
            0x6F: "O",
            0x70: "P",

            # home row
            0x61: "A",
            0x73: "S",
            0x64: "D",
            0x66: "F",
            0x67: "G",
            0x68: "H",
            0x6A: "J",
            0x6B: "K",
            0x6C: "L",
            0x0D: "ENTER",

            # bottom row
            0x7A: "Z",
            0x78: "X",
            0x63: "C",
            0x76: "V",
            0x62: "B",
            0x6E: "N",
            0x6D: "M",
            0x2C: "COMMA",
            0x2E: "DOT",
            0x20: "SPACE",

            # arrow keys
            0xB4: "LEFT",
            0xB5: "UP",
            0xB6: "DOWN",
            0xB7: "RIGHT",

            # number row symbols
            0x21: "LEFTSHIFT, 1",
            0x40: "LEFTSHIFT, 2",
            0x23: "LEFTSHIFT, 3",
            0x24: "LEFTSHIFT, 4",
            0x25: "LEFTSHIFT, 5",
            0x5E: "LEFTSHIFT, 6",
            0x26: "LEFTSHIFT, 7",
            0x2A: "LEFTSHIFT, 8",
            0x28: "LEFTSHIFT, 9",
            0x29: "LEFTSHIFT, 0",
            0x7B: "LEFTSHIFT, LEFTBRACE",
            0x7D: "LEFTSHIFT, RIGHTBRACE",

            # top row symbols
            0x5B: "LEFTBRACE",
            0x5D: "RIGHTBRACE",
            0x2f: "SLASH",
            0x5C: "BACKSLASH", 
            0x7C: "LEFTSHIFT, BACKSLASH",
            0x7E: "LEFTSHIFT, GRAVE",
            0x27: "APOSTROPHE",
            0x22: "LEFTSHIFT, APOSTROPHE",

            # bottom row symbols
            0x3B: "SEMICOLON",
            0x3A: "LEFTSHIFT, SEMICOLON",
            0x60: "GRAVE",
            0x2B: "LEFTSHIFT, EQUAL",
            0x2D: "MINUS",
            0x5F: "LEFTSHIFT, MINUS",
            0x3D: "EQUAL",
            0x3F: "LEFTSHIFT, SLASH",
            0x3C: "LEFTSHIFT, COMMA",
            0x3E: "LEFTSHIFT, DOT",

            # top row capitals
            0x51: "LEFTSHIFT, Q",
            0x57: "LEFTSHIFT, W",
            0x45: "LEFTSHIFT, E",
            0x52: "LEFTSHIFT, R",
            0x54: "LEFTSHIFT, T",
            0x59: "LEFTSHIFT, Y",
            0x55: "LEFTSHIFT, U",
            0x49: "LEFTSHIFT, I",
            0x4F: "LEFTSHIFT, O",
            0x50: "LEFTSHIFT, P",

            # home row capitals
            0x41: "LEFTSHIFT, A",
            0x53: "LEFTSHIFT, S",
            0x44: "LEFTSHIFT, D",
            0x46: "LEFTSHIFT, F",
            0x47: "LEFTSHIFT, G",
            0x48: "LEFTSHIFT, H",
            0x4A: "LEFTSHIFT, J",
            0x4B: "LEFTSHIFT, K",
            0x4C: "LEFTSHIFT, L",

            # bottom row capitals
            0x5A: "LEFTSHIFT, Z",
            0x58: "LEFTSHIFT, X",
            0x43: "LEFTSHIFT, C",
            0x56: "LEFTSHIFT, V",
            0x42: "LEFTSHIFT, B",
            0x4E: "LEFTSHIFT, N",
            0x4D: "LEFTSHIFT, M",

            # fn key will be used as Ctrl
            # number row Ctrls 
            # 0x80: "LEFTCTRL, ESC",
            0x81: "LEFTCTRL, 1",
            0x82: "LEFTCTRL, 2",
            0x83: "LEFTCTRL, 3",
            0x84: "LEFTCTRL, 4",
            0x85: "LEFTCTRL, 5",
            0x86: "LEFTCTRL, 6",
            0x87: "LEFTCTRL, 7",
            0x88: "LEFTCTRL, 8",
            0x89: "LEFTCTRL, 9",
            0x8A: "LEFTCTRL, 0",
            0x8B: "LEFTCTRL, BACKSPACE",

            # top row Ctrls
            0x8C: "LEFTCTRL, TAB",
            0x8D: "LEFTCTRL, Q",
            0x8E: "LEFTCTRL, W",
            0x8F: "LEFTCTRL, E",
            0x90: "LEFTCTRL, R",
            0x91: "LEFTCTRL, T",
            0x92: "LEFTCTRL, Y",
            0x93: "LEFTCTRL, U",
            0x94: "LEFTCTRL, I",
            0x95: "LEFTCTRL, O",
            0x96: "LEFTCTRL, P",
        
            # home row Ctrls
            0x9A: "LEFTCTRL, A",
            0x9B: "LEFTCTRL, S",
            0x9C: "LEFTCTRL, D",
            0x9D: "LEFTCTRL, F",
            0x9E: "LEFTCTRL, G",
            0x9F: "LEFTCTRL, H",
            0xA0: "LEFTCTRL, J",
            0xA1: "LEFTCTRL, K",
            0xA2: "LEFTCTRL, L",
            0xA3: "LEFTCTRL, ENTER",

            # bottom row Ctrls
            0xA6: "LEFTCTRL, Z",
            0xA7: "LEFTCTRL, X",
            0xA8: "LEFTCTRL, C",
            0xA9: "LEFTCTRL, V",
            0xAA: "LEFTCTRL, B",
            0xAB: "LEFTCTRL, N",
            0xAC: "LEFTCTRL, M",
            0xAD: "LEFTCTRL, COMMA",
            0xAE: "LEFTCTRL, DOT",
            0xAF: "LEFTCTRL, SPACE",
            
            # arrow key Ctrls
            0x98: "LEFTCTRL, LEFT",
            0x99: "LEFTCTRL, UP",
            0xA4: "LEFTCTRL, DOWN",
            0xA5: "LEFTCTRL, RIGHT",
            }
        return key_map

    def read_key(self):
        # Überprüfen, ob das Gerät bereit ist
        if self.addr not in self.i2c.scan():
            return None

        # Tastendruck lesen
        try:
            data = self.i2c.readfrom(self.addr, 1)
            key_code = data[0]
            return self.key_map.get(key_code, None)
        except OSError:
            return None

    def is_key_pressed(self, key):
        # Überprüfen, ob eine bestimmte Taste gedrückt wurde
        return self.read_key() == key
