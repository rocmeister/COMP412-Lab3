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

char *extract_quoted_string( char *in ) {
  char *first, *last;

  first = in;
  while (*first != '\'') 
    first++;

  first++;

  last = first;
  while (*last != '\'') 
    last++;

  *last = '\0';

  return first;
}

char *next_number_from_string( char *s, int *result, char *tag ) {
  int r, neg;

  if (DEBUG>1)
    fprintf(stderr,"NextNumberFromString( '%s', *, '%s' )",s,tag);
  r = 0;
  while(*s == ' ')
    s++;

  if (*s == '\0')
    *result = 0xFEFEFEFE;
  else {
    if (*s == '-') {
      neg = -1;
      s++;
    }
    else
      neg = 1;
    
    while('0' <= *s && *s <= '9') {
      r = 10 * r + (int) (*s - '0');
      s++;
    }
    *result = r;
  }

  if (DEBUG>1)
    fprintf(stderr," returns %d with string '%s'.\n",*result,s);
  return s;
}

int main( int argc, char **argv ) {
  char *buffer = NULL, *data_line = NULL;
  char fname[256],input_spec[256],output_spec[256];
  size_t b_len = 0;
  size_t d_len = 0;
  char *p, *q;
  int delimiter, expected, actual, value, correct;
  int insts, ops, cycles;

  if (argc != 2) {
    fprintf(stderr,"Invalid command line input.\n");
    fprintf(stdout,"Valid form is '%s log_file'\n",
	    argv[0]);
    exit(-1);
  }
  else {
    if (freopen(argv[1],"r",stdin) == (FILE *) NULL) {
      fprintf(stderr,"Failure to open log file '%s'.\n",argv[1]);
      exit(-1);
    }
  }
  /* initializations */
  
  b_len = (int) getline(&buffer,&b_len,stdin);
  buffer[b_len-1] = '\0';
  FixCRLF(buffer);
  while( b_len != (size_t) -1) {

    if (DEBUG>0) {
       fprintf(stdout,"-> '%s'.\n",buffer);
    }

    delimiter = 0;
    while (delimiter == 0 && b_len != (size_t) -1) {
      if (strncmp(buffer,"-----",5) == 0) 
	delimiter = 1;
      b_len = (int) getline(&buffer,&b_len,stdin);
      buffer[b_len-1] = '\0';
      FixCRLF(buffer);
    }

    if (b_len != (size_t) -1) {
      if (delimiter) {
	/* 1st line is file name */
	if (strncmp(buffer,"FILE:",5) != 0) {
	  if (strncmp(buffer,"File",4) == 0) {
	    fprintf(stdout,"ERROR: %s\n",buffer);

	    /* skip the rest of this iteration */
	    b_len = (int) getline(&buffer,&b_len,stdin);
	    buffer[b_len-1] = '\0';
	    FixCRLF(buffer);
	    continue;
	  }
	  else {
	    fprintf(stderr,"\n Format error in log file.\n");
	    fprintf(stderr," Offending line is '%s'.\n",buffer);
	    exit(-1);
	  }
	}
	
	/* pull out the file name */
	p = extract_quoted_string(buffer);
	strcpy(fname,p);
	if (DEBUG > 1)
	  fprintf(stdout,"Found file '%s'\n",fname);
      }

      b_len = (int) getline(&buffer,&b_len,stdin);
      buffer[b_len-1] = '\0';
      FixCRLF(buffer);
      
      /* 2nd line is INPUT spec */
      if (strncmp(buffer,"INPUT:",6) != 0) {    
	fprintf(stderr,"\n Format error in log file.\n");
	fprintf(stderr," Offending line is '%s'.\n",buffer);
	exit(-1);
      }

      p = extract_quoted_string(buffer);
      strcpy(input_spec,p);
      if (DEBUG > 1)
	fprintf(stdout,"Found input spec '%s'\n",input_spec);

      b_len = (int) getline(&buffer,&b_len,stdin);
      buffer[b_len-1] = '\0';
      FixCRLF(buffer);
      
      /* 3rd line is OUTPUT spec */
      if (strncmp(buffer,"EXPECTED OUTPUT:",16) != 0) {
	fprintf(stderr,"\n Format error in log file.\n");
	fprintf(stderr," Offending line is '%s'.\n",buffer);
	exit(-1);
      }

      p = extract_quoted_string(buffer);
      strcpy(output_spec,p);
      if (DEBUG > 1)
	fprintf(stdout,"Found output spec '%s'\n",output_spec);

      /* read blank line */
      b_len = (int) getline(&buffer,&b_len,stdin);
      buffer[b_len-1] = '\0'; 
      FixCRLF(buffer);

      p = next_number_from_string(p,&expected,"source");
      value = 1;
      correct = 1;
      /* 0xFEFEFEFE is an improbable large negative number */
      /* This is a cheap hack to avoid a more complex interface */
      while (expected != 0xFEFEFEFE ) {
	if (DEBUG>1)
	  fprintf(stdout,"--> next expected value is %d\n",expected);

	d_len = (int) getline(&data_line,&d_len,stdin);
	data_line[d_len-1] = '\0';
	FixCRLF(data_line);
	while(strncmp(data_line,"ERROR:",6) == 0) {
	  d_len = (int) getline(&data_line,&d_len,stdin);
	  data_line[d_len-1] = '\0';
	  FixCRLF(data_line);
	}
	  
	q = data_line;
	q = next_number_from_string(q,&actual,"results");
	if (actual != expected) {
	  fprintf(stdout,
		  "In program '%s', value number %d differs from the spec (%d vs %d).\n",
		  fname,value,expected,actual);
	  correct = 0;
	}

	p = next_number_from_string(p,&expected,"bottom of loop");
	value++;
	if (DEBUG>1)
	  fprintf(stderr,"\n");
      }
      if (correct) {
	cycles = 0;
	b_len = (int) getline(&buffer,&b_len,stdin);
	buffer[b_len-1] = '\0';	
	FixCRLF(buffer);

	while(strncmp(buffer,"-----",5) != 0) {
	  if (strncmp(buffer,"Executed",8) == 0) {
	    value = sscanf(buffer,
			   "Executed %d instructions and %d operations in %d cycles.",
			   &insts,&ops,&cycles);
	    break;
	  }
	  b_len = (int) getline(&buffer,&b_len,stdin);
	  buffer[b_len-1] = '\0';	
	  FixCRLF(buffer);
	}
	if (strlen(fname) > 5)
	  fprintf(stdout,"Program '%s'\tcorrectly executed %d cycles\n",fname,cycles);
	else
	  fprintf(stdout,"Program '%s'\t\tcorrectly executed %d cycles\n",fname,cycles);
      }
    }
  }
  return 0;
}
