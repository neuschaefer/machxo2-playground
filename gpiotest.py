from amaranth import *
from amaranth.build.res import *
from amaranth.build.dsl import *
from amaranth.lib.io import *
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


from pprint import pprint

class PinMux(Elaboratable):
    def __init__(self):
        self.i = Signal()
        self.pin = Signal(range(256))
        self.max_pin = Signal(range(256))
        self.pin0 = Signal(range(10))
        self.pin1 = Signal(range(10))
        self.pin2 = Signal(range(10))

    @staticmethod
    def iter_pins(platform):
        for _, x in platform.connectors.items():
            for _, y in x:
                yield int(y)

    def elaborate(self, platform):
        m = Module()
        pin_list = sorted(list(self.iter_pins(platform)))

        res_num = 0
        with m.Switch(self.pin):
            print(pin_list)
            for pin in pin_list:
                with m.Case(int(pin)):
                    try:
                        pins = [ Pins(str(pin), dir='o') ]
                        platform.add_resources([Resource.family(int(pin), default_name='gpio', ios=pins)])
                        res_num += 1
                        p = platform.request('gpio', pin)
                        m.d.comb += p.o.eq(self.i)
                    except ResourceError as e:
                        print(e)

        m.d.sync += self.pin0.eq((self.pin //   1) % 10)  # decimal!
        m.d.sync += self.pin1.eq((self.pin //  10) % 10)
        m.d.sync += self.pin2.eq((self.pin // 100) % 10)

        m.d.comb += self.max_pin.eq(max(pin_list))

        return m

class GPIOTest(Elaboratable):
    """
    My board has a bunch of GPIOs on several connectors. This design aims to
    make it possible to see if I have described them correctly in the platform
    class.
    """

    def __init__(self):
        self.pinmux = PinMux()
        self.uart = AsyncSerialTX(divisor = 42, data_bits=8)

        self.pin = Signal(8)

    def elaborate(self, platform):
        m = Module()
        m.submodules.pinmux = self.pinmux
        m.submodules.uart = uart = self.uart

        self.uart.divisor = int(platform.default_clk_frequency // 115200)

        m.d.comb += self.pinmux.i.eq(self.uart.o)
        m.d.comb += self.pinmux.pin.eq(self.pin)

        # State machine:
        # Iterate over pins
        #   Count 0-5:
        #     print a character, wait for completion

        step = Signal(range(6))
        next_pin = Signal.like(self.pin)

        sequence = [
            uart.data.eq(ord('J')),
            uart.data.eq(ord('0') + self.pinmux.pin2),
            uart.data.eq(ord('0') + self.pinmux.pin1),
            uart.data.eq(ord('0') + self.pinmux.pin0),
            uart.data.eq(ord('\r')),
            uart.data.eq(ord('\n')),
        ]

        with m.Switch(step):
            for i, op in enumerate(sequence):
                with m.Case(i):
                    m.d.comb += op

        with m.If(uart.rdy):
            m.d.comb += uart.ack.eq(1)
            with m.If(step < len(sequence) - 1):
                m.d.sync += step.eq(step + 1)
            with m.Else():
                m.d.sync += step.eq(0)
                m.d.sync += self.pin.eq(next_pin)

        with m.If(self.pin < self.pinmux.max_pin):
            m.d.comb += next_pin.eq(self.pin + 1)
        with m.Else():
            m.d.comb += next_pin.eq(0)

        leds = Cat(get_all_resources(platform, 'led'))
        m.d.comb += leds.eq(step)

        return m
