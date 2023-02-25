from amaranth import *
from amaranth.lib.io import Pin
from amaranth.build.res import ResourceError
from amaranth.build.dsl import *
from amaranth_stdio.serial import *

def get_all_resources(platform, name):
    import itertools
    resources = []
    for number in itertools.count():
        try:
            resources.append(platform.request(name, number))
        except ResourceError:
            break
    return resources

class UARTTest(Elaboratable):

    def elaborate(self, platform):
        m = Module()

        leds = Cat(get_all_resources(platform, 'led'))

        divisor = int(platform.default_clk_frequency // 115200)
        m.submodules.uart = uart = AsyncSerial(divisor=divisor, data_bits=8, pins=platform.request('uart'))

        count = Signal(range(int(platform.default_clk_frequency)))
        m.d.comb += leds.eq(count[-len(leds):])

        # Transmit ABCDABCD...
        m.d.comb += uart.tx.data.eq(ord('A') + count[:2])

        with m.If(uart.tx.rdy):
            m.d.sync += uart.tx.ack.eq(1)
            m.d.sync += count.eq(count + 1)

        # Output to a specific pin
        pins = [ Pins('109', dir='o') ]
        res = Resource.family(0, default_name='gpio', ios=pins)
        platform.add_resources([res])
        pin = platform.request('gpio', 0)
        m.d.comb += pin.o.eq(uart.tx.o)

        return m
