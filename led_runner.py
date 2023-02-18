from amaranth import *
from amaranth.build.res import *
import itertools

class LEDRunner(Elaboratable):

    def elaborate(self, platform):

        def get_all_resources(name):
            resources = []
            for number in itertools.count():
                try:
                    resources.append(platform.request(name, number))
                except ResourceError:
                    break
            return resources

        m = Module()

        half_freq = int(platform.default_clk_frequency)
        timer = Signal(range(half_freq + 1))
        print(f'timer length is {len(timer)=}')
        m.d.sync += timer.eq(timer + 1)

        leds = get_all_resources('led')

        position0 = Signal(range(len(leds)))
        invert = Signal()
        position = Signal(range(len(leds)))
        with m.If(invert):
            m.d.comb += position.eq(position0)
        with m.Else():
            m.d.comb += position.eq(~position0)

        m.d.comb += Cat(position0, invert).eq(timer[-len(position)-1:])
        m.d.comb += Cat(leds).eq(1 << position)

        return m
