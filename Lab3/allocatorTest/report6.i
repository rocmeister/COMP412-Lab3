//NAME: Seth Lauer
//NETID: sjl4
//SIM INPUT: -i 2048 0 1 2 3 4 5 6 7 8 9
//OUTPUT: 8 88 888 8888 88888 888888 8888888 88888888 888888888
//
// COMP 412, Lab 1, block "report6.i"
//
// This report block was submitted as a Lab 1 
// test block by Seth Lauer in Fall 2014.
//
//ALGORITHM: Shows 0 * 9 + 8 = 8
//                 9 * 9 + 7 = 88
// 	          98 * 9 + 6 = 888...(continued)

loadI 2048 => r0
loadI 2052 => r1
loadI 2056 => r2
loadI 2060 => r3
loadI 2064 => r4
loadI 2068 => r5
loadI 2072 => r6
loadI 2076 => r7
loadI 2080 => r8
loadI 2084 => r9
loadI 0 => r20
loadI 10 => r21
loadI 9 => r22
loadI 0 => r30
loadI 4 => r29

mult r20, r22 => r40
load r8 => r8
add r40, r8 => r10 

mult r20, r21 => r20
load r9 => r9
add r20, r9 => r20
mult r20, r22 => r41
load r7 => r7
add r41, r7 => r11

mult r20, r21 => r20
add r20, r8 => r20
mult r20, r22 => r42
load r6 => r6
add r42, r6 => r12 

mult r20, r21 => r20
add r20, r7 => r20
mult r20, r22 => r43
load r5 => r5
add r43, r5 => r13 

mult r20, r21 => r20
add r20, r6 => r20
mult r20, r22 => r44
load r4 => r4
add r44, r4 => r14 

mult r20, r21 => r20
add r20, r5 => r20
mult r20, r22 => r45
load r3 => r3
add r45, r3 => r15 

mult r20, r21 => r20
add r20, r4 => r20
mult r20, r22 => r46
load r2 => r2
add r46, r2 => r16 

mult r20, r21 => r20
add r20, r3 => r20
mult r20, r22 => r47
load r1 => r1
add r47, r1 => r17 

mult r20, r21 => r20
add r20, r2 => r20
mult r20, r22 => r48
load r0 => r0
add r48, r0 => r18

add r30, r29 => r31
add r31, r29 => r32
add r32, r29 => r33
add r33, r29 => r34
add r34, r29 => r35
add r35, r29 => r36
add r36, r29 => r37
add r37, r29 => r38
store r10 => r30
store r11 => r31
store r12 => r32
store r13 => r33
store r14 => r34
store r15 => r35
store r16 => r36
store r17 => r37
store r18 => r38
output 0
output 4
output 8
output 12
output 16
output 20
output 24
output 28
output 32
