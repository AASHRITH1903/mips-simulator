from tkinter import *
from tkinter.filedialog import askopenfile

default_REG = {
    "$zero": "0x00000000",
    "$at": "0x00000000",
    "$v0": "0x00000000",
    "$v1": "0x00000000",
    "$a0": "0x00000000",
    "$a1": "0x00000000",
    "$a2": "0x00000000",
    "$a3": "0x00000000",
    "$t0": "0x00000000",
    "$t1": "0x00000000",
    "$t2": "0x00000000",
    "$t3": "0x00000000",
    "$t4": "0x00000000",
    "$t5": "0x00000000",
    "$t6": "0x00000000",
    "$t7": "0x00000000",
    "$t8": "0x00000000",
    "$t9": "0x00000000",
    "$s0": "0x00000000",
    "$s1": "0x00000000",
    "$s2": "0x00000000",
    "$s3": "0x00000000",
    "$s4": "0x00000000",
    "$s5": "0x00000000",
    "$s6": "0x00000000",
    "$s7": "0x00000000",
    "$k0": "0x00000000",
    "$k1": "0x00000000",
    "$gp": "0x00000000",
    "$sp": "0x00000000",
    "$fp": "0x00000000",
    "$ra": "0x00000000",
}


class Simulator:
    def __init__(self):
        self.filename = ""
        self.instruction_set = []
        self.labels = {}
        self.PC = 0
        self.data = 0
        self.REG = default_REG.copy()
        self.MEM = ["00"] * pow(2, 12)

    def reset(self):
        self.instruction_set = []
        self.labels = {}
        self.PC = 0
        self.REG = default_REG.copy()
        self.MEM = ["00"] * pow(2, 12)

    def open_file(self):
        self.filename = askopenfile().name

    def start(self):
        # implement logic to see if it is a valid assembly file else return
        if self.filename == "":
            print("Invalid file.\n")
            return

        self.reset()
        self.parse()
        self.exe()
        print("Execution completed")
        print("t0 : ", self.REG["$t0"], " t1 : ", self.REG["$t1"], " t2 : ", self.REG["$t2"])
        print("MEM : ", self.MEM[53])

    def run(self):
        root = Tk()
        open_button = Button(root, text="open", command=self.open_file)
        open_button.pack()

        start_button = Button(root, text="start", command=self.start)
        start_button.pack()

        root.mainloop()
        return

    def parse(self):
        # self.instruction_set = ["li $t0,233", "li $t1,10", "st $t0,40($t1)", "ld $t2,40($t1)"]
        file1 = open(self.filename, 'r')
        for line in file1:
            if line.strip():
                line = line.strip()
            line = line.split("#")[0]
            if line.strip():
                line = line.strip()
                self.instruction_set.append(line)
        print(self.instruction_set)
        for i, line in enumerate(self.instruction_set):
            if line.find("main:") != -1:
                self.PC = i+1
                break
            else:
                print("ERROR")
        for i, line in enumerate(self.instruction_set):
            if line.find(".data") != -1:
                self.data = i+1
                break

        for i, line in enumerate(self.instruction_set):
            if line.find(":") != -1:
                label = line.split(":")[0]
                self.labels[label] = i
        print(self.labels)

        # then go through the file and append the instructions to the list
        # filename is stored in self.filename

    def get_command(self, current):
        return current.split(" ", 1)[0]

    def add(self, current_instruction):
        args = current_instruction.strip().split(",")
        target = args[0].strip().split()[1]
        reg1 = args[1].strip()
        reg2 = args[2].strip()

        res = hex(int(self.REG[reg1], 16) + int(self.REG[reg2], 16))[2:]
        if len(res) > 8:
            res = "0x" + res[len(res) - 8:]
        else:
            res = "0x" + "0" * (8 - len(res)) + res

        self.REG[target] = res
        self.PC += 1

    def sub(self, current_instruction):
        args = current_instruction.strip().split(",")
        target = args[0].strip().split()[1]
        reg1 = args[1].strip()
        reg2 = args[2].strip()

        res = hex(int(self.REG[reg1], 16) - int(self.REG[reg2], 16))[2:]
        if len(res) > 8:
            res = "0x" + res[len(res) - 8:]
        else:
            res = "0x" + "0" * (8 - len(res)) + res

        self.REG[target] = res
        self.PC += 1

    def bne(self, current_instruction):
        args = current_instruction.strip().split(",")
        reg1 = args[0].strip().split()[1]
        reg2 = args[1].strip()
        target_label = args[2].strip()
        if self.REG[reg1] != self.REG[reg2]:
            self.PC = self.labels[target_label]
        else:
            self.PC += 1

    def jump(self, current_instruction):
        args = current_instruction.strip().split(",")
        target_label = args[0].strip().split()[1]
        self.PC = self.labels[target_label]

    def load(self, current_instruction):
        args = current_instruction.strip().split(",")
        to_reg = args[0].strip().split()[1]
        tmp = args[1].strip().split("(")
        offset = tmp[0].strip()
        if offset[:2] == "0x":
            offset = int(offset, 16)
        else:
            offset = int(offset)
        base_reg = tmp[1][:len(tmp[1]) - 1].strip()
        target_address = offset + int(self.REG[base_reg], 16)
        self.REG[to_reg] = "0x" + self.MEM[target_address] + self.MEM[target_address + 1] + self.MEM[
            target_address + 2] + self.MEM[target_address + 3]
        self.PC += 1

    def store(self, current_instruction):
        args = current_instruction.strip().split(",")
        from_reg = args[0].strip().split()[1]
        tmp = args[1].strip().split("(")
        offset = tmp[0].strip()
        if offset[:2] == "0x":
            offset = int(offset, 16)
        else:
            offset = int(offset)
        base_reg = tmp[1][:len(tmp[1]) - 1].strip()
        to_address = offset + int(self.REG[base_reg], 16)
        val = self.REG[from_reg]
        self.MEM[to_address] = val[2:4]
        self.MEM[to_address + 1] = val[4:6]
        self.MEM[to_address + 2] = val[6:8]
        self.MEM[to_address + 3] = val[8:10]
        self.PC += 1

    def load_immediate(self, current_instruction):
        args = current_instruction.strip().split(",")
        reg = args[0].strip().split()[1]
        immediate = args[1].strip()

        if immediate[:2] != "0x":
            immediate = hex(int(immediate))

        immediate = immediate[2:]

        if len(immediate) > 8:
            immediate = "0x" + immediate[len(immediate) - 8:]
        else:
            immediate = "0x" + "0" * (8 - len(immediate)) + immediate

        self.REG[reg] = immediate
        self.PC += 1

    def exe(self):

        while self.PC < len(self.instruction_set):
            current_instruction = self.instruction_set[self.PC]
            command = self.get_command(current_instruction)
            if command == "add":
                self.add(current_instruction)
            elif command == "sub":
                self.sub(current_instruction)
            elif command == "bne":
                self.bne(current_instruction)
            elif command == "j":
                self.jump(current_instruction)
            elif command == "ld":
                self.load(current_instruction)
            elif command == "st":
                self.store(current_instruction)
            elif command == "li":
                self.load_immediate(current_instruction)
            else:
                print("Parsing Error!! Invalid Symbol.")
                return

        return


sim = Simulator()
sim.run()
