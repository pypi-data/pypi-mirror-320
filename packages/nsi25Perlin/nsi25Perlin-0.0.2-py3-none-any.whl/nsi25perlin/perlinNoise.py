from random import seed, randint
from math import floor

from proto import proto

def fade(t: int | float) -> int | float:
    return t * t * t * (t * (t * 6 - 15) + 10)

def lerp(t: int | float, a: int | float, b: int | float) -> int | float:
    return a + t * (b - a)

def grad(hash: int | float, x: int | float, y: int | float, z: int | float) -> int | float:
    h = hash % 16
    u = x if h < 8 else y
    v = y if h < 4 else (x if h == 12 or h == 14 else z)
    return ((u if h % 2 == 0 else -u) + (v if h % 3 == 0 else -v))

with proto("PerlinNoise") as PerlinNoise:
    @PerlinNoise
    def new(self, size: int = 256) -> None:
        self.size = size
        self.p = []
        self.permutation = list(range(self.size))
        self.shuffle()
        self.loadPermutations()
        return

    @PerlinNoise
    def shuffle(self) -> None:
        seed()
        tInput = self.permutation[:]
        for i in range(len(tInput) - 1, 0, -1):
            j = randint(0, i)
            tInput[i], tInput[j] = tInput[j], tInput[i]
        self.permutation = tInput
        return

    @PerlinNoise
    def loadPermutations(self) -> None:
        self.p = 2 * self.permutation
        return

    @PerlinNoise    
    def noise(self, x: int | float, y: int | float, z: int | float = 0) -> int | float:
        X = floor(x) % self.size
        Y = floor(y) % self.size
        Z = floor(z) % self.size
        x -= floor(x)
        y -= floor(y)
        z -= floor(z)
        
        u = fade(x)
        v = fade(y)
        w = fade(z)
        
        A  = self.p[X] + Y
        AA = self.p[A] + Z
        AB = self.p[A + 1] + Z
        B  = self.p[X + 1] + Y
        BA = self.p[B] + Z
        BB = self.p[B + 1] + Z

        return lerp(w, lerp(v, lerp(u, grad(self.p[AA], x, y, z),
                                       grad(self.p[BA], x - 1, y, z)),
                               lerp(u, grad(self.p[AB], x, y - 1, z),
                                       grad(self.p[BB], x - 1, y - 1, z))),
                       lerp(v, lerp(u, grad(self.p[AB + 1], x, y, z - 1),
                                       grad(self.p[BA + 1], x - 1, y, z - 1)),
                               lerp(u, grad(self.p[AB + 1], x, y - 1, z - 1),
                                       grad(self.p[BB + 1], x - 1, y - 1, z - 1))))