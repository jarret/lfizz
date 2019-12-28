from blinkr.animation import Animation


class Rainbow(Animation):
    def __init__(self, pixels):
        super().__init__(pixels)
        self.state = {'positions': [p for p in range(len(pixels))]}

    def exec_update(self):
        state['positions'] = [Animation.mod256(p + 5) for p in
                              self.state['positions']]
        rgbs = [Animation.wheel(p) for p in self.state['positions']]
        pixels[:] = rgbs[:]
        pixels.write()
        return 0.01
