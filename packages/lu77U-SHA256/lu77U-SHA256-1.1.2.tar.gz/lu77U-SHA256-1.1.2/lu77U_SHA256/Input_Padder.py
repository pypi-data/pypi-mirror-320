import struct

class InputPadder:
    def __init__(self, data):
        self.data = data.encode()

    def pad_input(self):
        bit_length = len(self.data) * 8
        self.data += b'\x80'
        
        while (len(self.data)*8) % 512 != 448:
            self.data += b'\x00'

        self.data += struct.pack('>Q', bit_length)
        
        return self.data