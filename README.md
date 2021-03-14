CO_Project_Phase1 (Team Name - Byte Me)

MIPS Simulator
Simulator on the lines of QtSPIM supporting the MIPS instructions ADD/SUB, BNE, Jump, LD/ST, ADDI, LI, SLT, LA.All the architecture specifications like register size, no of registers and instruction width are same as MIPS.The simulator reads in an assembly file, execute the instructions, and in the end display the contents of the registers, and the memory.

Code is written in the file simulator.py

All register values and memory is stored in hexadecimal.
A dictionary of 32 registers is created,with each registers initialised to zero.Memory is byte addressable,each register is of 4 bytes and 1 byte is 2 bits in hexadecimal, these two bits are stored as an element in a list named MEM.Empty byte in memory is represented with "."

Simulator class is created and all required variables are declared in the init function.Implementation of all the buttons in the GUI is done.The GUI buttons include open, load, auto, next.Open button is used to choose the assembly file to be opened,Load button loads the program,all the values of the registers and memory  are reset before loading and parsing is done here and execution starts from the first line of main,parsing is done differently for data segment and text segment with different functions, Auto button is used to execute the program completely, Next button is used to execute the program line by line and also the instruction currently being executed is displayed.
In the GUI, value of all the 32 registers and the Memory are shown.

All the instructions in the program are stored in a list line by line.
All the labels are stored in a dictionary with the line number of them in the program during parsing for easy access in running the program.
Variables in data are stored in the same way.
PC value(value of line number) is shown in the console during execution.

Different functions are written for the MIPS instructions that are supported.If any other instructions which are not implemented are given or during syntax errors, the program gives a Parsing Error showing at which instruction the parsing went wrong.
If no errors are shown during parsing,we can run the program by using either the auto button or next button(for line by line execution),if the program is run perfectly,a success message "Execution copleted" is shown.

Let us see how the GUI looks like during execution of bubble sort program provided in the repository.
GUI after opening the file:

![Screenshot (208)](https://user-images.githubusercontent.com/70936290/111072783-185b5680-8502-11eb-8a0d-bcace25293a6.png)

GUI after loading the file:

![Screenshot (209)](https://user-images.githubusercontent.com/70936290/111072870-79832a00-8502-11eb-972f-2d2f25a2c87f.png)

If we press next button the program executes line by line and current instruction that is being executed is also shown and the register values change acordingly.
GUI when next button is used:

![Screenshot (210)](https://user-images.githubusercontent.com/70936290/111072994-00380700-8503-11eb-81f1-ad3b910e90eb.png)

If we press on the auto button, the program is executed at once and the registers values are changed according to their use in the program.
GUI after execution completed:

![Screenshot (211)](https://user-images.githubusercontent.com/70936290/111073037-23fb4d00-8503-11eb-9b92-c67548763fa6.png)

Contributors: Aashrith(CS19B025) and Nitesh(CS19B028)

This project is still in development phase, more attributes will be added in the future.
