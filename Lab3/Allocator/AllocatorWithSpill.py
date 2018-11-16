from IR import DoublyLinkedList
import sys
import random

# Only use Allocator if the renamer has finished renaming!!!
# Allocator that reserves one register to hold the spill address, given MAXLIVE > k
class AllocatorWithSpill:
    # renamer: the renamer instance that rewrite the sr numbers into vr numbers
    # pr_num: the max number of PRs
    def __init__(self, renamer, pr_num):
        self.renamer = renamer
        self.max_vr_num = self.renamer.vr_name - 1
        self.max_pr_num = pr_num - 1  # pr: 0, 1,..., max_pr_num
        self.vr2pr = ["invalid" for i in range(self.max_vr_num + 1)]
        self.pr2vr = ["invalid" for j in range(self.max_pr_num)]
        self.pr_nu = [float('inf') for k in range(self.max_pr_num)]
        self.available_prs = []
        for pr in range(0, self.max_pr_num):
            self.available_prs.append(pr)
        self.spill_locations = ["invalid" for i in range(self.max_vr_num + 1)]
        self.loadI_vrs = ["invalid" for i in range(self.max_vr_num + 1)]
        self.load_vrs = ["invalid" for i in range(self.max_vr_num + 1)]

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
        self.PRINT = 14

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
    def allocate_with_spill(self):
        for i in range(0, self.renamer.n + 1):
            operation = self.OPS[i + self.inserted_lines].record

            # allocate uses OP1 and OP2, if applicable
            if operation[self.OPCODE] in self.OP1_is_reg:
                # if OP1.VR has no PR allocated to it
                if self.vr2pr[operation[self.OP1VR]] == "invalid":
                    operation[self.OP1PR] = self.get_a_pr(operation[self.OP1VR], operation[self.OP1NU], i, False)
                    self.restore(operation[self.OP1VR], operation[self.OP1PR], i)
                else:
                    operation[self.OP1PR] = self.vr2pr[operation[self.OP1VR]]

            if operation[self.OPCODE] in self.OP2_is_reg:
                if self.vr2pr[operation[self.OP2VR]] == "invalid":
                    operation[self.OP2PR] = self.get_a_pr(operation[self.OP2VR], operation[self.OP2NU], i, True)
                    self.restore(operation[self.OP2VR], operation[self.OP2PR], i)
                else:
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

                # records whether this VR comes from a loadI operation
                if operation[self.OPCODE] == "loadI":
                    self.loadI_vrs[operation[self.OP3VR]] = operation[self.OP1SR]
                    operation[self.PRINT] = False
                else:
                    operation[self.OP3PR] = self.get_a_pr(operation[self.OP3VR], operation[self.OP3NU], i, False)
                    self.loadI_vrs[operation[self.OP3VR]] = "invalid"

    # vr: the vr to allocate a pr to
    # op_num: either 1 or 2
    def get_a_pr(self, vr, nu, i, op_num_is_2):
        if self.available_prs:
            x = self.available_prs.pop()
        
        # pick an x to spill
        # exclude OP1's pr from available pr pool if allocating for OP2
        else:
            if op_num_is_2:
                operation = self.OPS[i + self.inserted_lines].record
                temp = self.pr_nu[:]
                temp[operation[self.OP1PR]] = -1
                x = temp.index(max(temp))
                #x = temp.index(max(temp))
                # big = max(temp)
                # indices = [j for j, y in enumerate(temp) if y == big]
                # # x = random.choice(indices)
                # #x = temp.index(max(temp))
                # x = random.choice(indices)
                # for c in indices:
                #     if self.loadI_vrs[self.pr2vr[c]] != "invalid":
                #         x = c
                #         break

            else:
                x = self.pr_nu.index(max(self.pr_nu))
            self.spill(x, i)
            self.vr2pr[self.pr2vr[x]] = "invalid"
        self.vr2pr[vr] = x
        self.pr2vr[x] = vr
        self.pr_nu[x] = nu

        return x

    # vr: the vr whose value will be restored from x to memory
    # pr: the pr to store vr's value to
    # i: the i-th operation "group"
    def restore(self, vr, pr, i):
        current_index = i + self.inserted_lines
        if self.loadI_vrs[vr] != "invalid":
            # print "loadI! %i" % i
            loadI_op = DoublyLinkedList.DoublyLinkedList()
            loadI_op.record[self.OPCODE] = "loadI"
            loadI_op.record[self.OP1SR] = self.loadI_vrs[vr]
            loadI_op.record[self.OP3PR] = pr

            self.OPS.insert(current_index, loadI_op)
            self.inserted_lines += 1

        elif self.load_vrs[vr] != "invalid":
            # print "load! %i" % i
            loadI_op = DoublyLinkedList.DoublyLinkedList()
            loadI_op.record[self.OPCODE] = "loadI"
            loadI_op.record[self.OP1SR] = self.load_vrs[vr]
            loadI_op.record[self.OP3PR] = self.max_pr_num

            load_op = DoublyLinkedList.DoublyLinkedList()
            load_op.record[self.OPCODE] = "load"
            load_op.record[self.OP1PR] = self.max_pr_num
            load_op.record[self.OP3PR] = pr

            self.OPS.insert(current_index, loadI_op)
            self.OPS.insert(current_index + 1, load_op)
            self.inserted_lines += 2

        else:
            loadI_op = DoublyLinkedList.DoublyLinkedList()
            loadI_op.record[self.OPCODE] = "loadI"
            loadI_op.record[self.OP1SR] = self.spill_locations[vr]
            loadI_op.record[self.OP3PR] = self.max_pr_num

            load_op = DoublyLinkedList.DoublyLinkedList()
            load_op.record[self.OPCODE] = "load"
            load_op.record[self.OP1PR] = self.max_pr_num
            load_op.record[self.OP3PR] = pr

            self.OPS.insert(current_index, loadI_op)
            self.OPS.insert(current_index + 1, load_op)
            self.inserted_lines += 2

            # update a clean value
            self.load_vrs[vr] = self.spill_locations[vr]

        # if self.loadI_vrs[vr] == "invalid":
        #     loadI_op = DoublyLinkedList.DoublyLinkedList()
        #     loadI_op.record[self.OPCODE] = "loadI"
        #     loadI_op.record[self.OP1SR] = self.spill_locations[vr]
        #     loadI_op.record[self.OP3PR] = self.max_pr_num

        #     load_op = DoublyLinkedList.DoublyLinkedList()
        #     load_op.record[self.OPCODE] = "load"
        #     load_op.record[self.OP1PR] = self.max_pr_num
        #     load_op.record[self.OP3PR] = pr

        #     self.OPS.insert(current_index, loadI_op)
        #     self.OPS.insert(current_index + 1, load_op)
        #     self.inserted_lines += 2

        # else:
        #     loadI_op = DoublyLinkedList.DoublyLinkedList()
        #     loadI_op.record[self.OPCODE] = "loadI"
        #     loadI_op.record[self.OP1SR] = self.loadI_vrs[vr]
        #     loadI_op.record[self.OP3PR] = pr

        #     self.OPS.insert(current_index, loadI_op)
        #     self.inserted_lines += 1

    def free_a_pr(self, pr):
        self.vr2pr[self.pr2vr[pr]] = "invalid"
        self.pr2vr[pr] = "invalid"
        self.pr_nu[pr] = float('inf')

    # vr: the new vr whose value will be allocated to pr
    # nu: the vr's next use
    # pr: the freed up pr that will be assigned to vr
    # i: the i-th operation "group"
    def spill(self, pr, i):
        current_index = i + self.inserted_lines
        spilled_vr = self.pr2vr[pr]

        if self.loadI_vrs[spilled_vr] == "invalid" and self.load_vrs[spilled_vr] == "invalid":
            loadI_op = DoublyLinkedList.DoublyLinkedList()
            loadI_op.record[self.OPCODE] = "loadI"
            loadI_op.record[self.OP1SR] = self.start_spill_location + 4 * spilled_vr
            loadI_op.record[self.OP3PR] = self.max_pr_num
            self.spill_locations[spilled_vr] = self.start_spill_location + 4 * spilled_vr

            store_op = DoublyLinkedList.DoublyLinkedList()
            store_op.record[self.OPCODE] = "store"
            store_op.record[self.OP1PR] = pr
            store_op.record[self.OP2PR] = self.max_pr_num

            # insert the operations into the IR and update the tables
            self.OPS.insert(current_index, loadI_op)
            self.OPS.insert(current_index + 1, store_op)
            self.inserted_lines += 2

    def test_print(self):
        self.IR.print_me()

    def print_allocated_block(self):
        while self.OPS:
            operation = self.OPS.pop(0).record
            if operation[self.PRINT] is True:
                if self.Type[operation[0]] == "MEMOP":
                    if operation[0] == "store":
                        print >> sys.stdout, "%s  r%i    =>  r%i" % (operation[0], operation[3], operation[7])
                    else:
                        print >> sys.stdout, "%s  r%i    =>  r%i" % (operation[0], operation[3], operation[11])
                elif self.Type[operation[0]] == "LOADI":
                    print >> sys.stdout, "%s  %i    =>  r%i" % (operation[0], operation[1], operation[11])
                elif self.Type[operation[0]] == "ARITHOP":
                    print >> sys.stdout, "%s  r%i, r%i    =>  r%i" \
                                         % (operation[0], operation[3], operation[7], operation[11])
                elif self.Type[operation[0]] == "OUTPUT":
                    print >> sys.stdout, "%s  %i" % (operation[0], operation[1])
