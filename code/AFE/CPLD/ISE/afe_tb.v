`timescale 1ns / 1ps

////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer:
//
// Create Date:   14:14:01 02/06/2023
// Design Name:   afe_main
// Module Name:   D:/Users/Hans/Xilinx/AFE/afe_tb.v
// Project Name:  AFE
// Target Device:  
// Tool versions:  
// Description: 
//
// Verilog Test Fixture created by ISE for module: afe_main
//
// Dependencies:
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
////////////////////////////////////////////////////////////////////////////////

`include "afe.v"

module afe_tb;

	// Inputs
	reg MOSI;
	reg CS_B;
	reg SCLK;
	reg INJ;
	reg INJ_DEL;
	reg COMP;
	reg CLK;

	// Outputs
	wire MISO;
	wire HIT;
	wire [7:0] GPIO;
	reg  [7:0] out_data = 8'b00000000;

	initial
	begin
		$dumpfile("afe.vcd");
		$dumpvars(0,SCLK,CS_B,MISO,MOSI);
	end
	
	// Instantiate the Unit Under Test (UUT)
	afe uut (
		.MOSI(MOSI), 
		.MISO(MISO), 
		.CS_B(CS_B), 
		.SCLK(SCLK), 
		.INJ_IN(INJ), 
		//.INJ_IN_DEL(INJ_DEL), 
		.COMP(COMP), 
		.HIT(HIT), 
		.GPIO(GPIO), 
		.LED(LED),
		.CLK(CLK)
	);


	initial 
	begin
		// Initialize Inputs
		MOSI = 0;
		CS_B = 1;
		SCLK = 0;
		INJ = 0;
		INJ_DEL = 0;
		COMP = 0;
		CLK = 0;

		// Wait 10 ns for global reset to finish
		#10;
        
	    forever #12.5 CLK = ~CLK;
	end
	
	
	initial
    begin	
		// SPI transfer
	  	CS_B = 0;
		#50;
		repeat(16)
		begin
			#50 SCLK = ~SCLK;
		end
		CS_B = 1;
		#100; 
	
		// trigger injection
		#70  INJ = 1;	
		#180 INJ_DEL = 1;
		#300 COMP = 1;
		#530 COMP = 0;	    
		
		#100;

		// SPI transfer
		CS_B = 0;
		#50;
		repeat(32)
		begin
			#50 SCLK = ~SCLK;
		end
		CS_B = 1;

		// stop injection
		#70  INJ = 0;	
		#180 INJ_DEL = 0;	

		#100
		
		$finish;
	end	
	
	
	initial
		MOSI = CS_B? 1'b1: out_data[7];
	
	initial
	forever @(posedge SCLK)
		out_data[7:0] <= {out_data[6:0], 1'b0};
	
endmodule	
