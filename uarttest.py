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

        base_char = Signal(8, reset=ord('A'))
        count = Signal(range(4))
        paused = Signal()

        timer = Signal(range(int(platform.default_clk_frequency)))
        m.d.sync += timer.eq(timer + 1)
        with m.If(timer[-1] | paused):
            m.d.comb += leds.eq(base_char)

        # Transmit ABCDABCD...
        m.d.comb += uart.tx.data.eq(base_char + count[:2])

        with m.If(uart.tx.rdy):
            with m.If(~paused):
                m.d.comb += uart.tx.ack.eq(1)
                m.d.sync += count.eq(count + 1)

        m.d.comb += uart.rx.ack.eq(1)
        with m.If(uart.rx.rdy):
            with m.Switch(uart.rx.data):
                # Press space to pause/unpause output
                with m.Case(ord(' ')):
                    m.d.sync += paused.eq(~paused)
                # Press anything else to set the base character
                with m.Default():
                    m.d.sync += base_char.eq(uart.rx.data)

        # Output to a specific pin
        pins = [ Pins('109', dir='o') ]
        res = Resource.family(0, default_name='gpio', ios=pins)
        platform.add_resources([res])
        pin = platform.request('gpio', 0)
        m.d.comb += pin.o.eq(uart.tx.o)

        return m
