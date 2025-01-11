import struct
from lu77U_SHA256.Right_Rotator import RightRotator

class InputParser:
    def __init__(self, input_data):
        self.input_data = input_data

    def process_chunks(self):
        result = []
        for i in range(0, len(self.input_data), 64):
            chunk = self.input_data[i:i + 64]
            w = list(struct.unpack('>16L', chunk)) + [0] * 48
            for i in range(16, 64):
                s0 = RightRotator(w[i - 15], 7).right_rotate() ^ RightRotator(w[i - 15], 18).right_rotate() ^ (w[i - 15] >> 3)
                s1 = RightRotator(w[i - 2], 17).right_rotate() ^ RightRotator(w[i - 2], 19).right_rotate() ^ (w[i - 2] >> 10)
                w[i] = (w[i - 16] + s0 + w[i - 7] + s1) & 0xFFFFFFFF

            result.append(w)

        return result