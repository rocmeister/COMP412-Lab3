from Scanner import Scanner
import sys


def main():
    block = open("Testfiles/many.i", "r")
    test = Scanner(block)
    word = test.next_word()

    while word != "EoF":
        # print "tokens", test.tokens
        if word is not None:
            if word[0] == "invalid":
                lex_error(word)
            else:
                print >> sys.stdout, str(word[2]) + ": < " + word[0] + ', \"' + word[1] + "\" >"
        #print "tokens", test.tokens
        word = test.next_word()


def lex_error(word):
    print >> sys.stderr, "Lexical Error: %i: \"%s\" is not a valid word." % (word[2], word[1])

    # while word != "EoF":
    #     #print "hey you"
    #     if word[0] == "invalid":
    #         print word
    #     elif word is not None:
    #         print str(word[2]) + ": < " + word[0] + ', \"' + word[1] + "\" >"
    #     word = test.next_word()

    #
    # with open('') as f:
    #     lines = f.readlines()
    #     test = Scanner(",")
    #     word = test.next_word()
    #     print "< " + word[0] + ', ' + word[1] + " >"


if __name__ == "__main__":
    main()
