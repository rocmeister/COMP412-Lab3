from Scanner import Scanner
from IR import IR
from IR.DoublyLinkedList import DoublyLinkedList
import sys


# A Parser for ILOC
class Parser:
    def __init__(self, filename):
        self.file_obj = open(filename, "r")
        self.scanner = Scanner.Scanner(self.file_obj)
        self.IR = IR.IR()
        self.new_record = DoublyLinkedList()
        self.result = False
        self.num_errors = 0
        self.valid_operation = 0
        self.max_sr = 0
        self.is_store = False
        #self.sr_set = set([])

    # def parse_file(self):
    #     result = self.parse_line()

    # Parse the file and build the IR in the process, returns True if its syntax is valid, False otherwise
    def parse_file(self):
        #result = False
        self.valid_operation = 0
        word = self.next_token()
        while word != "EoF":
            # print self.valid_operation
            self.new_record = DoublyLinkedList()
            self.new_record.write(0, word[1])  # store the opcode instruction
            #self.new_record.write(13, word[2])  # store the line number, CHANGED TO INDEX!!!
            # print "line NO:" , self.scanner.lineNo
            # print "word is", word
            # print "line contains", self.scanner.tokens
            if word[0] == "MEMOP":
                self.is_store = word[1] == "store"
                self.finish_memop()
            elif word[0] == "LOADI":
                self.finish_loadI()
            elif word[0] == "ARITHOP":
                self.finish_arithop()
            elif word[0] == "OUTPUT":
                self.finish_output()
            elif word[0] == "NOP":
                self.finish_nop()
            else:
                self.parser_error("Operation starts with an invalid opcode: %s." % word[1])
                self.num_errors += 1
            # print "line contains", self.scanner.tokens
            # write the operation index
            self.new_record.write(13, self.valid_operation - 1)
            self.IR.add_list(self.new_record)
            self.flush_current_line()
            word = self.next_token()
            # print "word is", word
        self.file_obj.close()
        if self.num_errors == 0:
            self.result = True
        return self.result, self.num_errors

    def update_max_sr(self, candidate):
            self.max_sr = max(self.max_sr, candidate)

    def print_IR(self):
        self.IR.print_me()

    # Returns the next token from the scanner queue, if the queue is empty and we have not reached EoF, we query
    # the queue again
    def next_token(self):
        word = self.scanner.next_word()
        while word is None:
            word = self.scanner.next_word()
        return word

    # returns the next token if the scanner queue is not empty, otherwise report "EOL"
    def try_next_token(self):
        if self.scanner.tokens and not self.scanner.EoF:
            return self.scanner.next_word()
        else:
            return "EOL"

    # flushes out the rest of current line's tokens
    def flush_current_line(self):
        while self.scanner.tokens:
            self.scanner.tokens.popleft()
            #print "flush debug", word

        # while self.try_next_token() != "EOL":
        #     word = self.scanner.next_word()
        #     print "flush debug", word
            #self.scanner.next_word()

    # Stub for parse_line sub-routines #
    def finish_memop(self):
        result = False
        #print "tokens:", self.scanner.tokens
        #print "memop number: ", self.scanner.next_line_tokens

        # if self.scanner.next_line_tokens != 4:
        #     self.parser_error("Wrong number of tokens for MEMOP operation!")
        #     self.num_errors += 1
        #     return result
        # if self.scanner.next_line_tokens < 4:
        #     self.parser_error('Operation on this line is incomplete.', self.scanner.lineNo)
        #     self.num_errors += 1
        #     return result

        word = self.try_next_token()
        if word[0] == "REG":
            self.new_record.write(1, word[1])
            self.update_max_sr(word[1])
            #self.sr_set.add(word[1])
            word = self.try_next_token()
            if word[0] == "INTO":
                word = self.try_next_token()
                if word[0] == "REG":
                    if self.is_store:
                        self.new_record.write(5, word[1])
                    else:
                        self.new_record.write(9, word[1])
                    self.update_max_sr(word[1])
                    #self.sr_set.add(word[1])
                    #result = True
                    #self.valid_operation += 1
                    if not self.scanner.tokens:
                        result = True
                        self.valid_operation += 1
                    else:
                        self.parser_error("More tokens than expected for MEMOP")
                else:
                    self.parser_error("Wrong token type - expected %s" % "REG")
            else:
                self.parser_error("Wrong token type - expected %s" % "INTO")
        else:
            self.parser_error("Wrong token type - expected %s" % "REG")
        if self.incomplete(4):
            result = False
        if not result:
            #self.parser_error("MEMOP parsing error!")
            self.num_errors += 1
        return result

    def finish_loadI(self):
        result = False
        word = self.try_next_token()
        if word[0] == "CONST":
            self.new_record.write(1, word[1])
            word = self.try_next_token()
            if word[0] == "INTO":
                word = self.try_next_token()
                if word[0] == "REG":
                    self.new_record.write(9, word[1])
                    self.update_max_sr(word[1])
                    #self.sr_set.add(word[1])
                    if not self.scanner.tokens:
                        result = True
                        self.valid_operation += 1
                    else:
                        self.parser_error("More tokens than expected for LOADI")
                else:
                    self.parser_error("Wrong token type - expected %s" % "REG")
            else:
                self.parser_error("Wrong token type - expected %s" % "INTO")
        else:
            self.parser_error("Wrong token type - expected %s" % "CONST")
        if self.incomplete(4):
            result = False
        # if self.scanner.next_line_tokens != 4:
        #     self.parser_error("Wrong number of tokens for LOADI operation!")
        #     self.num_errors += 1
        #     result = False
        #     return result
        if not result:
            #self.parser_error("LOADI parsing error!")
            self.num_errors += 1
        return result

    def finish_arithop(self):
        result = False
        word = self.try_next_token()
        # if self.scanner.next_line_tokens != 6:
        #     self.parser_error("Wrong number of tokens for ARITHOP operation!")
        #     self.num_errors += 1
        #     result = False
        #     return result

        if word[0] == "REG":
            self.new_record.write(1, word[1])
            self.update_max_sr(word[1])
            #self.sr_set.add(word[1])
            word = self.try_next_token()
            if word[0] == "COMMA":
                word = self.try_next_token()
                if word[0] == "REG":
                    self.new_record.write(5, word[1])
                    self.update_max_sr(word[1])
                    #self.sr_set.add(word[1])
                    word = self.try_next_token()
                    if word[0] == "INTO":
                        word = self.try_next_token()
                        if word[0] == "REG":
                            self.new_record.write(9, word[1])
                            self.update_max_sr(word[1])
                            #self.sr_set.add(word[1])
                            if not self.scanner.tokens:
                                result = True
                                self.valid_operation += 1
                            else:
                                self.parser_error("More tokens than expected for ARITHOP")
                        else:
                            self.parser_error("Wrong token type - expected %s" % "REG")
                    else:
                        self.parser_error("Wrong token type - expected %s" % "INTO")
                else:
                    self.parser_error("Wrong token type - expected %s" % "REG")
            else:
                self.parser_error("Wrong token type - expected %s" % "COMMA")
        else:
            self.parser_error("Wrong token type - expected %s" % "REG")
        if self.incomplete(6):
            result = False
        if not result:
            #self.parser_error("ARITHOP parsing error!")
            self.num_errors += 1
        return result

    def finish_output(self):
        result = False
        word = self.try_next_token()
        # if self.scanner.next_line_tokens != 2:
        #     self.parser_error("Wrong number of tokens for OUTPUT operation!")
        #     self.num_errors += 1
        #     return result
        if word[0] == "CONST":
            self.new_record.write(1, word[1])
            if not self.scanner.tokens:
                result = True
                self.valid_operation += 1
            else:
                self.parser_error("More tokens than expected for OUTPUT")
        else:
            self.parser_error("Wrong token type - expected %s" % "CONST")
        if self.incomplete(2):
            result = False
        if not result:
            #self.parser_error("OUTPUT parsing error!")
            self.num_errors += 1
        return result

    def finish_nop(self):
        result = False
        # if self.scanner.next_line_tokens != 1:
        #     self.parser_error("Wrong number of tokens for NOP operation!")
        #     self.num_errors += 1
        #     return result
        #result = True
        # if not self.scanner.tokens:
        #     result = True
        #     self.valid_operation += 1
        # else:
        #     self.parser_error("More tokens than expected for NOP")
        result = True
        self.valid_operation += 1
        if self.incomplete(1):
            result = False
        if not result:
            self.parser_error("NOP parsing error!")
            self.num_errors += 1
        #self.valid_operation += 1
        return result

    def incomplete(self, num_tokens):
        result = False
        if self.scanner.next_line_tokens < num_tokens:
            self.parser_error('Operation on this line is incomplete, due to not enough tokens or lexical errors')
            #self.num_errors += 1
            result = True
        return result

    def parser_error(self, msg):
        print >> sys.stderr, 'ERROR: %i: %s' % (self.scanner.lineNo, msg)
