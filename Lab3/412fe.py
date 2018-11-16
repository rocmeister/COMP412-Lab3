import sys
import getopt
import argparse
import time
import Parser

from Scanner import Scanner
from Parser import Parser


def main():
    #start_time = time.time()
    try:
        opts, args = getopt.getopt(sys.argv[1:], 's:p:r:h')
    except getopt.GetoptError as err:
        print >> sys.stderr, err
        usage()
        sys.exit(2)
    if args:
        if len(args) == 1:
            parse(args[0])
            return
        else:
            print "args", args
            usage()
            sys.exit()

    for o, a in opts:
        o = o[:2]
        if o == '-h':
            usage()
            sys.exit()
        elif o == '-s':
            scan(a)
        elif o == '-p' or not opts:
            parse(a)
        elif o == '-r':
            run(a)
        else:
            usage()
            sys.exit(2)
    #print("--- %s seconds ---" % (time.time() - start_time))

    # cmd_parser = argparse.ArgumentParser(description='COMP 412, Fall 2018 Front End (lab 1)')
    # #cmd_parser.add_argument('-h', action='store_true')
    # cmd_parser.add_argument('-s', "--scan", help='prints tokens in token stream')
    # cmd_parser.add_argument('-p', "--parse", help='invokes parser and reports on success or failure')
    # cmd_parser.add_argument('-r', "--read", help='prints human readable version of parser\'s IR')
    # #cmd_parser.print_usage('python 412fe.py [flags] filename')
    # args = cmd_parser.parse_args()
    # print "I read %s" % args.scan

    # with open('') as f:
    #     lines = f.readlines()
    #     test = Scanner(",")
    #     word = test.next_word()
    #     print "< " + word[0] + ', ' + word[1] + " >"


def scan(filename):
    block = open(filename, "r")
    scanner = Scanner.Scanner(block)
    word = scanner.next_word()
    #print word

    while word != "EoF":
        #print "tokens", scanner.tokens
        if word is not None:
            if word[0] == "invalid":
                lex_error(word)
            else:
                #print >> sys.stdout, str(word[2]) + ": < " + word[0] + ', \"' + word[1] + "\" >"
                print >> sys.stdout, "%i: < %s, \"%s\" >" % (word[2], str(word[0]), word[1])
        #print "tokens", scanner.tokens
        word = scanner.next_word()
    if scanner.lineNo == 0:
        print >> sys.stdout, scanner.lineNo, ': < ENDFILE, \"\" >'
    else:
        print >> sys.stdout, scanner.lineNo - 1, ': < ENDFILE, \"\" >'


def parse(filename):
    parser = Parser.Parser(filename)
    result = parser.parse_file()
    if result[0]:
        if parser.valid_operation == 0:
            print >> sys.stdout, "ERROR: ILOC file contained no valid operations.\n"
            print >> sys.stdout, "ERROR: Terminating."
        else:
            print >> sys.stdout, "Parse succeeded, finding %i ILOC operations." % parser.valid_operation
            #print >> sys.stdout, parser.valid_operation
            parser.print_IR()
    else:
        #print >> sys.stdout, "Parser found %i syntax errors." % result[1]
        print >> sys.stdout, '\nParser found %i syntax errors in %i lines of input.' \
                             % (parser.num_errors, parser.scanner.lineNo - 1)
        #print >> sys.stdout, "Parser found errors."


def run(filename):
    parser = Parser.Parser(filename)
    result = parser.parse_file()
    if result[0]:
        parser.print_IR()
    else:
        print >> sys.stdout, "Due to syntax errors, run terminates."


# stub for helper functions #
def lex_error(word):
    print >> sys.stderr, "Lexical Error: %i: \"%s\" is not a valid word." % (word[2], word[1])


def usage():
    print >> sys.stderr, "COMP 412, Fall 2018 Front End (lab 1)"
    print >> sys.stderr, "Command Syntax:"
    print >> sys.stderr, "      python 412fe.py [flags] filename"
    print >> sys.stderr, "\nRequired arguments:"
    print >> sys.stderr, "       filename is the pathname (absolute or relative) to the input file"
    print >> sys.stderr, "\nOptional flags:"
    print >> sys.stderr, "       -h	 prints this message"
    #print >> sys.stderr, "       -l	 Opens log file \"./Log\" and starts logging."
    print >> sys.stderr, "       -s	 prints tokens in token stream"
    print >> sys.stderr, "       -p	 invokes parser and reports on success or failure"
    print >> sys.stderr, "       -r	 prints human readable version of parser's IR"


if __name__ == "__main__":
    main()
