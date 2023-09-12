CO_Project (Team Name - Byte Me)

MIPS Simulator:

Simulator on the lines of QtSPIM supporting the MIPS instructions ADD/SUB, BNE, Jump, LD/ST, ADDI, LI, SLT, LA.All the architecture specifications like register size, no of registers and instruction width are same as MIPS.The simulator reads in an assembly file, execute the instructions, and in the end display the contents of the registers, and the memory.

Pipelining is also implemented in which data forwarding can be enabled or disabled as you like.
The simulator supports two levels of cache L1 and L2 with LRU replacement policy.
The no of stalls and total clock cycles required for execution is also dispayed.

Implementation:

All register values and memory is stored in hexadecimal.
A dictionary of 32 registers is created,with each registers initialised to zero.Memory is byte addressable,each register is of 4 bytes and 1 byte is 2 bits in hexadecimal, these two bits are stored as an element in a list named MEM.Empty byte in memory is represented with "."

Simulator class is created and all required variables are declared in the init function.Implementation of all the buttons in the GUI is done.The GUI buttons include open, load, auto, next.Open button is used to choose the assembly file to be opened,Load button loads the program,all the values of the registers and memory  are reset before loading and parsing is done here and execution starts from the first line of main,parsing is done differently for data segment and text segment with different functions, Auto button is used to execute the program completely, Next button is used to execute the program line by line and also the instruction currently being executed is displayed.
In the GUI, value of all the 32 registers and the Memory are shown.

All the instructions in the program are stored in a list line by line.
All the labels are stored in a dictionary with the line number of them in the program during parsing for easy access in running the program.
Variables in data are stored in the same way.

Different functions are written for the MIPS instructions that are supported.If any other instructions which are not implemented are used or during syntax errors, the program gives a Parsing Error showing at which instruction the parsing went wrong.
If no errors are shown during parsing,we can run the program by using either the auto button or next button(for line by line execution).

pipelined.py file contains code for pipelining without data forwarding and pipelined_df.py file contains code for pipelining with data forwarding.
Four latches present between the 5 stages of pipelining are declared as lists. They carry the required data from one stage to the other.
The default dependency of all the registers is set to False, it is made True whenever there arises a dependency in the code.
A cache controller which controls the L1 and L2 cache is initialised with the block size, associativity, cache size of both L1 and L2.

All the 5 stages of pipelining IF, IDRF, EX, mem, WB are implemeted as separarte functions and specific code is written for different instructions to be handled in both pipelined.py and pipelined_df.py
The number of stalls are incremented according to the dependencies of a particular instruction.

Cache is implemented in cache.py file.
A Block class is created with attributes Block size and rem(This is the remainder of the address after removing the index bit and offset). Block objects are created for L1 and L2 cache according to the number of blocks they contain.
A Set class is created with attributes index i, associativity A and block size B. Set objects are created in the L1 and L2 cache according to the number of sets present in each of them. Set class contains add_block method which appends a particular block to the set.

The Set class is extended by Set1 class for L1 cache and Set2 class for L2 cache. They contain read and write methods.

A Cache class is created with the attributes Associativity, Block size and Cache size. It contains add_block method which adds a block to the specified set using the index bit.

L1Cache and L2Cache classes extend the Cache class which contains read and write methods which in turn calls the read and write methods of a particular Set required using the index bit.

A Cache_Controller which controls the L1 and L2 cache is created with the attributes Associativity, Cache size and Block size of both L1 and L2 caches. It contains read method which checks for the address in both L1 and L2 caches, write method which writes the changes back to the cache(either L1 or L2 in which the address is found), add_to_L1 method to add a block to L1 cache, add_to_L2 method to add a block to L2 cache, clear method which cleares the entire memory.


INSTRUCTIONS to Run the Simulator:
 - Run the main.py file.
 - A GUI window with an option to enable data forwarding or not, choose an option as you like.
 - A new GUI window will open. Click on 'open' button to select a file to be executed.
 - Click on 'load' button to load the registers and the main memory.
 - Click on 'auto' to execute the file at once or click on 'next' for line by line execution.
 - Close the program once finished.

The GUI looks as below after the execution of a test case:


 
 ![Screenshot from 2021-05-10 21-03-43](https://user-images.githubusercontent.com/63637200/117685372-84d99580-b1d3-11eb-88d7-baeb86d38c12.png)

Contributors: Aashrith(CS19B025) and Nitesh(CS19B028)
