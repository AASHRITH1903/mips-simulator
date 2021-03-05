from tkinter import *
from tkinter.filedialog import askopenfile

default_REG = {
    "$zero": 0,
    "$at": 0,
    "$v0": 0,
    "$v1": 0,
    "$a0": 0,
    "$a1": 0,
    "$a2": 0,
    "$a3": 0,
    "$t0": 0,
    "$t1": 0,
    "$t2": 0,
    "$t3": 0,
    "$t4": 0,
    "$t5": 0,
    "$t6": 0,
    "$t7": 0,
    "$t8": 0,
    "$t9": 0,
    "$s0": 0,
    "$s1": 0,
    "$s2": 0,
    "$s3": 0,
    "$s4": 0,
    "$s5": 0,
    "$s6": 0,
    "$s7": 0,
    "$k0": 0,
    "$k1": 0,
    "$gp": 0,
    "$sp": 0,
    "$fp": 0,
    "$ra": 0,
}


class Simulator:
    filename = ""
    instruction_set = []
    labels = {}
    PC = 0
    REG = default_REG.copy()
    MEM = []

    def reset(self):
        self.instruction_set = []
        self.labels = {}
        self.PC = 0
        self.REG = default_REG.copy()
        self.MEM = []

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

    def run(self):
        root = Tk()
        open_button = Button(root, text="open", command=self.open_file)
        open_button.pack()

        start_button = Button(root, text="start", command=self.start)
        start_button.pack()

        root.mainloop()
        return

    def parse(self):
        # first empty the prev instructions
        self.instruction_set = ["add $r1,$r2,$r2", "sub $r1,$r2,$r2", "fff $r1,$r2,$r2", "add $r1,$r2,$r2"]
        # then go through the file and append the instructions to the list
        # filename is stored in self.filename

    def get_command(self, current):
        return current.split(" ", 1)[0]

    def add(self, current_instruction):
        args = current_instruction.strip().split(",")
        target = args[0].strip().split()[1]
        reg1 = args[1].strip()
        reg2 = args[2].strip()

        self.REG[target] = self.REG[reg1] + self.REG[reg2]

        self.PC += 1
        return

    def sub(self, current_instruction):
        args = current_instruction.strip().split(",")
        target = args[0].strip().split()[1]
        reg1 = args[1].strip()
        reg2 = args[2].strip()

        self.REG[target] = self.REG[reg1] - self.REG[reg2]

        self.PC += 1
        return

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
        return

    def store(self, current_instruction):
        return

    def load_immediate(self, current_instruction):
        args = current_instruction.strip().split(",")
        reg = args[0].strip().split()[1]
        immediate = int(args[1].strip())
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
