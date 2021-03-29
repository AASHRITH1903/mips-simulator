from simulator import *

default_dep = {
    "$zero": False,
    "$at": False,
    "$v0": False,
    "$v1": False,
    "$a0": False,
    "$a1": False,
    "$a2": False,
    "$a3": False,
    "$t0": False,
    "$t1": False,
    "$t2": False,
    "$t3": False,
    "$t4": False,
    "$t5": False,
    "$t6": False,
    "$t7": False,
    "$t8": False,
    "$t9": False,
    "$s0": False,
    "$s1": False,
    "$s2": False,
    "$s3": False,
    "$s4": False,
    "$s5": False,
    "$s6": False,
    "$s7": False,
    "$k0": False,
    "$k1": False,
    "$gp": False,
    "$sp": False,
    "$fp": False,
    "$ra": False,
}

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

class Pipelined(Simulator):
    def __init__(self):
        super().__init__()
        self.root.title("Pipelined MIPS Simulator")

        self.L1 = None
        self.L2 = None
        self.L3 = None
        self.L4 = None

        self.dep = default_dep.copy()
        self.stalls = 0
        self.branch_taken = False
        self.stop_IF = False
        self.to_be_updated = None

        self.total_clock_cycles = 0

    def load_program(self):
        self.text_box.delete("1.0", "end")
        self.cib.delete("1.0", "end")
        self.reset()

        if not self.filename.endswith((".asm", ".s")):
            self.text_box.insert(END, "Invalid file.\n")
            self.next_button["state"] = "disabled"
            return

        self.parse()

        if self.main == -1:
            self.text_box.insert(END, "Main function not found . \nExecution aborted .")
            self.next_button["state"] = "disabled"
            return

        self.next_button["state"] = "active"
        self.PC = self.main + 1

        self.display_reg_mem()
        self.cib.insert(END, f"stalls : {self.stalls}\n")
        self.cib.insert(END, f"total clock cycles : {self.total_clock_cycles}\n")

        print(self.instruction_set)
        print(self.labels)
        print(self.variable_address)

        return

    def reset(self):
        self.instruction_set = []
        self.labels = {}
        self.PC = 0
        self.main = -1
        self.REG = default_REG.copy()
        self.MEM = ["."] * pow(2, 12)
        self.variable_address = {}

        self.L1 = None
        self.L2 = None
        self.L3 = None
        self.L4 = None

        self.dep = default_dep.copy()
        self.stalls = 0
        self.branch_taken = False
        self.stop_IF = False

        self.total_clock_cycles = 0

    def next(self):
        self.single_clock_cycle()
        self.total_clock_cycles += 1

        self.text_box.delete("1.0", "end")
        self.cib.delete("1.0", "end")

        self.display_reg_mem()
        self.cib.insert(END, f"stalls : {self.stalls}\n")
        #self.cib.insert(END, f"{"None" if not self.L1 else self.L1} {"None" if not self.L2 else self.L2} {"None" if not self.L3 else self.L3} {"None" if not self.L4 else self.L4}")
        self.cib.insert(END, f"total clock cycles : {self.total_clock_cycles}\n")

        if not (self.L1 or self.L2 or self.L3 or self.L4):
            self.next_button["state"] = "disabled"
            return

    def auto(self):
        self.next()
        while self.L1 or self.L2 or self.L3 or self.L4:
            self.next()
        

    def single_clock_cycle(self):
        self.WB()
        self.mem()
        self.ex()
        self.IDRF()
        if not self.stop_IF:
            self.IF()

        if self.to_be_updated != None:
            self.dep[self.to_be_updated] = False

    def IF(self):
        if self.branch_taken == True:
            # similar to stall at IF
            self.stalls += 1
            self.L1 = None
            self.branch_taken = False
            return

        if self.PC < len(self.instruction_set):
            self.L1 = self.instruction_set[self.PC]
            self.PC += 1
        else:
            self.L1 = None

    def IDRF(self):
        if self.L1 == None:
            self.L2 = None
            return
        current_instruction = self.L1
        command = get_opcode(current_instruction)

        if command == "add" or command == "sub":
            args = current_instruction.strip().split(",")
            target = args[0].strip().split()[1]
            reg1 = args[1].strip()
            reg2 = args[2].strip()

            is_stall = self.dep[reg1] or self.dep[reg2]

            if is_stall:
                self.stalls += 1
                self.stop_IF = True
                self.L2 = None
            else:
                self.dep[target] = True
                self.stop_IF = False
                self.L2 = [command, target, int(self.REG[reg1], 16), int(self.REG[reg2], 16)]



        elif command == "bne":
            args = current_instruction.strip().split(",")
            reg1 = args[0].strip().split()[1]
            reg2 = args[1].strip()
            target_label = args[2].strip()
            if self.REG[reg1] != self.REG[reg2]:
                # branch taken
                self.PC = self.labels[target_label] + 1
                self.branch_taken = True
                self.L2 = ["bne", True]
            else:
                # branch not taken
                self.L2 = ["bne", False]

        elif command == "j":
            args = current_instruction.strip().split(",")
            target_label = args[0].strip().split()[1]
            self.PC = self.labels[target_label] + 1
            self.L2 = ["j", True]

        elif command == "ld":
            args = current_instruction.strip().split(",")
            to_reg = args[0].strip().split()[1]
            tmp = args[1].strip().split("(")

            offset = tmp[0].strip()
            if offset[:2] == "0x":
                offset = int(offset, 16)
            else:
                offset = int(offset)
            base_reg = tmp[1][:len(tmp[1]) - 1].strip()

    def ex(self):
        if self.L2 == None:
            self.L3 = None
            return

        if self.L2[0] == "add":
            self.L3 = ["add", self.L2[1], self.L2[2] + self.L2[3]]

        elif self.L2[0] == "sub":
            self.L3 = ["sub", self.L2[1], self.L2[2] - self.L2[3]]

        elif self.L2[0] == "ld":
            self.L3 = ["ld", self.L2[1], self.L2[2] + self.L2[3]]

        elif self.L2[0] == "st":
            self.L3 = ["st", self.L2[1], self.L2[2] + self.L2[3]]

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
            val = "0x" + self.MEM[address] + self.MEM[address+1] + self.MEM[address+2] + self.MEM[address+3]
            self.L4 = [self.L3[1], val ]
        
        elif self.L3[0] == "st":
            self.L4 = None
            self.MEM[self.L3[2]] = self.REG[self.L3[1]]
        elif self.L3[0] == "add" or self.L3[0] == "sub":
            self.L4 = self.L3[1:]
        else:
            self.L4 = self.L3

    def WB(self):
        if self.L4 == None:
            return
        if self.L4[0] == "bne" or self.L4[0] == "j":
            return
        else:
            target_reg = self.L4[0]
            self.REG[target_reg] = to_hex(self.L4[1])
            self.to_be_updated = target_reg




class Pipelined_DF(Simulator):
    def __init__(self):
        super().__init__()
        self.root.title("Pipelined MIPS Simulator with Data Forwarding")

        self.L1 = None
        self.L2 = None
        self.L3 = None
        self.L4 = None

        self.dep = default_dep.copy()
        self.df = default_df.copy()
        self.stalls = 0
        self.branch_taken = False
        self.stop_IF = False

        self.total_clock_cycles = 0

    def load_program(self):
        self.text_box.delete("1.0", "end")
        self.cib.delete("1.0", "end")
        self.reset()

        if not self.filename.endswith((".asm", ".s")):
            self.text_box.insert(END, "Invalid file.\n")
            self.next_button["state"] = "disabled"
            return

        self.parse()

        if self.main == -1:
            self.text_box.insert(END, "Main function not found . \nExecution aborted .")
            self.next_button["state"] = "disabled"
            return

        self.next_button["state"] = "active"
        self.PC = self.main + 1

        self.display_reg_mem()
        self.cib.insert(END, f"stalls : {self.stalls}\n")
        self.cib.insert(END, f"total clock cycles : {self.total_clock_cycles}\n")

        print(self.instruction_set)
        print(self.labels)
        print(self.variable_address)

        return

    def reset(self):
        self.instruction_set = []
        self.labels = {}
        self.PC = 0
        self.main = -1
        self.REG = default_REG.copy()
        self.MEM = ["."] * pow(2, 12)
        self.variable_address = {}

        self.L1 = None
        self.L2 = None
        self.L3 = None
        self.L4 = None

        self.dep = default_dep.copy()
        self.df = default_df.copy()
        self.stalls = 0
        self.branch_taken = False
        self.stop_IF = False

        self.total_clock_cycles = 0


    def next(self):
        self.single_clock_cycle()
        self.total_clock_cycles += 1

        self.text_box.delete("1.0", "end")
        self.cib.delete("1.0", "end")

        self.display_reg_mem()
        self.cib.insert(END, f"stalls : {self.stalls}\n")
        #self.cib.insert(END, f"{"None" if not self.L1 else self.L1} {"None" if not self.L2 else self.L2} {"None" if not self.L3 else self.L3} {"None" if not self.L4 else self.L4}")
        self.cib.insert(END, f"total clock cycles : {self.total_clock_cycles}\n")


        if not (self.L1 or self.L2 or self.L3 or self.L4):
            self.next_button["state"] = "disabled"
            return
    
    def auto(self):
        self.next()
        while self.L1 or self.L2 or self.L3 or self.L4:
            self.next()
    
    def single_clock_cycle(self):
        self.WB()
        self.mem()
        self.EXE()
        self.IDRF()
        if not self.stop_IF:
            self.IF()


    def IF(self):        
        if self.branch_taken == True:
            # similar to stall at IF
            self.stalls += 1
            self.L1 = None
            self.branch_taken = False
            return

        if self.PC < len(self.instruction_set):
            self.L1 = self.instruction_set[self.PC]
            self.PC += 1
        else:
            self.L1 = None

    def IDRF(self):

        if self.L1 == None:
            self.L2 = None
            return
        current_instruction = self.L1
        command = get_opcode(current_instruction)

        if command == "add" or command == "sub":
            args = current_instruction.strip().split(",")
            target = args[0].strip().split()[1]
            reg1 = args[1].strip()
            reg2 = args[2].strip()

            is_stall = (self.dep[reg1] and self.df[reg1] == None ) or (self.dep[reg2] and self.df[reg2] == None )

            if is_stall:
                # stall at IDRF
                self.stalls += 1
                self.stop_IF = True
                self.L2 = None
                return

            v1 = self.df[reg1] if self.dep[reg1]  else int(self.REG[reg1], 16)
            v2 = self.df[reg2] if self.dep[reg2]  else int(self.REG[reg2], 16)

            self.dep[target] = True
            self.L2 = [command, target, v1, v2]
            self.stop_IF = False

            print("L2 : ", self.L2)


        elif command == "bne":
            args = current_instruction.strip().split(",")
            reg1 = args[0].strip().split()[1]
            reg2 = args[1].strip()
            target_label = args[2].strip()
            if self.REG[reg1] != self.REG[reg2]:
                # branch taken
                self.PC = self.labels[target_label] + 1
                self.branch_taken = True
                self.L2 = ["bne", True]
            else:
                # branch not taken
                self.L2 = ["bne", False]

        elif command == "j":
            args = current_instruction.strip().split(",")
            target_label = args[0].strip().split()[1]
            self.PC = self.labels[target_label] + 1
            self.branch_taken = True
            self.L2 = ["j", True]

        elif command == "ld":
            args = current_instruction.strip().split(",")
            to_reg = args[0].strip().split()[1]
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
                self.stop_IF = True
                self.L2 = None
                return

            v = self.df[base_reg] if self.dep[base_reg] else int(self.REG[base_reg], 16)

            self.L2 = ["ld", to_reg, offset, v]
            self.dep[to_reg] = True

        elif command == "st":
            args = current_instruction.strip().split(",")
            from_reg = args[0].strip().split()[1]
            tmp = args[1].strip().split("(")

            offset = tmp[0].strip()
            if len(offset) >=2 and offset[:2] == "0x":
                offset = int(offset, 16)
            else:
                offset = int(offset)
            base_reg = tmp[1][:len(tmp[1]) - 1].strip()

            is_stall = (self.dep[base_reg] and self.df[base_reg] == None ) or (self.dep[from_reg] and self.df[from_reg] == None )

            if is_stall:
                # stall at IDRF
                self.stalls += 1
                self.stop_IF = True
                self.L2 = None
                return

            v1 = self.df[from_reg] if self.dep[from_reg]  else int(self.REG[from_reg], 16)
            v2 = self.df[base_reg] if self.dep[base_reg]  else int(self.REG[base_reg], 16)

            self.L2 = ["st", v1, offset, v2]


            
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
            self.L3 = ["ld", self.L2[1], self.L2[2] + self.L2[3]]

        elif self.L2[0] == "st":
            self.L3 = ["st", self.L2[1], self.L2[2] + self.L2[3]]

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
            val = "0x" + self.MEM[address] + self.MEM[address+1] + self.MEM[address+2] + self.MEM[address+3]
            self.L4 = [self.L3[1], val ]
            self.df[self.L3[1]] = int(val, 16)
        
        elif self.L3[0] == "st":
            self.MEM[self.L3[2]] = self.L3[1]
            self.L4 = None

        elif self.L3[0] == "add" or self.L3[0] == "sub":
            self.L4 = self.L3[1:]

        else:
            self.L4 = self.L3


    def WB(self):
        if self.L4 == None:
            return
        if self.L4[0] == "bne" or self.L4[0] == "j":
            return
        else:
            target_reg = self.L4[0]
            self.REG[target_reg] = to_hex(self.L4[1])
            self.dep[target_reg] = False
            self.df[target_reg] = None
