CO_Project (Team Name - Byte Me)

MIPS Simulator
Simulator on the lines of QtSPIM supporting the MIPS instructions ADD/SUB, BNE, Jump, LD/ST, ADDI, LI, SLT, LA.All the architecture specifications like register size, no of registers and instruction width are same as MIPS.The simulator reads in an assembly file, execute the instructions, and in the end display the contents of the registers, and the memory.
Pipelining is also implemented in which data forwarding can be enabled or disabled as you like.
The simulator supports two levels of cache L1 and L2 with LRU replacement policy.
The no of stalls and total clock cycles required for execution is also dispayed.

All register values and memory is stored in hexadecimal.
A dictionary of 32 registers is created,with each registers initialised to zero.Memory is byte addressable,each register is of 4 bytes and 1 byte is 2 bits in hexadecimal, these two bits are stored as an element in a list named MEM.Empty byte in memory is represented with "."

Simulator class is created and all required variables are declared in the init function.Implementation of all the buttons in the GUI is done.The GUI buttons include open, load, auto, next.Open button is used to choose the assembly file to be opened,Load button loads the program,all the values of the registers and memory  are reset before loading and parsing is done here and execution starts from the first line of main,parsing is done differently for data segment and text segment with different functions, Auto button is used to execute the program completely, Next button is used to execute the program line by line and also the instruction currently being executed is displayed.
In the GUI, value of all the 32 registers and the Memory are shown.

All the instructions in the program are stored in a list line by line.
All the labels are stored in a dictionary with the line number of them in the program during parsing for easy access in running the program.
Variables in data are stored in the same way.

Different functions are written for the MIPS instructions that are supported.If any other instructions which are not implemented are given or during syntax errors, the program gives a Parsing Error showing at which instruction the parsing went wrong.
If no errors are shown during parsing,we can run the program by using either the auto button or next button(for line by line execution).

pipelined.py file contains code for pipelining without data forwarding and pipelined_df.py file contains code for pipelining with data forwarding.
Four latches present between the 5 stages of pipelining are declared as lists. They carry the required data from one stage to the other.
The default dependency of all the registers is set to False, it is made True whenever there arises a dependency in the code.
A cache controller is initialised with the block size, associativity , it controls the L1 and L2 cache

All the 5 stages of pipelining IF, IDRF, EX, mem, WB are implemeted as separarte functions and specific code is written for different instructions to be handled in both pipelined.py and pipelined_df.py
The number of stalls are incremented according to the dependencies of a particular instruction.


INSTRUCTIONS to Run the Simulator:
 - Run the main.py file.
 - You will get an option to enable data forwarding or not, choose an option as you like.
 - A new window will open. Click on 'open' button to select a file to be executed.
 - Click on 'load' button to load the registers and the main memory.
 - Click on 'auto' to execute the file at once or click on 'next' for line by line execution.
 - Close the program once finished.


Contributors: Aashrith(CS19B025) and Nitesh(CS19B028)
