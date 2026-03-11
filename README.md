# RISC-V Assembler (Python)

This project implements a basic RISC-V assembler in Python.
It reads RISC-V assembly instructions from an input file and converts them into their corresponding 32-bit binary machine code.

## Features

* Supports multiple RISC-V instruction formats:

  * R-type
  * I-type
  * S-type
  * B-type
  * U-type
  * J-type
* Handles labels and branch offsets
* Performs syntax and semantic error checking
* Validates:

  * Register names
  * Immediate value ranges
  * Label existence
  * Instruction format
* Ensures a virtual halt instruction is present at the end

## Usage

Run the assembler using:<br>
```
python Assembler.py input.txt output.txt
```

* input.txt -> file containing RISC-V assembly instructions
* output.txt -> file where binary machine code will be written

## Output

* If the program executes successfully, then it will print the message for successful decoding and the output file will contain 32-bit binary instructions, one per line.
* If an error occurs, the output file will contain the error message with the line number.
