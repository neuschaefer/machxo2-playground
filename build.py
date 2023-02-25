#!/usr/bin/python3

import argparse, sys

from settings import ssh_settings

from amaranth_boards.machxo2_breakout import *
from amaranth_boards.test.blinky import Blinky
from amaranth.back import verilog
from led_runner import *

def get_design(name):
    match args.design.lower():
        case 'ledrunner': return LEDRunner()
        case 'boringledrunner': return BoringLEDRunner()
        case 'blinky': return Blinky()
        case _:
            print(f'Unknown design "{name}"')
            sys.exit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MachXO2 build script')
    parser.add_argument('--osch-frequency', default='2.08', help='Internal oscillator frequency')
    parser.add_argument('design', default='ledrunner', nargs='?', help='design name')
    parser.add_argument('--verilog', type=argparse.FileType('w'), help='verilog file to export')
    parser.add_argument('--local', help='run build locally', action='store_true')
    parser.add_argument('--toolchain', help='toolchain to use (Diamond or Trellis)', default='Diamond')
    args = parser.parse_args()

    p = MachXO2_7000HE_BreakoutPlatform(toolchain=args.toolchain)
    p.osch_frequency = float(args.osch_frequency)
    design = get_design(args.design)

    if args.verilog:
        output = verilog.convert(design, 'top', p, ports=())
        args.verilog.write(output)
    else:
        plan = p.prepare(design)
        if args.local:
            prod = plan.execute()
        else:
            prod = plan.execute_remote_ssh(connect_to=ssh_settings, root='/tmp/fpga-build')
        p.toolchain_program(prod, 'top')
