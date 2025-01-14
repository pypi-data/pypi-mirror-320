class RightRotator:
    def __init__(self, value, bits):
        self.value = value
        self.bits = bits

    def right_rotate(self):
        return ((self.value >> self.bits) | (self.value << (32 - self.bits))) & 0xFFFFFFFF