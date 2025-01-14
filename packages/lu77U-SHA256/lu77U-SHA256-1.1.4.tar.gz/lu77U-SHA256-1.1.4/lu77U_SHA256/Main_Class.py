from lu77U_SHA256.Right_Rotator import RightRotator

class MainClass:
    K = [
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
        0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
        0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
        0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
        0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
        0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
        0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
        0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
    ]

    H = [
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
    ]

    def __init__(self, expanded_message_schedule):
        self.expanded_message_schedule = expanded_message_schedule

    def hash_message(self):
        for chunk in self.expanded_message_schedule:
            a, b, c, d, e, f, g, h = self.H
            
            for i in range(64):
                w_i = chunk[i]
                
                s1 = RightRotator(e, 6).right_rotate() ^ RightRotator(e, 11).right_rotate() ^ RightRotator(e, 25).right_rotate()
                ch = (e & f) ^ (~e & g)
                temp1 = (h + s1 + ch + MainClass.K[i] + w_i) & 0xFFFFFFFF
                
                s0 = RightRotator(a, 2).right_rotate() ^ RightRotator(a, 13).right_rotate() ^ RightRotator(a, 22).right_rotate()
                maj = (a & b) ^ (a & c) ^ (b & c)
                temp2 = (s0 + maj) & 0xFFFFFFFF
                
                h, g, f, e, d, c, b, a = g, f, e, (d + temp1) & 0xFFFFFFFF, c, b, a, (temp1 + temp2) & 0xFFFFFFFF
            
            self.H[0] = (self.H[0] + a) & 0xFFFFFFFF
            self.H[1] = (self.H[1] + b) & 0xFFFFFFFF
            self.H[2] = (self.H[2] + c) & 0xFFFFFFFF
            self.H[3] = (self.H[3] + d) & 0xFFFFFFFF
            self.H[4] = (self.H[4] + e) & 0xFFFFFFFF
            self.H[5] = (self.H[5] + f) & 0xFFFFFFFF
            self.H[6] = (self.H[6] + g) & 0xFFFFFFFF
            self.H[7] = (self.H[7] + h) & 0xFFFFFFFF
        
        return ''.join(f'{x:08x}' for x in self.H)