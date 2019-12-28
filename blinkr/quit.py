from animation import Animation

class Quit(Animation):
    def exec_update(self):
        rgbs = [(0, 0, 0) for _ in range(len(self.pixels))]
        self.pixels[:] = rgbs[:]
        self.pixels.write()
        return 0.0
