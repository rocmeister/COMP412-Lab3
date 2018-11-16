from DoublyLinkedList import DoublyLinkedList
from collections import deque
import sys

class IR:
    def __init__(self):
        # self.head_list = None
        # self.tail_list = None
        self.queue = []
        self.opcode_index = ("load", "store", "loadI", "add", "sub", "mult", "lshift", "rshift", "output", "nop")

    def add_list(self, new_list):
        self.queue.append(new_list)
        # if self.head_list is None:
        #     self.head_list = new_list
        #     self.head_list.next_list = self.tail_list
        # else:
        #     if self.tail_list is not None:
        #         self.tail_list.next_list = new_list
        #         new_list.prev_list = self.tail_list
        #     else:
        #         self.head_list.next_list = new_list
        #         new_list.prev_list = self.head_list
        #     self.tail_list = new_list

    def print_me(self):
        print "Print Format: [Opcode", "SR", "VR", "PR", "NU", "SR", "VR", "PR", "NU", \
            "SR", "VR", "PR", "NU", "LN PRINT]"
        while self.queue:
            dl_list = self.queue.pop(0)
            print dl_list.record
            # for item in dl_list.record:
            #     if item is not None:
            #         print item

    def pretty_printer(self):
        print >> sys.stdout, "Pretty printer not implemented yet, calling print_me..."
        self.print_me()
