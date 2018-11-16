from Parser import Parser


def main():
    print "Parser Driver: "
    #parser = Parser("test.txt")
    parser = Parser("allocatorTest/report1.i")
    parser.parse_file()
    parser.print_IR()


if __name__ == "__main__":
    main()
