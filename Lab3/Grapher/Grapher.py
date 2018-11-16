# Data Structure

# Old version
# Map: [List1, List2, ...] # row n corresponds to VR_n <==> Node_m
# List_n = [operation index, type(n), delay(n), priority] represents a Node_m for VR_n

# New version of Map
# Map: [i, j, k, m, ...] # each entry corresponds to VR_n <==> Node_m

# Graph
# Nodes = [Node(operation) index, Succ edge index, Pred edge index, type(n), delay(n), priority]
# Node Table: [Node index, Succ edge index, Pred edge index] # row m corresponds to Node_m <==> OP_m
# Edge Table: [Edge index, Source node index, Sink node index, Next Succ, Next Pred, latency(n)]
# Type = [load, store, output]


# the input renamer must have completed the renaming sr to vr process
class Grapher:
    def __init__(self, renamer):
        self.Renamer = renamer
        self.IR = renamer.IR
        self.OPs = self.IR.queue
        self.n = renamer.n  # operation 0...n

        # Initializes the Map from VR to Node, row_n <==> VR_n, note we only need up to number of def_ops
        #self.Map = [[None, None, None, None] for i in range(self.n + 1)]
        self.Map = [None for i in range(self.n + 1)]

        # Initializes the Node Table
        self.Nodes = [[j, None, None, None, None, None] for j in range(self.n + 1)]

        # Initializes the Edge Table
        self.Edges = []
        self.edge_index = 0

        # Indexes for the most recent load, store, and output for serialization of memory ops
        self.last_load = None
        self.last_store = None
        self.last_output = None
        self.prev_loads = []

        # Mapping Table from Type to Integer
        self.type = {"load": 0, "store": 1, "output": 2, "loadI": 3, "add": 4, "sub": 5, "mult": 6, "lshift": 7,
                     "rshift": 8, "nop": 9}
        # Mapping Table from TypedInteger to Latency
        self.latency = [5, 5, 1, 1, 1, 1, 3, 1, 1, 1]

        # Set of opcodes
        self.OP1_is_reg = {"load", "store", "add", "sub", "mult", "lshift", "rshift"}
        self.OP2_is_reg = {"add", "sub", "mult", "lshift", "rshift", "store"}
        self.OP3_is_reg = {"load", "loadI", "add", "sub", "mult", "lshift", "rshift"}

        # OPCODE Type Dictionary
        self.OP_type = {"load": "MEMOP", "store": "MEMOP", "loadI": "LOADI", "add": "ARITHOP", "sub": "ARITHOP",
                     "mult": "ARITHOP", "lshift": "ARITHOP", "rshift": "ARITHOP", "output": "OUTPUT", "nop": "NOP"}

        # Define MACROs
        # Operations
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
        self.OPINDEX = 13
        self.OPPRINT = 14
        # Nodes
        self.NODEINDEX = 0
        self.NODESUCC = 1
        self.NODEPRED = 2
        self.NODETYPE = 3
        self.NODEDELAY = 4
        self.NODEPRIORITY = 5
        # Edges
        self.EDGEINDEX = 0
        self.EDGESOURCE = 1
        self.EDGESINK = 2
        self.EDGENEXTSUCC = 3
        self.EDGENEXTPRED = 4
        self.EDGELATENCY = 5

    # Builds the dependence graph to capture critical relationships in the code
    def graph_builder(self):
        for i in range(self.n + 1):
            operation = self.OPs[i].record
            #print "operation: "
            #print operation

            # create a node for op
            # [Node(operation) index, Succ edge index, Pred edge index, type(n), delay(n), priority]
            node = [operation[self.OPINDEX], None, None, self.type[operation[self.OPCODE]], None, None]
            self.Nodes[operation[self.OPINDEX]] = node

            if operation[self.OPCODE] in self.OP3_is_reg:
                #print "defining map"
                self.Map[operation[self.OP3VR]] = node[self.NODEINDEX]  # could also be just i
            if operation[self.OPCODE] in self.OP1_is_reg:
                # add an edge from o to the node in M(VR_j)
                #print "sink node is", self.Nodes[self.Map[operation[self.OP1VR]]]
                self.add_edge(node, self.Nodes[self.Map[operation[self.OP1VR]]], False, None)
            if operation[self.OPCODE] in self.OP2_is_reg:
                self.add_edge(node, self.Nodes[self.Map[operation[self.OP2VR]]], False, None)

            # if load, store, or output operation, add edges to ensure serialization of memory ops
            # load
            if self.type[operation[self.OPCODE]] == 0:
                self.last_load = operation[self.OPINDEX]
                self.prev_loads.append(operation[self.OPINDEX])
                # needs an edge to the most recent store with full latency
                if self.last_store: self.add_edge(node, self.Nodes[self.last_store], True, 5)
            # store
            elif self.type[operation[self.OPCODE]] == 1:
                self.last_store = operation[self.OPINDEX]
                # needs a serialized edge to the most recent store & output, as well as each previous load
                if self.last_store: self.add_edge(node, self.Nodes[self.last_store], True, 1)
                if self.last_output: self.add_edge(node, self.Nodes[self.last_output], True, 1)
                for index in self.prev_loads:
                    load_node = self.Nodes[index]
                    self.add_edge(node, load_node, True, 1)
            # output
            elif self.type[operation[self.OPCODE]] == 2:
                self.last_output = operation[self.OPINDEX]
                # needs a full latency edge to the most recent store,
                if self.last_store: self.add_edge(node, self.Nodes[self.last_store], True, 5)
                # and a serialized edge to the most recent output
                if self.last_output: self.add_edge(node, self.Nodes[self.last_output], True, 1)

    # Adds an edge from source to sink node
    # [Node(operation) index, Succ edge index, Pred edge index, type(n), delay(n), priority]
    # [Edge index, Source node index, Sink node index, Next Succ, Next Pred, latency]
    def add_edge(self, source, sink, is_io, latency):
        #print "sink is", sink
        if is_io:
            new_edge = [self.edge_index, source[self.NODEINDEX], sink[self.NODEINDEX], None, None, latency]
        else:
            new_edge = [self.edge_index, source[self.NODEINDEX], sink[self.NODEINDEX], None, None, sink[self.NODEDELAY]]
        self.Edges.append(new_edge)
        self.edge_index += 1

        # update the Node table for the source, and then sink
        #print "add_edge", self.Nodes[source[self.NODEINDEX]][self.NODESUCC]
        if self.Nodes[source[self.NODEINDEX]][self.NODESUCC] is None:
            self.Nodes[source[self.NODEINDEX]][self.NODESUCC] = new_edge[self.EDGEINDEX]
        else:
            # find the last edge that doesn't have Next Succ
            last_edge_source_index = self.Nodes[source[self.NODEINDEX]][self.NODESUCC]
            while self.Edges[last_edge_source_index][self.EDGENEXTSUCC]:
                last_edge_source_index = self.Edges[last_edge_source_index][self.EDGENEXTSUCC]
            self.Edges[last_edge_source_index][self.EDGENEXTSUCC] = new_edge[self.EDGEINDEX]

        if self.Nodes[sink[self.NODEINDEX]][self.NODEPRED] is None:
            self.Nodes[sink[self.NODEINDEX]][self.NODEPRED] = new_edge[self.EDGEINDEX]
        else:
            last_edge_sink_index = self.Nodes[sink[self.NODEINDEX]][self.NODEPRED]
            while self.Edges[last_edge_sink_index][self.EDGENEXTPRED]:
                last_edge_sink_index = self.Edges[last_edge_sink_index][self.EDGENEXTSUCC]
            self.Edges[last_edge_sink_index][self.EDGENEXTSUCC] = new_edge[self.EDGEINDEX]

    def print_graph(self):
        print "Map(VR, Node)", self.Map, "\n"
        print "Node Table", self.Nodes, "\n"
        print "Edge Table", self.Edges, "\n"
