from tkinter import *
from tkinter.filedialog import askopenfile


class Simulator:
    filename = ""
    instruction_set = []
    PC = 0
    REG = {
        "$t1": 0,
        "$t2": 0,
        "$t3": 0,
        "$t4": 0,
        "$t5": 0,
        "$t6": 0,
        "$t7": 0,
    }

    def open_file(self):
        self.filename = askopenfile().name

    def start(self):
        # implement logic to see if it is a valid assembly file else return
        if self.filename == "":
            print("Invalid file.\n")
            return
        self.parse()
        self.PC = 0
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
        self.instruction_set = []
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

    def exe(self):

        while self.PC < len(self.instruction_set):
            current_instruction = self.instruction_set[self.PC]
            command = self.get_command(current_instruction)
            if command == "add":
                self.add(current_instruction)
            elif command == "sub":
                self.sub(current_instruction)
            else:
                print("Error!!!")
                return

        return


sim = Simulator()
sim.run()
