//NAME: Nicholas Hanson-Holtry
//NETID: nbh2
//SIM INPUT: 
//OUTPUT: 1 4 27 256 3125

// COMP 412, Lab 1, block "report5.i"
//
// This report block was submitted as a Lab 1 test
// block by Nicholas Hanson-Holtry in Fall 2014.
//
// Output Explanation: Compute n^n for n=1 through n=5.
//
// Allocator Test Goal: The allocator needs to be able
// to recognize when it can rematerialize a value with the
// immediate value it came from (ie, r1 through r5), and
// when doing so isn't valid and it must instead spill the
// calculated value to memory (ie, r22 through r25).
//
// Example Usage: ./sim < report5.i

// the values of n
loadI 1 => r1
loadI 2 => r2
loadI 3 => r3
loadI 4 => r4
loadI 5 => r5

// multiply by n, for values > 1
mult r2 , r2 => r22
mult r3 , r3 => r23
mult r4 , r4 => r24
mult r5 , r5 => r25

// multiply by n, for values > 2
mult r3 , r23 => r23
mult r4 , r24 => r24
mult r5 , r25 => r25

// multiply by n, for values > 3
mult r4 , r24 => r24
mult r5 , r25 => r25

// multiply by n, for values > 4
mult r5 , r25 => r25

// the memory locations to store into
loadI 1000 => r11
loadI 1004 => r12
loadI 1008 => r13
loadI 1012 => r14
loadI 1016 => r15

// write the final values out to memory
store r1  => r11 // r1 never moved to r21
store r22 => r12
store r23 => r13
store r24 => r14
store r25 => r15

// output the results
output 1000
output 1004
output 1008
output 1012
output 1016
