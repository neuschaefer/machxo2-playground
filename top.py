#!/usr/bin/python3

from amaranth_boards.machxo2_breakout import *
from amaranth_boards.test.blinky import Blinky
from led_runner import LEDRunner
from settings import ssh_settings

p = MachXO2_7000HE_BreakoutPlatform()
plan = p.prepare(LEDRunner(), do_program=False)
prod = plan.execute_remote_ssh(connect_to=ssh_settings, root='/tmp/fpga-build')

p.toolchain_program(prod, 'top')