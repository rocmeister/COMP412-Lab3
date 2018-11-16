from IR import DoublyLinkedList
import sys


# Allocator that reserves one register to hold the spill address, given MAXLIVE <= k
class AllocatorWithoutSpill:
    # renamer: the renamer instance that translate the sr numbers into vr numbers
    # pr_num: the max number of PRs
    def __init__(self, renamer, pr_num):
        self.renamer = renamer
        self.max_vr_num = self.renamer.vr_name - 1
        self.max_pr_num = pr_num - 1  # pr: 0, 1,..., max_pr_num
        self.vr2pr = ["invalid" for i in range(self.max_vr_num + 1)]
        #print self.max_vr_num
        self.pr2vr = ["invalid" for j in range(self.max_pr_num + 1)]  # pr: 0, 1, ..., max_pr_num
        self.pr_nu = [float('inf') for k in range(self.max_pr_num + 1)]
        self.available_prs = []
        for pr in range(0, self.max_pr_num + 1):
            self.available_prs.append(pr)

        # for simplicity sake
        self.IR = renamer.IR
        self.OPS = self.IR.queue

        # define MACROs
        self.OPCODE = 0
        self.OP1SR = 1
        self.OP1VR = 2
        self.OP1PR = 3
        self.OP1NU = 4
        self.OP2SR = 5
        self.OP2VR = 6
        self.OP2PR = 7
        self.OP2NU = 8
        self.OP3SR = 9
        self.OP3VR = 10
        self.OP3PR = 11
        self.OP3NU = 12
        self.NL = 13

        # set of opcodes
        self.OP1_is_reg = {"load", "store", "add", "sub", "mult", "lshift", "rshift"}
        self.OP2_is_reg = {"add", "sub", "mult", "lshift", "rshift", "store"}
        self.OP3_is_reg = {"load", "loadI", "add", "sub", "mult", "lshift", "rshift"}

        # number of inserted spill and restore operations into the IR
        self.inserted_lines = 0
        self.start_spill_location = 32768

        # OPCODE Type Dictionary
        self.Type = {"load": "MEMOP", "store": "MEMOP", "loadI": "LOADI", "add": "ARITHOP", "sub": "ARITHOP",
                     "mult": "ARITHOP", "lshift": "ARITHOP", "rshift": "ARITHOP", "output": "OUTPUT", "nop": "NOP"}

    # Allocate in the situation that MAXLIVE > max_pr_num + 1
    def allocate_without_spill(self):
        for i in range(0, self.renamer.n + 1):
            operation = self.OPS[i + self.inserted_lines].record

            # allocate uses OP1 and OP2, if applicable
            if operation[self.OPCODE] in self.OP1_is_reg:
                operation[self.OP1PR] = self.vr2pr[operation[self.OP1VR]]

            if operation[self.OPCODE] in self.OP2_is_reg:
                operation[self.OP2PR] = self.vr2pr[operation[self.OP2VR]]

            # free OP1 and OP2 pr if last use
            if operation[self.OPCODE] in self.OP1_is_reg:
                if operation[self.OP1NU] == float('inf'):
                    self.free_a_pr(operation[self.OP1PR])
                    self.available_prs.append(operation[self.OP1PR])

            if operation[self.OPCODE] in self.OP2_is_reg:
                if operation[self.OP2NU] == float('inf') and \
                        (operation[self.OP1VR] != operation[self.OP2VR]):
                    self.free_a_pr(operation[self.OP2PR])
                    self.available_prs.append(operation[self.OP2PR])

            # allocate defs OP3
            if operation[self.OPCODE] in self.OP3_is_reg:
                #None
                operation[self.OP3PR] = self.get_a_pr(operation[self.OP3VR], operation[self.OP3NU], i, False)

                if operation[self.OP3NU] == float('inf'):
                    self.free_a_pr(operation[self.OP3PR])
                    self.available_prs.append(operation[self.OP3PR])

    # vr: the vr to allocate a pr to
    # op_num: either 1 or 2
    def get_a_pr(self, vr, nu, i, op_num_is_2):
        x = self.available_prs.pop()
        self.vr2pr[vr] = x
        self.pr2vr[x] = vr
        self.pr_nu[x] = nu

        return x

    def free_a_pr(self, pr):
        self.vr2pr[self.pr2vr[pr]] = "invalid"
        self.pr2vr[pr] = "invalid"
        self.pr_nu[pr] = float('inf')

    def test_print(self):
        self.IR.print_me()

    def print_allocated_block(self):
        while self.OPS:
            dl_list = self.OPS.pop(0)
            if self.Type[dl_list.record[0]] == "MEMOP":
                if dl_list.record[0] == "store":
                    print >> sys.stdout, "%s  r%i    =>  r%i" % (dl_list.record[0], dl_list.record[3], dl_list.record[7])
                else:
                    print >> sys.stdout, "%s  r%i    =>  r%i" % (dl_list.record[0], dl_list.record[3], dl_list.record[11])
            elif self.Type[dl_list.record[0]] == "LOADI":
                print >> sys.stdout, "%s  %i    =>  r%i" % (dl_list.record[0], dl_list.record[1], dl_list.record[11])
            elif self.Type[dl_list.record[0]] == "ARITHOP":
                print >> sys.stdout, "%s  r%i, r%i    =>  r%i" \
                                     % (dl_list.record[0], dl_list.record[3], dl_list.record[7], dl_list.record[11])
            elif self.Type[dl_list.record[0]] == "OUTPUT":
                print >> sys.stdout, "%s  %i" % (dl_list.record[0], dl_list.record[1])
