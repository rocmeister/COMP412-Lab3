# Makefile for the COMP 412, Lab 2, code checking tools
CFLAGS=-Wall -O2

tools:	CheckResults AllocOne RunOne

CheckResults:	CheckResults.c
	gcc $(CFLAGS) CheckResults.c
	mv a.out CheckResults

AllocOne:	AllocOne.c
	gcc $(CFLAGS) AllocOne.c
	mv a.out AllocOne

RunOne:		RunOne.c
	gcc $(CFLAGS) RunOne.c
	mv a.out RunOne

export:	Makefile README AllocOne.c CheckResults.c AllocAndRunAll AllocHelper
	tar cvf export.tar Makefile README *.c AllocAndRunAll AllocHelper\
	        RunAll RunAllHelper 

clean:	
	rm -i *~ CheckResults AllocOne RunOne
