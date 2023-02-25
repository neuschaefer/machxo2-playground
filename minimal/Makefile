all: minimal.bit

YOSYS := yosys
NEXTPNR := nextpnr-machxo2
ECPPACK := ecppack

program: minimal.bit
	openFPGALoader -m $<

%.json: %.v
	$(YOSYS) -p "synth_machxo2 -json $@" $<

%.cfg: %.json
	$(NEXTPNR) --7000 --package TQFP144 --json $< --textcfg $@

%.bit: %.cfg
	$(ECPPACK) $< $@
