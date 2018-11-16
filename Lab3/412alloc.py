import sys
import getopt

from Parser import Parser
from Renamer import Renamer
from Allocator import AllocatorWithSpill
from Allocator import AllocatorWithoutSpill


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'x:h')
    except getopt.GetoptError as err:
        print >> sys.stderr, err
        usage()
        sys.exit(2)

    if sys.argv[1].isdigit():
        if int(sys.argv[1]) > 64 or int(sys.argv[1]) < 3:
            print >> sys.stderr, "ERROR: k must be an integer between 3 and 64."
        else:
            allocate(sys.argv[2], int(sys.argv[1]))
    else:
        for o, a in opts:
            if o == '-x':
                rename(a)
            elif o == '-h':
                usage()
                sys.exit()
            else:
                usage()
                sys.exit(2)


def allocate(filename, k):
    parser = Parser.Parser(filename)
    result = parser.parse_file()

    if result[0]:
        if parser.valid_operation == 0:
            print >> sys.stdout, "ERROR: ILOC file contained no valid operations.\n"
            print >> sys.stdout, "ERROR: Terminating."
        else:
            # core of this allocate routine
            renamer = Renamer.Renamer(parser)
            renamer.rename_sr_2_live_range()

            allocator = AllocatorWithSpill.AllocatorWithSpill(renamer, k)
            allocator.allocate_with_spill()
            allocator.print_allocated_block()
            # decide whether to reserve the last pr for spill and restore
            # by evaluating MAXLIVE > k
            # if renamer.max_live > k:
            #     allocator = AllocatorWithSpill.AllocatorWithSpill(renamer, k)
            #     allocator.allocate_with_spill()
            #     allocator.print_allocated_block()
            # else:
            #     allocator = AllocatorWithoutSpill.AllocatorWithoutSpill(renamer, k)
            #     allocator.allocate_without_spill()
            #     allocator.print_allocated_block()
    else:
        print >> sys.stdout, '\nParser found %i syntax errors in %i lines of input.' \
                             % (parser.num_errors, parser.scanner.lineNo - 1)


def rename(filename):
    parser = Parser.Parser(filename)
    result = parser.parse_file()

    if result[0]:
        if parser.valid_operation == 0:
            print >> sys.stdout, "ERROR: ILOC file contained no valid operations.\n"
            print >> sys.stdout, "ERROR: Terminating."
        else:
            # core of this routine
            renamer = Renamer.Renamer(parser)
            renamer.rename_sr_2_live_range()
            renamer.print_renamed_block()
    else:
        print >> sys.stdout, '\nParser found %i syntax errors in %i lines of input.' \
                             % (parser.num_errors, parser.scanner.lineNo - 1)


def usage():
    print >> sys.stderr, "COMP 412, Fall 2018 Local Register Allocation (Lab 2)"
    print >> sys.stderr, "Command Syntax:"
    print >> sys.stderr, "      412alloc k filename [-h] [-x]"
    print >> sys.stderr, "\nRequired arguments:"
    print >> sys.stderr, "       k        specifies the number of register available"
    print >> sys.stderr, "       filename the pathname (absolute or relative) to the input file"
    print >> sys.stderr, "\nOptional flags:"
    print >> sys.stderr, "       -h        prints this message"
    print >> sys.stderr, "       -x        peforms register renaming"


if __name__ == "__main__":
    main()