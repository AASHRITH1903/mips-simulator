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
        self.main = -1
        self.REG = default_REG.copy()
        self.MEM = ["."] * pow(2, 12)
        self.variable_address = {}

    def reset(self):
        self.instruction_set = []
        self.labels = {}
        self.PC = 0
        self.main = -1
        self.REG = default_REG.copy()
        self.MEM = ["."] * pow(2, 12)
        self.variable_address = {}

    def open_file(self):
        self.filename = askopenfile().name

    def start(self, text_box):
        # implement logic to see if it is a valid assembly file else return
        if self.filename == "":
            print("Invalid file.\n")
            return

        self.reset()
        self.parse()

        print(self.instruction_set)
        print(self.labels)
        print(self.variable_address)

        code = self.exe()
        if code == 0:
            text_box.insert(END, "Executed successfully.\n\nREGISTERS : \n\n")
            for key in self.REG:
                text_box.insert(END, key + " : " + self.REG[key] + "\n")
            text_box.insert(END, "\nMEMORY : \n\n")
            for byte in self.MEM:
                text_box.insert(END, byte + " ")

        elif code == -1:
            text_box.insert(END, "Main function not found . Aborted !!")
        elif code == -2:
            text_box.insert(END, "Parsing error : Invalid symbol !!")

        return

    def run(self):
        root = Tk()
        open_button = Button(root, text="open", command=self.open_file)
        start_button = Button(root, text="start", command=lambda: self.start(text_box))
        text_box = Text(root, height=500, width=200)

        open_button.pack()
        start_button.pack()
        text_box.pack()

        root.mainloop()
        return

    def parse_data_segment(self, lines):
        mi = 0
        for line in lines:
            line = line.strip()
            if not line:
                continue

            tmp = line.split(":", 1)
            variable_name = tmp[0].strip()
            self.variable_address[variable_name] = mi
            variable_type = tmp[1].strip().split(" ", 1)[0]
            value = 0
            if variable_type == ".asciiz":
                value = tmp[1].split("\"")[1]
                for c in value:
                    self.MEM[mi] = c
                    mi += 1

            elif variable_type == ".word":
                value = tmp[1].split()[1]
                if value[:2] != "0x":
                    value = hex(int(value))

                value = value[2:]

                if len(value) > 8:
                    value = "0x" + value[len(value) - 8:]
                else:
                    value = "0x" + "0" * (8 - len(value)) + value

                self.MEM[mi] = value[2:4]
                self.MEM[mi + 1] = value[4:6]
                self.MEM[mi + 2] = value[6:8]
                self.MEM[mi + 3] = value[8:10]
                mi += 4

            elif variable_type == ".space":
                value = int(tmp[1].split()[1])
                for _ in range(value):
                    self.MEM[mi] = "_"
                    mi += 1

        return

    def parse_text_segment(self, lines):
        i = -1
        for line in lines:
            line = line.strip()
            if not line or line[0] == '#':
                continue
            line = line.split("#")[0].strip()

            if line.find(":") != -1:
                # label : instruction
                # or
                # label :
                tmp = line.split(":")
                label = tmp[0].strip()
                instruction = tmp[1].strip()

                self.instruction_set.append(label)
                i += 1
                self.labels[label] = i
                if label == "main":
                    self.main = i
                if instruction:
                    self.instruction_set.append(instruction)
                    i += 1
            else:
                # instruction
                self.instruction_set.append(line)
                i += 1

        return

    def parse(self):
        file = open(self.filename, 'r')
        lines = file.readlines()
        data_segment_start = -1
        text_segment_start = -1
        for idx, line in enumerate(lines):
            if line.strip() == ".text":
                text_segment_start = idx
            elif line.strip() == ".data":
                data_segment_start = idx

        if data_segment_start == -1:
            # data segment doesn't exist
            self.parse_text_segment(lines[text_segment_start + 1:])
        else:
            if data_segment_start < text_segment_start:
                self.parse_data_segment(lines[data_segment_start + 1:text_segment_start])
                self.parse_text_segment(lines[text_segment_start + 1:])
            else:
                self.parse_data_segment(lines[data_segment_start + 1:])
                self.parse_text_segment(lines[text_segment_start + 1:data_segment_start])

        return

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
            self.PC = self.labels[target_label] + 1
        else:
            self.PC += 1

    def jump(self, current_instruction):
        args = current_instruction.strip().split(",")
        target_label = args[0].strip().split()[1]
        self.PC = self.labels[target_label] + 1

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

    def is_label(self, s):
        res = self.labels.get(s, "not found")
        if res == "not found":
            return False
        else:
            return True

    def exe(self):
        if self.main == -1:
            return -1
        self.PC = self.main + 1
        while self.PC < len(self.instruction_set):
            current_instruction = self.instruction_set[self.PC]

            if self.is_label(current_instruction):
                self.PC += 1
                continue

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
                return -2

        return 0


sim = Simulator()
sim.run()
