from amaranth import *
from amaranth.build.res import *
import itertools

def get_all_resources(platform, name):
    resources = []
    for number in itertools.count():
        try:
            resources.append(platform.request(name, number))
        except ResourceError:
            break
    return resources

class LEDRunner(Elaboratable):
    cool = True

    def elaborate(self, platform):
        m = Module()

        freq = int(platform.default_clk_frequency)
        timer = Signal(range(freq))
        print(f'timer length {len(timer)}')
        m.d.sync += timer.eq(timer + 1)

        leds = get_all_resources(platform, 'led')

        position0 = Signal(range(len(leds)))
        position = Signal(range(len(leds)))
        invert = Signal()

        m.d.comb += Cat(position0, invert).eq(timer[-len(position0)-1:])
        m.d.comb += position.eq(position0)
        if self.cool:
            with m.If(invert):
                m.d.comb += position.eq(~position0)

        m.d.comb += Cat(leds).eq(1 << position)

        return m

class BoringLEDRunner(LEDRunner):
    cool = False
