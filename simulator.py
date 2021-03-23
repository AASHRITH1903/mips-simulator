from tkinter import *
from tkinter.filedialog import askopenfile
from tkinter import scrolledtext

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


# to convert int , dec-str , hex-str ------------> hex-str with 8 digits (REG format)
def to_hex(num):
    if type(num) == int:
        num = hex(num)
    elif type(num) == str and len(num) < 2:
        num = hex(int(num))
    elif type(num) == str and len(num) >= 2:
        if num[:2] != "0x":
            num = hex(int(num))

    neg = False
    if num[0] == '-':
        neg = True
        num = num[3:]
    else:
        num = num[2:]

    if len(num) > 8:
        num = "0x" + num[len(num) - 8:]
    else:
        num = "0x" + "0" * (8 - len(num)) + num

    return '-' + num if neg else num


class Simulator:
    def __init__(self):
        self.filename = ""
        self.instruction_set = []
        self.labels = {}
        self.PC = 0
        self.main = -1
        # register_name -> hex string
        self.REG = default_REG.copy()
        # char , 2 hex digits , _ , . ,
        self.MEM = ["."] * pow(2, 12)
        # variable_names -> int
        self.variable_address = {}

        self.L1 = ""
        self.L2 = []
        self.L3 = []
        self.L4 = []

        self.dep = {}

        # GUI
        self.root = Tk()
        self.root.title("MIPS Simulator")
        self.open_button = Button(self.root, text="open", command=self.open_file, bg="black", fg="white")
        self.load_button = Button(self.root, text="load", command=self.load_program, bg="grey", fg="white")
        self.next_button = Button(self.root, text="next", command=self.next)
        self.auto_button = Button(self.root, text="auto", command=self.auto)
        self.text_box = scrolledtext.ScrolledText(self.root, width=500, height=200, wrap=WORD)
        self.cib = scrolledtext.ScrolledText(self.root, width=200, height=1, wrap=WORD)

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

    def load_program(self):
        self.text_box.delete("1.0", "end")
        self.cib.delete("1.0", "end")
        self.reset()

        # implement logic to see if it is a valid assembly file else return
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
        self.cib.insert(END, "current instruction : " + self.instruction_set[self.PC])
        self.display_reg_mem(self.text_box)

        print(self.instruction_set)
        print(self.labels)
        print(self.variable_address)

        return

    def auto(self):
        self.text_box.delete("1.0", "end")
        self.cib.delete("1.0", "end")
        while self.PC < len(self.instruction_set):
            message = self.single_instruction_exe()
            if message != "success":
                self.text_box.delete("1.0", "end")
                self.text_box.insert(END, message)
                return
        self.display_reg_mem(self.text_box)
        self.cib.insert(END, "execution completed.")

    def next(self):
        self.text_box.delete("1.0", "end")
        self.cib.delete("1.0", "end")

        message = self.single_instruction_exe()
        if message == "success":
            self.display_reg_mem(self.text_box)
        else:
            self.text_box.insert(END, message)

        if self.PC >= len(self.instruction_set):
            self.cib.insert(END, 'execution completed.')
            self.next_button["state"] = "disabled"
            return
        else:
            self.cib.insert(END, "current instruction : " + self.instruction_set[self.PC])

    def display_reg_mem(self, text_box):
        text_box.insert(END, "\nREGISTERS : \n\n")
        for key in self.REG:
            text_box.insert(END, key + " : " + self.REG[key] + "\n")
        text_box.insert(END, "\nMEMORY : \n\n")
        for byte in self.MEM:
            text_box.insert(END, byte + " ")

    def run(self):

        self.open_button.pack()
        self.load_button.pack()
        self.auto_button.pack()
        self.cib.pack()
        self.next_button.pack()
        self.text_box.pack()

        self.root.mainloop()
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
            if variable_type == ".asciiz":
                value = tmp[1].split("\"")[1]
                for c in value:
                    self.MEM[mi] = c
                    mi += 1

            elif variable_type == ".word":
                values = tmp[1].strip().split(" ", 1)[1].strip().split(',')
                for value in values:
                    value = value.strip()
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

    def IF(self):
        self.L1 = self.instruction_set[self.PC]
        self.PC += 1

    def IDRF(self):
        current_instruction = self.L1
        command = self.get_command(current_instruction)

        if command == "add" or command == "sub":
            args = current_instruction.strip().split(",")
            target = args[0].strip().split()[1]
            reg1 = args[1].strip()
            reg2 = args[2].strip()
            self.L2 = [command, target, int(self.REG[reg1], 16), int(self.REG[reg2], 16)]
            self.dep[target] = True


        elif command == "bne":
            args = current_instruction.strip().split(",")
            reg1 = args[0].strip().split()[1]
            reg2 = args[1].strip()
            target_label = args[2].strip()
            if self.REG[reg1] != self.REG[reg2]:
                # branch taken
                self.PC = self.labels[target_label] + 1
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


    def get_command(self, current):
        return current.split(" ", 1)[0]

    def add(self, current_instruction):
        try:
            args = current_instruction.strip().split(",")
            target = args[0].strip().split()[1]
            reg1 = args[1].strip()
            reg2 = args[2].strip()

            self.REG[target] = to_hex(int(self.REG[reg1], 16) + int(self.REG[reg2], 16))
            self.PC += 1
            return 0

        except:
            return -1

    def sub(self, current_instruction):
        try:
            args = current_instruction.strip().split(",")
            target = args[0].strip().split()[1]
            reg1 = args[1].strip()
            reg2 = args[2].strip()

            self.REG[target] = to_hex(int(self.REG[reg1], 16) - int(self.REG[reg2], 16))
            self.PC += 1
            return 0

        except:
            return -1

    def bne(self, current_instruction):
        try:
            args = current_instruction.strip().split(",")
            reg1 = args[0].strip().split()[1]
            reg2 = args[1].strip()
            target_label = args[2].strip()

            if self.REG[reg1] != self.REG[reg2]:
                self.PC = self.labels[target_label] + 1
            else:
                self.PC += 1

            return 0

        except:
            return -1

    def jump(self, current_instruction):
        try:
            args = current_instruction.strip().split(",")
            target_label = args[0].strip().split()[1]
            self.PC = self.labels[target_label] + 1
            return 0

        except:
            return -1

    def load(self, current_instruction):
        try:
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
            return 0

        except:
            return -1

    def store(self, current_instruction):
        try:
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
            return 0

        except:
            return -1

    def load_immediate(self, current_instruction):
        try:
            args = current_instruction.strip().split(",")
            target_reg = args[0].strip().split()[1]
            immediate = args[1].strip()
            self.REG[target_reg] = to_hex(immediate)
            self.PC += 1
            return 0

        except:
            return -1

    def load_address(self, current_instruction):
        args = current_instruction.strip().split(",")
        target_reg = args[0].strip().split()[1]
        variable_name = args[1].strip()
        print(target_reg, variable_name)
        self.REG[target_reg] = to_hex(self.variable_address[variable_name])
        self.PC += 1
        return 0

    def add_immediate(self, current_instruction):
        try:
            args = current_instruction.strip().split(",")
            target_reg = args[0].strip().split()[1]
            reg1 = args[1].strip()
            immediate = args[2].strip()
            self.REG[target_reg] = to_hex(int(to_hex(immediate), 16) + int(self.REG[reg1], 16))
            self.PC += 1
            return 0

        except:
            return -1

    def slt(self, current_instruction):
        try:
            args = current_instruction.strip().split(",")
            target_reg = args[0].strip().split()[1]
            reg1 = args[1].strip()
            reg2 = args[2].strip()
            v1 = int(self.REG[reg1], 16)
            v2 = int(self.REG[reg2], 16)
            if v1 < v2:
                self.REG[target_reg] = to_hex(1)
            else:
                self.REG[target_reg] = to_hex(0)
            self.PC += 1
            return 0

        except:
            return -1

    def is_label(self, s):
        res = self.labels.get(s, "not found")
        if res == "not found":
            return False
        else:
            return True

    def single_instruction_exe(self):
        print("pc : ", self.PC)
        if self.PC < len(self.instruction_set):

            current_instruction = self.instruction_set[self.PC]
            if self.is_label(current_instruction):
                self.PC += 1
            else:
                command = self.get_command(current_instruction)
                ret_code = 0
                if command == "add":
                    ret_code = self.add(current_instruction)
                elif command == "sub":
                    ret_code = self.sub(current_instruction)
                elif command == "bne":
                    ret_code = self.bne(current_instruction)
                elif command == "j":
                    ret_code = self.jump(current_instruction)
                elif command == "ld":
                    ret_code = self.load(current_instruction)
                elif command == "st":
                    ret_code = self.store(current_instruction)
                elif command == "li":
                    ret_code = self.load_immediate(current_instruction)
                elif command == "la":
                    ret_code = self.load_address(current_instruction)
                elif command == "addi":
                    ret_code = self.add_immediate(current_instruction)
                elif command == "slt":
                    ret_code = self.slt(current_instruction)
                else:
                    return "Parsing Error at : " + current_instruction + "\nExecution aborted !!."

                if ret_code == -1:
                    return "Parsing Error at : " + current_instruction + "\nExecution aborted !!."

        return "success"


sim = Simulator()
sim.run()

# print(to_hex("-4"))

