from pipelined import *

default_df = {
    "$zero": None,
    "$at": None,
    "$v0": None,
    "$v1": None,
    "$a0": None,
    "$a1": None,
    "$a2": None,
    "$a3": None,
    "$t0": None,
    "$t1": None,
    "$t2": None,
    "$t3": None,
    "$t4": None,
    "$t5": None,
    "$t6": None,
    "$t7": None,
    "$t8": None,
    "$t9": None,
    "$s0": None,
    "$s1": None,
    "$s2": None,
    "$s3": None,
    "$s4": None,
    "$s5": None,
    "$s6": None,
    "$s7": None,
    "$k0": None,
    "$k1": None,
    "$gp": None,
    "$sp": None,
    "$fp": None,
    "$ra": None,
}

class Pipelined_DF(Pipelined):
    def __init__(self):

        super().__init__()

        self.root.title("Pipelined MIPS Simulator with Data Forwarding")
        self.df = default_df.copy()


    def reset(self):
        super().reset()
        self.df = default_df.copy()

    
    def single_clock_cycle(self):
        self.WB()
        self.mem()
        self.EXE()
        self.IDRF()
        if not self.stop_IF:
            self.IF()


    def IDRF(self):

        if self.L1 == None:
            self.L2 = None
            return
        current_instruction = self.L1
        op_code = get_opcode(current_instruction)

        if op_code == "add" or op_code == "sub":
            args = current_instruction.strip().split(",")
            target = args[0].strip().split()[1]
            reg1 = args[1].strip()
            reg2 = args[2].strip()

            is_stall = (self.dep[reg1] and self.df[reg1] == None ) or (self.dep[reg2] and self.df[reg2] == None )

            if is_stall:
                # stall at IDRF
                self.stalled_instructions.append(current_instruction)
                self.stalls += 1
                self.stop_IF = True
                self.L2 = None
                return

            v1 = self.df[reg1] if self.dep[reg1]  else int(self.REG[reg1], 16)
            v2 = self.df[reg2] if self.dep[reg2]  else int(self.REG[reg2], 16)

            self.total_stalls += self.stalls
            self.stalls = 0

            self.dep[target] = True
            self.L2 = [op_code, target, v1, v2]
            self.stop_IF = False


        elif op_code == "bne":
            args = current_instruction.strip().split(",")
            reg1 = args[0].strip().split()[1]
            reg2 = args[1].strip()
            target_label = args[2].strip()


            if self.L3 and ( (self.dep[reg1] and self.L3[1] == reg1) or (self.dep[reg2] and self.L3[1] == reg2) ):
                if self.L3[0] == "add" or self.L3[0] == "sub":
                    print("2")
                    self.stop_IF = True
                    self.L2 = None
                    return
                elif self.L3[0] == "ld":
                    self.total_stalls += 1
                    self.total_clock_cycles += 1
                    self.stalled_instructions.append(current_instruction)
                    self.stop_IF = True
                    self.L2 = None
                    return


            v1 = self.df[reg1] if self.dep[reg1] else self.REG[reg1]
            v2 = self.df[reg2] if self.dep[reg2] else self.REG[reg2]

            self.stop_IF = False
            if v1 != v2:
                # branch taken
                self.PC = self.labels[target_label] + 1
                self.branch_taken = True
                self.L2 = ["bne", True]
            else:
                # branch not taken
                self.L2 = ["bne", False]

        elif op_code == "j":
            args = current_instruction.strip().split(",")
            target_label = args[0].strip().split()[1]
            self.PC = self.labels[target_label] + 1
            self.stop_IF = False
            self.branch_taken = True
            self.L2 = ["j", True]

        elif op_code == "ld":
            args = current_instruction.strip().split(",")
            to_reg = args[0].strip().split()[1]

            if args[1].find("(") != -1:
                # using : base_reg

                tmp = args[1].strip().split("(")

                offset = tmp[0].strip()
                if len(offset) >= 2 and offset[:2] == "0x":
                    offset = int(offset, 16)
                else:
                    offset = int(offset)

                base_reg = tmp[1][:len(tmp[1]) - 1].strip()

                is_stall = self.dep[base_reg] and self.df[base_reg] == None

                if is_stall:
                    # stall at IDRF
                    self.stalls += 1
                    self.stalled_instructions.append(current_instruction)
                    self.stop_IF = True
                    self.L2 = None
                    return

                self.total_stalls += self.stalls
                self.stalls = 0

                v = self.df[base_reg] if self.dep[base_reg] else int(self.REG[base_reg], 16)

                self.dep[to_reg] = True
                self.stop_IF = False
                self.L2 = ["ld", to_reg, offset, v]
            else:
                # using : -
                target_address = self.variable_address[args[1].strip()]
                self.dep[to_reg] = True
                self.stop_IF = False
                self.L2 = ["ld", to_reg, target_address]

        elif op_code == "st":
            args = current_instruction.strip().split(",")
            from_reg = args[0].strip().split()[1]

            if args[1].find("(") != -1:
                # using : base_reg , from_reg
                tmp = args[1].strip().split("(")

                offset = tmp[0].strip()
                if len(offset) >=2 and offset[:2] == "0x":
                    offset = int(offset, 16)
                else:
                    offset = int(offset)
                base_reg = tmp[1][:len(tmp[1]) - 1].strip()

                is_stall = (self.dep[base_reg] and self.df[base_reg] == None ) # or (self.dep[from_reg] and self.df[from_reg] == None )

                if is_stall:
                    # stall at IDRF
                    self.stalls += 1
                    self.stalled_instructions.append(current_instruction)
                    self.stop_IF = True
                    self.L2 = None
                    return

                self.total_stalls += self.stalls
                self.stalls = 0

                b = self.df[base_reg] if self.dep[base_reg]  else int(self.REG[base_reg], 16)

                self.L2 = ["st", from_reg, offset, b]
                self.stop_IF = False
            else:
                # using : from_reg
                # if self.dep[from_reg] and :
                    # # stall at IDRF
                    # self.stalls += 1
                    # self.stop_IF = True
                    # self.L2 = None
                    # return

                self.total_stalls += self.stalls
                self.stalled_instructions.append(current_instruction)
                self.stalls = 0

                target_address = self.variable_address[args[1].strip()]
                self.L2 = ["st", from_reg, target_address]
                self.stop_IF = False


            
    def EXE(self):
        if self.L2 == None:
            self.L3 = None
            return

        if self.L2[0] == "add":
            self.L3 = ["add", self.L2[1], self.L2[2] + self.L2[3]]
            self.df[self.L3[1]] = self.L3[2]

        elif self.L2[0] == "sub":
            self.L3 = ["sub", self.L2[1], self.L2[2] - self.L2[3]]
            self.df[self.L3[1]] = self.L3[2]

        elif self.L2[0] == "ld":
            if len(self.L2) == 4:
                self.L3 = ["ld", self.L2[1], self.L2[2] + self.L2[3]]
            else:
                self.L3 = self.L2

        elif self.L2[0] == "st":
            from_reg = self.L2[1]
            if len(self.L2) == 4:
                self.L3 = ["st", to_hex(self.df[from_reg]) if self.dep[from_reg] else self.REG[from_reg], self.L2[2] + self.L2[3]]
            else:
                self.L3 = ["st", to_hex(self.df[from_reg]) if self.dep[from_reg] else self.REG[from_reg], self.L2[2]]

        elif self.L2[0] == "bne":
            self.L3 = self.L2

        elif self.L2[0] == "j":
            self.L3 = self.L2

    def mem(self):
        if self.L3 == None:
            self.L4 = None
            return

        if self.L3[0] == "ld":
            address = self.L3[2]
            val = "0x" + self.cc.read(to_hex(address)) + self.cc.read(to_hex(address+1)) + self.cc.read(to_hex(address+2)) + self.cc.read(to_hex(address+3))
            self.L4 = [self.L3[1], val ]
            self.df[self.L3[1]] = int(val, 16)
            self.total_clock_cycles -= 1
            self.total_stalls -= 1
        
        elif self.L3[0] == "st":

            self.cc.write(to_hex(self.L3[2]), self.L3[1][2:4])
            self.cc.write(to_hex(self.L3[2] + 1), self.L3[1][4:6])
            self.cc.write(to_hex(self.L3[2] + 2) , self.L3[1][6:8])
            self.cc.write(to_hex(self.L3[2] + 3) , self.L3[1][8:10])

            self.L4 = ["st"]
            self.total_clock_cycles -= 1
            self.total_stalls -= 1

        elif self.L3[0] == "add" or self.L3[0] == "sub":
            self.L4 = self.L3[1:]

        else:
            self.L4 = self.L3


    def WB(self):
        if self.L4 == None:
            return
        if self.L4[0] == "bne" or self.L4[0] == "j" or self.L4[0] == "st":
            return
        else:
            target_reg = self.L4[0]
            self.REG[target_reg] = to_hex(self.L4[1])
            self.dep[target_reg] = False
            self.df[target_reg] = None
