#include <stdlib.h>
#include <stdio.h>

#include <ctype.h>
#include <sys/stat.h>
#include <string.h>

int DEBUG = 0;

void FixCRLF( char *s ) {
  char *p = s;
  while (*p != '\0') {
    if (*p =='\r') {
      *p = ' ';
    }
    p++;
  }
}

int main( int argc, char **argv ) {
  char *buffer = NULL;
  char *line;
  char input[256], output[256], command_line[256];
  size_t len = 0;
  int flag, found_input, found_output;
  
  struct stat s_buf; /* for call to stat() */

  if (argc != 3) {
    fprintf(stderr,"Invalid command line input.\n");
    fprintf(stdout,"Valid form is '%s iloc_file sim_path_name'\n",
	    argv[0]);
    exit(-1);
  }
  else {
    if (freopen(argv[1],"r",stdin) == (FILE *) NULL) {
      fprintf(stderr,"Failure to open file '%s'.\n",argv[1]);
      exit(-1);
    }
    flag = stat(argv[2],&s_buf);
    if (flag!= 0) {
      fprintf(stderr,"Invalid path to simulator '%s' (%d).\n",
	      argv[2],flag);
      exit(-1);
    }
      
  }

  /* initializations */
  found_input  = 0;
  found_output = 0;
  
  len = (int) getline(&buffer,&len,stdin);
  while( len != (size_t) -1) {
    buffer[len-1] = '\0';
    FixCRLF(buffer);
    if (DEBUG>1) {
       fprintf(stdout,"-> '%s'.\n",buffer);
    }
    line = buffer;
    if (line[0] == '/' && line[1] == '/') { /* ILOC Comment Line */
      if (DEBUG)
	fprintf(stdout,"** '%s'.\n",buffer);
      line += 2;
      if (strncasecmp(line,"sim input:",(size_t)10) == 0) {
	if (found_input) {
	  fprintf(stderr,"Encountered multiple 'SIM INPUT' comments.\n");
	  fprintf(stderr,"ILOC file is invalid.\n");
	  exit(-1);
	}
	found_input = 1;
	line += 10;
	(void) strncpy(input,line,250);
      }
      else if (strncasecmp(line,"output:",(size_t)7) == 0) {
	if (found_output) {
	  fprintf(stderr,"Encountered multiple 'OUTPUT' comments.\n");
	  fprintf(stderr,"ILOC file is invalid.\n");
	  exit(-1);
	}
	found_output = 1;
	line += 7;
	(void) strncpy(output,line,250);
      }
     }
    len = (int) getline(&buffer,&len,stdin);
    FixCRLF(buffer);
  }
  if (found_input && found_output) {
    fprintf(stdout,"FILE: '%s'\n",argv[1]);
    fprintf(stdout,"INPUT: '%s'\n",input);
    fprintf(stdout,"EXPECTED OUTPUT: '%s'\n\n",output);
    sprintf(command_line,"%s %s <%s\n",argv[2],input,argv[1]);
    if (DEBUG)
      fprintf(stdout,"\nExecuting '%s':\n",command_line);
    fflush(stdout);
    system(command_line);
  }
  else 
    fprintf(stdout,"File '%s' has invalid INPUT or OUTPUT specification.\n",
	    argv[1]);

  return 0;
}
