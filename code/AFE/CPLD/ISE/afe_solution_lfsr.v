module afe_solution_lfsr
(
	input  MOSI,
	output MISO,
	input  CS_B,
	input  SCLK,
	input  INJ_IN,
	input  INJ_IN_DEL,
	input  COMP,
	output HIT,
	output INJ_OUT,
	output[7:0] GPIO,
	input  CLK,
	output LED
);  

  reg [7:0] lfsr_reg;
  reg [7:0] gpio_reg;
  reg hit_reg;
  wire feedback;
  wire reg_clk;
  wire lfsr_reset_b;

  assign LED = 1;
  assign INJ_OUT = INJ_IN;
  assign HIT = hit_reg;
  assign reg_clk = INJ_IN ? CLK : SCLK;  // 
  assign feedback  = CS_B ? (lfsr_reg[0] ^ lfsr_reg[2] ^ lfsr_reg[3] ^ lfsr_reg[4]) : MOSI;
  assign lfsr_rst_b = !(INJ_IN && !INJ_IN_DEL);
  assign MISO = CS_B ? 1'b0 : lfsr_reg[7];
  assign GPIO = gpio_reg;

  // asyc. hit latch
  always @(posedge COMP or negedge INJ_IN)
  begin
    if (!INJ_IN)
      hit_reg <= 1'b0;
    else
    begin
      hit_reg <= 1;
    end
  end

  // shit register: SPI data or TOT counter (lfsr)
  always @(posedge reg_clk or negedge lfsr_rst_b) 
  begin
    if (!lfsr_rst_b)   
      lfsr_reg <= 8'b11111111;
    else 
    begin
      if (COMP || !CS_B)
        lfsr_reg <= {lfsr_reg[6:0], feedback};
    end
  end

  // GPO data latch
  always @(posedge CS_B) 
  begin
    begin
      gpio_reg <= lfsr_reg;
    end
  end

endmodule