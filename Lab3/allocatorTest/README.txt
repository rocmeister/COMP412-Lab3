//NAME: Luoqi Wu
//NETID: lw31

Direction for building and invoking my program:

To run the program, uncompress the tar file then run the shell script 412alloc.
For example, typing "./412alloc 5 ~comp412/students/lab2/report/report1.i" will perform local register allocation.

Currently this program runs correctly on all provided report files and block files (i.e. report1.i - report7.i and block1.i - block12.i).

All command-line options:
       -h                        prints the help message
       -x [filename]             renames the ILOC block into an equivalent file
       k [filename]              performs local register allocation for the file spcified by filename
       otherwise display the help message