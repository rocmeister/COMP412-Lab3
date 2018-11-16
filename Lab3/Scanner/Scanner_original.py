from collections import deque
import sys


# A Scanner for ILOC
class Scanner:
    # Initialize the Type table
    def __init__(self, file_obj):
        # File related variables #
        self.file = file_obj
        self.next_line = ""
        self.next_char = ''
        self.line_ptr = -1  # set to -1 because we next_char() immediately
        self.next_line_tokens = 0

        # self.input = 0  # Input
        # self.n = 2048
        # self.buffer = [None] * (2 * self.n - 1)  # buffer is of size 2n
        # self.fill_buffer(0, self.n - 1)  # fill in initial n characters
        # self.fence = 0
        self.EoF = False
        self.lineNo = 0

        # Internal stack that stores the stream of tokens #
        self.tokens = deque()

        # Accepting State Set #
        self.SA = {5, 7, 11, 12, 18, 24, 27, 33, 35, 36, 37, 38}

        # Delta Transition Table #
        self.delta_table = [{} for i in range(39)]
        self.delta_table[0] = {'s': 1, 'l': 8, 'r': 13, 'm': 19, 'a': 22, 'n': 25, 'o': 28, '=': 34, ',': 36,
                               '0': 37, '1': 37, '2': 37, '3': 37, '4': 37, '5': 37, '6': 37, '7': 37,
                               '8': 37, '9': 37}
        self.delta_table[1] = {'t': 2, 'u': 6}
        self.delta_table[2] = {'o': 3}
        self.delta_table[3] = {'r': 4}
        self.delta_table[4] = {'e': 5}
        #self.delta_table[5]
        self.delta_table[6] = {'b': 7}
        #self.delta_table[7]
        self.delta_table[8] = {'o': 9, 's': 14}
        self.delta_table[9] = {'a': 10}
        self.delta_table[10] = {'d': 11}
        self.delta_table[11] = {'I': 12}
        #self.delta_table[12]
        self.delta_table[13] = {'s': 14, '0': 38, '1': 38, '2': 38, '3': 38, '4': 38, '5': 38, '6': 38, '7': 38,
                                '8': 38, '9': 38}
        self.delta_table[14] = {'h': 15}
        self.delta_table[15] = {'i': 16}
        self.delta_table[16] = {'f': 17}
        self.delta_table[17] = {'t': 18}
        #self.delta_table[18]
        self.delta_table[19] = {'u': 20}
        self.delta_table[20] = {'l': 21}
        self.delta_table[21] = {'t': 18}
        self.delta_table[22] = {'d': 23}
        self.delta_table[23] = {'d': 24}
        #self.delta_table[24]
        self.delta_table[25] = {'o': 26}
        self.delta_table[26] = {'p': 27}
        #self.delta_table[27] = {}
        self.delta_table[28] = {'u': 29}
        self.delta_table[29] = {'t': 30}
        self.delta_table[30] = {'p': 31}
        self.delta_table[31] = {'u': 32}
        self.delta_table[32] = {'t': 33}
        #self.delta_table[33]
        self.delta_table[34] = {'>': 35}
        #self.delta_table[35]
        #self.delta_table[36]
        self.delta_table[37] = {'0': 37, '1': 37, '2': 37, '3': 37, '4': 37, '5': 37, '6': 37, '7': 37,
                                '8': 37, '9': 37}
        self.delta_table[38] = {'0': 38, '1': 38, '2': 38, '3': 38, '4': 38, '5': 38, '6': 38, '7': 38,
                                '8': 38, '9': 38}

        # Token Type Table #
        self.Type = ["invalid" for i in range(39)]
        self.Type[5] = "MEMOP"
        self.Type[7] = "ARITHOP"
        self.Type[11] = "MEMOP"
        self.Type[12] = "LOADI"
        self.Type[18] = "ARITHOP"
        self.Type[24] = "ARITHOP"
        self.Type[27] = "NOP"
        self.Type[33] = "OUTPUT"
        self.Type[35] = "INTO"
        self.Type[36] = "COMMA"
        self.Type[37] = "CONST"
        self.Type[38] = "REG"

        # Error State #
        self.se = -1

    # stub for smaller sub-routines
    # def next_char(self):
    #     self.str_pointer += 1
    #     try:
    #         return self.block[self.str_pointer - 1]
    #     except IndexError:
    #         return "$"

    # fill from file[start] to file[end], inclusive
    # def fill_buffer(self, start, end):
    #     assert end - start + 1 <= self.n
    #     block = file.read(end - start + 1)
    #     size = len(block)
    #     if size == end - start + 1:
    #         self.buffer[start: end + 1] = block
    #     else:
    #         self.buffer[start: start + size] = block
    #         self.EoF = True

    # the pointer points at the last white space in this line,
    # WARNING: next_char doesn't get updated here, be careful!
    def clear_whitespace(self):
        while Scanner.iswhitespace(self.peek_char('n')):
            self.line_ptr += 1

    def peek_char(self, flag):
        try:
            if flag == 'n':
                return self.next_line[self.line_ptr + 1]
            elif flag == 'c':
                return self.next_line[self.line_ptr]
        except IndexError:
            return '\n'

    # SET next_char and ADVANCE line_ptr
    def next_character(self):
        self.line_ptr += 1
        try:
            self.next_char = self.next_line[self.line_ptr]
        except IndexError:
            self.next_char = '\n'

    def next_two_are_comment(self):
        try:
            if self.next_line[self.line_ptr + 1] == '/' and self.next_line[self.line_ptr + 2] == '/':
                return True
            else:
                return False
        except IndexError:
            return False

    # def next_char(self):
    #     char = self.buffer[self.input]
    #     self.input = (self.input + 1) % (2 * self.n)
    #
    #     if self.input % self.n == 0:
    #         self.fill_buffer(self.input, self.input + self.n - 1)
    #         self.fence = (self.input + self.n) % (2 * self.n)
    #     return char
    #
    # def rollback(self):
    #     if self.input == self.fence:
    #         print "rollback error!"
    #         raise RuntimeError
    #     self.input = (self.input - 1) % (2 * self.n)

    def delta(self, state, char):
        try:
            return self.delta_table[state][char]
        except:
            return self.se

    # Roll back line_ptr but doesn't update next_char!
    def rollback(self):
        self.line_ptr -= 1
        #self.next_char = self.next_line[self.line_ptr]

    # stub for larger routines
    # move pointer regardless of what the next line is (assuming not EoF)
    # def move_ptr_next_line(self):
    #     self.next_line = next(self.file, "EoF")
        # if self.buffer[self.input] == '\n':
        #     self.input += 1
        # else:
        #     self.input += 1
        #     self.move_ptr_next_line()
        #     # while self.block[self.str_pointer] != '\n':
        #     #     self.str_pointer += 1

    # returns <token, lexeme> if possible,
    def scan_next_word(self):
        state = 0
        lexeme = ""
        stack = ["bad"]

        # check new-line
        #if self.next_char == '\n':
        #if self.next_line[self.line_ptr + 1] == '\n':
        if self.peek_char('n') == '\n':
            self.line_ptr += 1
            #self.lineNo += 1
            return "\n"

        # check comment
        if self.next_two_are_comment():
            #print "comment detected!"
            #self.lineNo += 1
            return "//"

        while state != self.se:
            #print "next char: ", self.next_character()
            self.next_character()
            lexeme += self.next_char

            # print "state: ", state
            # print "next char", self.next_char

            if state in self.SA:
                stack = []
            stack.append(state)

            state = self.delta(state, self.next_char)

        trunc = ""
        while state not in self.SA and state != "bad":
            state = stack.pop()
            #print "lexeme: ", lexeme
            if lexeme:
                trunc = lexeme[-1] + trunc
            lexeme = lexeme[: - 1]
            #lexeme = Scanner.truncate(lexeme)
            #print "pointer", self.line_ptr
            self.rollback()

        if state in self.SA:
            return self.Type[state], lexeme, self.lineNo
        else:
            #Scanner.error("Invalid token!")
            #print "appear once only"
            Scanner.lex_error(trunc, self.lineNo)
            return "invalid", trunc, self.lineNo

    # scans the next available line and store the stream of tokens
    def scan_next_line(self):
        self.next_line = self.file.readline()
        self.lineNo += 1
        self.line_ptr = -1
        self.next_char = ''
        self.next_line_tokens = 0

        # scans the line until 1) reaches \n; 2) finds an invalid lexical error;
        if self.next_line == "":
            self.EoF = True
        else:
            is_eol = Scanner.isEoL(self.peek_char('n'))
            #is_comment = self.next_two_are_comment()
            #print "line", self.next_line
            self.clear_whitespace()
            token = self.scan_next_word()
            #print self.tokens
            #print "POGGERS", token
            # if token[0] == "invalid":
            #     self.tokens.append(token)
            while token[0] != "invalid" and not is_eol and token != "//": #not is_comment:
                #print "ummm"
                #print self.peek_char('n')
                # look ahead and eliminate incoming whitespace
                #while Scanner.iswhitespace(self.peek_char('n')):
                    #print "whitespace"
                    #print 'peek', self.peek_char('n')
                    #print Scanner.iswhitespace(self.peek_char('n'))
                    #self.line_ptr += 1
                    #print "is this",self.line_ptr,"space"
                self.clear_whitespace()
                is_eol = Scanner.isEoL(self.peek_char('n'))
                self.tokens.append(token)
                self.next_line_tokens += 1
                #print self.next_line_tokens
                #print "token: ", token
                #print self.next_line[self.line_ptr:]
                #print "pointer: ", self.line_ptr
                token = self.scan_next_word()
                #print "debug1:", self.tokens

            # if token[0] == "invalid":
            #     self.tokens.append(token)
            #print "debug2:", self.tokens

    # pops the next <token, lexeme> pair or "invalid" from the queue, or EoF,
    # or Nothing if the next line consists of comments, '\n', or whitespaces
    def next_word(self):
        #print self.tokens
        if self.EoF:
            #print "I'd be surprised if this gets triggered!"
            return "EoF"
        elif self.tokens:
            return self.tokens.popleft()
        else:
            self.scan_next_line()
            #print "POG", self.tokens
            if self.EoF:
                return "EoF"
            elif self.tokens:
                #return "EoF" if self.EoF else self.tokens.popleft()
                return self.tokens.popleft()
            # self.next_word()

    # Static Helper Methods #
    @staticmethod
    def truncate(lexeme):
        return lexeme[: - 1]

    @staticmethod
    def error(msg):
        print msg

    @staticmethod
    def iswhitespace(string):
        return True if (string == " " or string == "\t") else False

    @staticmethod
    def isEoL(string):
        return True if string == '\n' else False

    @staticmethod
    def lex_error(word, lineNo):
        print >> sys.stderr, "Lexical Error: %i: \"%s\" is not a valid word." % (lineNo, word)
