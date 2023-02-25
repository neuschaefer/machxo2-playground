// Based on tinyfpga.v in nextpnr/machxo2/examples, but adapted for the MachXO2 Breakout board.

module top (
  (* LOC="97" *)
  inout led0
);

  wire clk;

  OSCH #(
    .NOM_FREQ("16.63")
  ) internal_oscillator_inst (
    .STDBY(1'b0),
    .OSC(clk)
  );

  reg [23:0] led_timer;

  always @(posedge clk) begin
    led_timer <= led_timer + 1;
  end

  assign led0 = led_timer[23];
endmodule
