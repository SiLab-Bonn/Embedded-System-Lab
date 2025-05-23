`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date:    12:42:32 02/06/2023 
// Design Name: 
// Module Name:    afe_main 
// Project Name: 
// Target Devices: 
// Tool versions: 
// Description: 
//
// Dependencies: 
//
// Revision: 
// Revision 0.01 - File Created
// Additional Comments: 
//
//////////////////////////////////////////////////////////////////////////////////
module afe
(
	input  MOSI,
	output MISO,
	input  CS_B,
	input  SCLK,
	input  INJ_IN,
	input  COMP,
	output HIT,
	output INJ_OUT,
	output[7:0] GPIO,
	input  CLK,
	output LED
);


reg[7:0] sr_in;
reg[7:0] gpio_reg;
reg hit_reg;
wire clk_buf;
wire sclk_buf;
reg[2:0] ptr;

assign MISO = CS_B? 1'b0 : 1'bz;
assign GPIO = gpio_reg;
assign HIT = hit_reg;
assign INJ_OUT = INJ_IN;
assign LED = 1'b1;

BUFG CLK_BUFG_INST (.O(clk_buf), .I(CLK));
BUFG SCLK_BUFG_INST (.O(sclk_buf), .I(SCLK));


always @(posedge sclk_buf or posedge CS_B)
begin
  if (CS_B)  // reset serial output
    begin
    ptr <= 7;
	end
  else
    begin
	sr_in[7:0] <= {sr_in[6:0], MOSI}; // shift in GPIO register
	ptr <= ptr - 1;
    end
end
    
always @(posedge CS_B)	
begin
  gpio_reg <= sr_in;
end

always @(posedge COMP or negedge INJ_IN)
begin
  if (!INJ_IN)
    hit_reg <= 0;
  else
    hit_reg <= 1;
end

  

endmodule
