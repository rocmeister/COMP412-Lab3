from Parser import Parser
from Renamer import Renamer
from Grapher import Grapher


def main():
    filename = "allocatorTest/report1.i"
    parser = Parser.Parser(filename)
    parse_result = parser.parse_file()

    renamer = Renamer.Renamer(parser)
    renamer.rename_sr_2_live_range()

    grapher = Grapher(renamer)
    grapher.print_Graph()


if __name__ == "__main__":
    main()
