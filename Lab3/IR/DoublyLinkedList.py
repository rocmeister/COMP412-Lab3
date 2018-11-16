class DoublyLinkedList:
    def __init__(self):
        #self.record_index = ("Opcode", "SR", "VR", "PR", "NU", "SR", "VR", "PR", "NU", "SR", "VR", "PR", "NU", "INDEX", "PRINT")
        self.record = [None for i in range(15)]
        self.record[14] = True

    def write(self, index, content):
        self.record[index] = content
