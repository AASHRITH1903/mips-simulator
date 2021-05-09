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

class Pipelined(Simulator):
    def __init__(self):

        self.cc = Cache_Controller(4,64,4,64,4,self)
        super().__init__(self.cc)

        self.root.title("Pipelined MIPS Simulator without Data Forwarding")

        self.L1 = None
        self.L2 = None
        self.L3 = None
        self.L4 = None

        self.dep = default_dep.copy()
        self.stalls = 0
        self.branch_taken = False
        self.stop_IF = False
        self.to_be_updated = None

        self.total_stalls = 0
        self.total_clock_cycles = 0
        self.total_instructions = 0
        self.stalled_instructions = []


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
        super().reset()
        self.L1 = None
        self.L2 = None
        self.L3 = None
        self.L4 = None

        self.dep = default_dep.copy()
        self.stalls = 0
        self.branch_taken = False
        self.stop_IF = False

        self.total_stalls = 0
        self.total_clock_cycles = 0
        self.total_instructions = 0
        self.stalled_instructions = []


    def next(self):
        self.single_clock_cycle()
        self.total_clock_cycles += 1

        self.text_box.delete("1.0", "end")
        self.cib.delete("1.0", "end")

        self.display_reg_mem()

        self.cib.insert(END, f"total clock cycles : {self.total_clock_cycles}\n")
        self.cib.insert(END, f"stalls : {self.total_stalls}\n")
        self.cib.insert(END, f"IPC : {self.total_instructions / self.total_clock_cycles}")
        
        print(self.L1, self.L2, self.L3, self.L4)

        if not (self.L1 or self.L2 or self.L3 or self.L4):
            self.next_button["state"] = "disabled"
            self.cib.insert(END, "\nstalled instructions : \n")
            for i in self.stalled_instructions:
                self.cib.insert(END, i+"\n" )
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

        if self.to_be_updated != None:
            self.dep[self.to_be_updated] = False

    def IF(self):
        if self.branch_taken == True:
            # similar to stall at IF
            # self.stalls += 1
            self.L1 = None
            self.branch_taken = False
            return

        if self.PC < len(self.instruction_set):

            if self.is_label(self.instruction_set[self.PC]):
                self.PC += 1

            if self.PC < len(self.instruction_set):
                self.L1 = self.instruction_set[self.PC]
                self.total_instructions += 1
                self.PC += 1
            else:
                self.L1 = None
        else:
            self.L1 = None

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

            is_stall = self.dep[reg1] or self.dep[reg2]

            if is_stall:
                # stall at IDRF
                self.stalls += 1
                self.stalled_instructions.append(current_instruction)
                self.stop_IF = True
                self.L2 = None
                return

            self.total_stalls += self.stalls-1 if self.stalls > 0 else 0
            self.stalls = 0

            self.dep[target] = True
            self.stop_IF = False
            self.L2 = [op_code, target, int(self.REG[reg1], 16), int(self.REG[reg2], 16)]



        elif op_code == "bne":
            args = current_instruction.strip().split(",")
            reg1 = args[0].strip().split()[1]
            reg2 = args[1].strip()
            target_label = args[2].strip()
            # using : reg1 , reg2
            is_stall = self.dep[reg1] or self.dep[reg2] 

            if is_stall:
                self.stalls += 1
                self.stalled_instructions.append(current_instruction)
                self.stop_IF = True
                self.L2 = None
                return

            self.total_stalls += self.stalls-1 if self.stalls > 0 else 0
            self.stalls = 0

            self.stop_IF = False
            if self.REG[reg1] != self.REG[reg2]:
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

                is_stall = self.dep[base_reg]

                if is_stall:
                    # stall at IDRF
                    self.stalls += 1
                    self.stalled_instructions.append(current_instruction)
                    self.stop_IF = True
                    self.L2 = None
                    return

                self.total_stalls += self.stalls-1 if self.stalls > 0 else 0
                self.stalls = 0

                self.dep[to_reg] = True
                self.stop_IF = False
                self.L2 = ["ld", to_reg, offset, int(self.REG[base_reg], 16)]
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
                # using : from_reg , base_reg

                tmp = args[1].strip().split("(")

                offset = tmp[0].strip()
                if len(offset) >=2 and offset[:2] == "0x":
                    offset = int(offset, 16)
                else:
                    offset = int(offset)
                base_reg = tmp[1][:len(tmp[1]) - 1].strip()

                is_stall = (self.dep[base_reg] ) or (self.dep[from_reg] )

                if is_stall:
                    # stall at IDRF
                    self.stalls += 1
                    self.stalled_instructions.append(current_instruction)
                    self.stop_IF = True
                    self.L2 = None
                    return

                self.total_stalls += self.stalls-1 if self.stalls > 0 else 0
                self.stalls = 0

                self.L2 = ["st", self.REG[from_reg], offset, int(self.REG[base_reg], 16)]
                self.stop_IF = False
            else:
                # using : from_reg
                if self.dep[from_reg]:
                    # stall at IDRF
                    self.stalls += 1
                    self.stalled_instructions.append(current_instruction)
                    self.stop_IF = True
                    self.L2 = None
                    return

                self.total_stalls += self.stalls-1 if self.stalls > 0 else 0
                self.stalls = 0

                target_address = self.variable_address[args[1].strip()]
                self.L2 = ["st", self.REG[from_reg], target_address]
                self.stop_IF = False




    def EXE(self):
        if self.L2 == None:
            self.L3 = None
            return

        if self.L2[0] == "add":
            self.L3 = ["add", self.L2[1], self.L2[2] + self.L2[3]]

        elif self.L2[0] == "sub":
            self.L3 = ["sub", self.L2[1], self.L2[2] - self.L2[3]]

        elif self.L2[0] == "ld":
            if len(self.L2) == 4:
                self.L3 = ["ld", self.L2[1], self.L2[2] + self.L2[3]]
            else:
                self.L3 = self.L2

        elif self.L2[0] == "st":
            if len(self.L2) == 4:
                self.L3 = ["st", self.L2[1], self.L2[2] + self.L2[3]]
            else:
                self.L3 = self.L2

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
            # val = "0x" + self.MEM[address] + self.MEM[address+1] + self.MEM[address+2] + self.MEM[address+3]
            val = "0x" + self.cc.read(to_hex(address)) + self.cc.read(to_hex(address+1)) + self.cc.read(to_hex(address+2)) + self.cc.read(to_hex(address+3))
            self.L4 = [self.L3[1], val ]
            self.total_clock_cycles -= 1
            self.total_stalls -= 1
        
        elif self.L3[0] == "st":
            # self.MEM[self.L3[2]] = self.L3[1][2:4]
            # self.MEM[self.L3[2] + 1] = self.L3[1][4:6]
            # self.MEM[self.L3[2] + 2] = self.L3[1][6:8]
            # self.MEM[self.L3[2] + 3] = self.L3[1][8:10]

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
            self.to_be_updated = target_reg



