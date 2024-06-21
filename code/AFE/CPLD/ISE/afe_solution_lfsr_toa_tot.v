module afe_solution_lfsr_toa_tot
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

  reg [7:0] tot_reg;
  reg [7:0] toa_reg;
  reg [7:0] gpio_reg;
  reg toa_ce;
  reg hit_reg;
  wire tot_fb;
  wire toa_fb;
  wire reg_clk;
  wire lfsr_rst_b;

  assign LED = 1;
  assign INJ_OUT = INJ_IN;
  assign HIT = hit_reg;
  assign reg_clk = INJ_IN ? CLK : SCLK;  // 
  assign tot_fb  = CS_B ? (tot_reg[0] ^ tot_reg[2] ^ tot_reg[3] ^ tot_reg[4]) : MOSI;
  assign toa_fb  = CS_B ? (toa_reg[0] ^ toa_reg[2] ^ toa_reg[3] ^ toa_reg[4]) : tot_reg[7];
  assign lfsr_rst_b = !(INJ_IN & !INJ_IN_DEL);
  assign MISO = CS_B ? 1'b0 : toa_reg[7];
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
  
    // asyc. toa count enable latch
  always @(posedge INJ_IN_DEL or posedge COMP)
  begin
    if (COMP)
      toa_ce <= 1'b0;
    else
    begin
      toa_ce <= 1;
    end
  end

  // shift register: SPI data or TOT counter (lfsr)
  always @(posedge reg_clk or negedge lfsr_rst_b) 
  begin
    if (!lfsr_rst_b)   
      tot_reg <= 8'b11111111;
    else 
    begin
      if (COMP || !CS_B)
        tot_reg <= {tot_reg[6:0], tot_fb};
    end
  end

  // shift register: SPI data or TOA counter (lfsr)
  always @(posedge reg_clk or negedge lfsr_rst_b) 
  begin
    if (!lfsr_rst_b)   
      toa_reg <= 8'b11111111;
    else 
    begin
      if (toa_ce || !CS_B)
        toa_reg <= {toa_reg[6:0], toa_fb};
    end
  end

  // GPO data latch
  always @(posedge CS_B) 
  begin
    begin
      gpio_reg <= tot_reg;
    end
  end

endmodule