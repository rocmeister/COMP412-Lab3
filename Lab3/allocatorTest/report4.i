//NAME: Yun, Min Hong
//NETID: my12
//SIM INPUT: -i 128 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20
//OUTPUT: 183 164
//
// COMP 412, Lab 1, block "report4.i"
//
// This report block is a slightly altered version of a 
// Lab 1 test block submitted by Min Hong Yun in Fall 2014.
//
//
// Example usage: ./sim -i 128 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 < report4.i
//
loadI	128		=>	r1
loadI	132		=>	r2
loadI	136		=>	r3
loadI	140		=>	r4
loadI	144		=>	r5
loadI	148		=>	r6
loadI	152		=>	r7
loadI	156		=>	r8
loadI	160		=>	r9
loadI	164		=>	r10
loadI	168		=>	r11
loadI	172		=>	r12
loadI	176		=>	r13
loadI	180		=>	r14
loadI	184		=>	r15
loadI	188		=>	r16
loadI	192		=>	r17
loadI	196		=>	r18
loadI	200		=>	r19
loadI	204		=>	r20

load 	r20		=>	r20	// load backward
load 	r19		=>	r19
load 	r18		=>	r18
load 	r17		=>	r17
load 	r16		=>	r16
load 	r15		=>	r15
load 	r14		=>	r14

store 	r10		=>	r13	// make the mem dirty

load 	r13		=>	r13
load 	r12		=>	r12
load 	r11		=>	r11
load 	r10		=>	r10
load 	r9		=>	r9
load 	r8		=>	r8
load 	r7		=>	r7
load 	r6		=>	r6
load 	r5		=>	r5
load 	r4		=>	r4
load 	r3		=>	r3
load 	r2		=>	r2
load 	r1		=>	r1

add		r1,	r2	=> r2 	// sum up
add		r2,	r3	=> r3
add		r3,	r4	=> r4
add		r4,	r5	=> r5
add		r5,	r6	=> r6
add		r6,	r7	=> r7
add		r7,	r8	=> r8
add		r8,	r9	=> r9
add		r9,	r10	=> r10
add		r10, r11 => r11
add		r11, r12 => r12
add		r12, r15 => r15
add		r15, r16 => r16
add		r16, r17 => r17
add		r17, r18 => r18
add		r18, r19 => r19
add		r19, r20 => r20

loadI 	1024		=>  r0
store 	r20			=>  r0

output 1024
output 176
