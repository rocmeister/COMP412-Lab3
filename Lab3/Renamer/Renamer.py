import Scanner
import Parser
from IR import IR
import sys


# Only use Renamer if the parser has finished parsing the file!!!
class Renamer:
    def __init__(self, parser):
        self.OPS = parser.IR.queue
        self.n = parser.valid_operation - 1
        self.IR = parser.IR
        self.max_sr = parser.max_sr
        self.sr_to_vr = ["invalid" for i in range(self.max_sr + 1)]
        self.lu = [float('inf') for j in range(self.max_sr + 1)]
        self.max_live = 0
        #self.sr_set = parser.sr_set

        self.vr_name = 0

        #define MACROs
        self.OPCODE = 0
        self.OP3SR = 9
        self.OP3VR = 10
        self.OP3NU = 12

        #set of opcodes
        self.OP1_is_reg = {"load", "store", "add", "sub", "mult", "lshift", "rshift"}
        self.OP2_is_reg = {"add", "sub", "mult", "lshift", "rshift", "store"}

        # OPCODE Type Dictionary
        self.Type = {"load": "MEMOP", "store": "MEMOP", "loadI": "LOADI", "add": "ARITHOP", "sub": "ARITHOP",
                     "mult": "ARITHOP", "lshift": "ARITHOP", "rshift": "ARITHOP", "output": "OUTPUT", "nop": "NOP"}

    def rename_sr_2_live_range(self):
        #self.renamed = self.OPS
        #return self.renamed
        #OPS[i] = ("Opcode", "SR", "VR", "PR", "NU", "SR", "VR", "PR", "NU", "SR", "VR", "PR", "NU", "LN")

        for i in range(self.n, -1, -1):
            # update MAXLIVE
            live_count = (self.max_sr + 1) - self.sr_to_vr.count("invalid")
            if live_count > self.max_live:
                self.max_live = live_count

            #print "renaming...i is", i
            # handle the def
            if self.OPS[i].record[self.OP3SR] is not None:
                if self.sr_to_vr[self.OPS[i].record[self.OP3SR]] == "invalid":
                    self.sr_to_vr[self.OPS[i].record[self.OP3SR]] = self.vr_name
                    self.vr_name += 1
                self.OPS[i].record[self.OP3VR] = self.sr_to_vr[self.OPS[i].record[self.OP3SR]]
                self.OPS[i].record[self.OP3NU] = self.lu[self.OPS[i].record[self.OP3SR]]

                # kill OP3
                self.sr_to_vr[self.OPS[i].record[self.OP3SR]] = "invalid"
                self.lu[self.OPS[i].record[self.OP3SR]] = float('inf')

            # handle the uses
            if self.OPS[i].record[self.OPCODE] in self.OP1_is_reg:
                self.update(1, i)
            if self.OPS[i].record[self.OPCODE] in self.OP2_is_reg:
                self.update(2, i)

    def update(self, op_num, index):
        op_sr = (op_num - 1) * 4 + 1
        op_vr = (op_num - 1) * 4 + 2
        op_nu = (op_num - 1) * 4 + 4

        # SR has no VR
        if self.sr_to_vr[self.OPS[index].record[op_sr]] == "invalid":
            self.sr_to_vr[self.OPS[index].record[op_sr]] = self.vr_name
            self.vr_name += 1

        self.OPS[index].record[op_vr] = self.sr_to_vr[self.OPS[index].record[op_sr]]
        self.OPS[index].record[op_nu] = self.lu[self.OPS[index].record[op_sr]]
        self.lu[self.OPS[index].record[op_sr]] = index

    def print_renamed_block(self):
        while self.OPS:
            dl_list = self.OPS.pop(0)
            if self.Type[dl_list.record[0]] == "MEMOP":
                if dl_list.record[0] == "store":
                    print >> sys.stdout, "%s  r%i    =>  r%i" % (dl_list.record[0], dl_list.record[2], dl_list.record[6])
                else:
                    print >> sys.stdout, "%s  r%i    =>  r%i" % (dl_list.record[0], dl_list.record[2], dl_list.record[10])
            elif self.Type[dl_list.record[0]] == "LOADI":
                print >> sys.stdout, "%s  %i    =>  r%i" % (dl_list.record[0], dl_list.record[1], dl_list.record[10])
            elif self.Type[dl_list.record[0]] == "ARITHOP":
                print >> sys.stdout, "%s  r%i, r%i    =>  r%i" \
                                     % (dl_list.record[0], dl_list.record[2], dl_list.record[6], dl_list.record[10])
            elif self.Type[dl_list.record[0]] == "OUTPUT":
                print >> sys.stdout, "%s  %i" % (dl_list.record[0], dl_list.record[1])
            #print dl_list.record
        #self.parser.IR.pretty_printer()
