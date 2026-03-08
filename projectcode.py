import sys


if len(sys.argv) != 3:
    print("Usage: python Assembler.py input.txt output.txt")
    sys.exit()

InputFile=sys.argv[1]
OutputFile=sys.argv[2]

with open(InputFile, 'r') as filein:
    lines =filein.readlines()


assembly_codelines= []
for line in lines:
    line=line.strip()
    if line != "":
        assembly_codelines.append(line)

errcount=0


rtype=["add", "sub", "sll", "slt", "sltu", "xor", "srl", "or", "and"]
itype=["addi", "lw", "sltiu", "jalr"]
stype=["sw"]
btype=["beq", "bne", "blt", "bge", "bltu", "bgeu"]
utype=["lui", "auipc"]
jtype=["jal"]



r_opcode={
   "add":"0110011",
    "sub":"0110011",
    "sll":"0110011",
    "slt":"0110011",
    "sltu":"0110011",
    "xor":"0110011",
    "srl":"0110011",
    "or":"0110011",
    "and":"0110011"
}

r_fn3={
    "add":"000",
    "sub":"000",
    "sll":"001",
    "slt":"010",
    "sltu":"011",
    "xor":"100",
    "srl":"101",
    "or":"110",
    "and":"111"
}

r_fn7={
    "add":"0000000",
    "sub":"0100000",
    "sll":"0000000",
    "slt":"0000000",
    "sltu":"0000000",
    "xor":"0000000",
    "srl":"0000000",
    "or":"0000000",
    "and":"0000000"
}



i_opcode={
    "addi":"0010011",
    "sltiu":"0010011",
    "jalr":"1100111",
    "lw":"0000011"
}

i_fn3={
    "addi":"000",
    "sltiu":"011",
    "jalr":"000",
    "lw":"010"
}



s_opcode={"sw":"0100011"}

s_fn3={"sw":"010"}



b_opcode={
   "beq":"1100011",
    "bne":"1100011",
    "blt":"1100011",
    "bge":"1100011",
    "bltu":"1100011",
    "bgeu":"1100011"
}

b_fn3={
   "beq":"000",
    "bne":"001",
    "blt":"100",
    "bge":"101",
    "bltu":"110",
    "bgeu":"111"
}


u_opcode={
    "lui":"0110111",
    "auipc":"0010111"
}

j_opcode={
    "jal":"1101111"}



def _12bitsigned(value):
    value=int(value)
    if value>=0:
        return format(value, "012b")
    else:
        return format((1<<12)+value, "012b")     
   
    
def _13bitsigned(value):
    value=int(value)     

    if value>=0:
        return format(value, "013b")
    else:
        return format((1<<13)+value, "013b")

def _20bitsigned(value): 
    value=int(value)

    if value>=0:
        return format(value, "020b")
    else:
        return format((1<<20)+value, "020b")

def _21bitsigned(value): 
    value=int(value)

    if value>=0:
        return format(value, "021b")
    else:
        return format((1<<21)+value, "021b")



labels={}
pc=0
new_lines=[]

for orig_lineno, line in enumerate(assembly_codelines, start=1):

    if ":" in line:
        label, rest=line.split(":", 1)

        if not label.strip()[0].isalpha():
            print(f"INVALID LABEL NAME AT LINE {orig_lineno}")
            errcode=f"INVALID LABEL NAME AT LINE {orig_lineno}"
            errcount=1
            break

        if label.strip() in labels:
            print(f"DUPLICATE LABEL AT LINE {orig_lineno}")
            errcode=f"DUPLICATE LABEL AT LINE {orig_lineno}"
            errcount=1
            break

        labels[label.strip()]=pc
        
        rest=rest.strip()

        if rest!="":
            new_lines.append((orig_lineno, rest))
            pc+=4

    else:
        new_lines.append((orig_lineno, line))
        pc+=4


if errcount==0 and assembly_codelines:

    last_raw=assembly_codelines[-1].strip()

    if ":" in last_raw and last_raw[last_raw.index(":")+1:].strip()=="":
        print(f"VIRTUAL HALT MUST BE LAST INSTRUCTION AT LINE {new_lines[-1][0]}")
        errcode=f"VIRTUAL HALT MUST BE LAST INSTRUCTION AT LINE {new_lines[-1][0]}"
        errcount=1




if errcount==0:

    if not new_lines:                        
        print("NO VIRTUAL HALT AT END OF CODE")
        errcode="NO VIRTUAL HALT AT END OF CODE"
        errcount=1

    else:
        end_lineno, end_instruction=new_lines[-1]

        checkLine=end_instruction.replace(",", " ")
        parts=checkLine.split()

        if len(parts) != 4:
            print(f"NO VIRTUAL HALT AT END OF CODE (i.e at line {end_lineno})")
            errcode=f"NO VIRTUAL HALT AT END OF CODE (i.e at line {end_lineno})"
            errcount=1

        elif parts[0] != "beq" or parts[1] != "zero" or parts[2] != "zero":
            print(f"NO VIRTUAL HALT AT END OF CODE (i.e at line {end_lineno})")
            errcode=f"NO VIRTUAL HALT AT END OF CODE (i.e at line {end_lineno})"
            errcount=1

        elif parts[3]=="0" or parts[3]=="0x00000000":
            pass

        elif parts[3] not in labels:
            print(f"NO VIRTUAL HALT AT END OF CODE (LABEL NOT FOUND AT LINE {end_lineno})")
            errcode=f"NO VIRTUAL HALT AT END OF CODE (LABEL NOT FOUND AT LINE {end_lineno})"
            errcount=1

        elif labels[parts[3]] != pc - 4:
            print(f"NO VIRTUAL HALT AT END OF CODE (INCORRECT LABEL NAME AT LINE {end_lineno})")
            errcode=f"NO VIRTUAL HALT AT END OF CODE (INCORRECT LABEL NAME AT LINE {end_lineno})"
            errcount=1
        

bcode=[]


reg={
    "zero":"00000",
    "ra":"00001",
    "sp":"00010",
    "gp":"00011",
    "tp":"00100",
    "t0":"00101",
    "t1":"00110",
    "t2":"00111",
    "s0":"01000",
    "fp":"01000",
    "s1":"01001",
    "a0":"01010",
    "a1":"01011",
    "a2":"01100",
    "a3":"01101",
    "a4":"01110",
    "a5":"01111",
    "a6":"10000",
    "a7":"10001",
    "s2":"10010",
    "s3":"10011",
    "s4":"10100",
    "s5":"10101",
    "s6":"10110",
    "s7":"10111",
    "s8":"11000",
    "s9":"11001",
    "s10":"11010",
    "s11":"11011",
    "t3":"11100",
    "t4":"11101",
    "t5":"11110",
    "t6":"11111",
    "x0":"00000",
    "x1":"00001",
    "x2":"00010",
    "x3":"00011",
    "x4":"00100",
    "x5":"00101",
    "x6":"00110",
    "x7":"00111",
    "x8":"01000",
    "x9":"01001",
    "x10":"01010",
    "x11":"01011",
    "x12":"01100",
    "x13":"01101",
    "x14":"01110",
    "x15":"01111",
    "x16":"10000",
    "x17":"10001",
    "x18":"10010",
    "x19":"10011",
    "x20":"10100",
    "x21":"10101",
    "x22":"10110",
    "x23":"10111",
    "x24":"11000",
    "x25":"11001",
    "x26":"11010",
    "x27":"11011",
    "x28":"11100",
    "x29":"11101",
    "x30":"11110",
    "x31":"11111"
}

if(errcount==0):
    pc=0
    total_inst=len(new_lines)

    for i, (lineno, line) in enumerate(new_lines):     
        
        line=line.replace(",", " ")
        parts=line.split()
        instruction=parts[0]

 
        if i<total_inst - 1:
            if (instruction=="beq" and
                parts[1]=="zero" and
                parts[2]=="zero" and
                (parts[3]=="0" or parts[3]=="0x00000000" or (parts[3] in labels and labels[parts[3]]==pc))):
                print(f"VIRTUAL HALT MUST BE LAST INSTRUCTION AT LINE {lineno}")
                errcode=f"VIRTUAL HALT MUST BE LAST INSTRUCTION AT LINE {lineno}"
                errcount=1
                break

        if instruction in rtype:

            if len(parts) != 4:
                print(f"SYNTAX ERROR FOR R TYPE INSTRUCTION AT LINE {lineno}")
                errcode=f"SYNTAX ERROR FOR R TYPE INSTRUCTION AT LINE {lineno}"
                errcount=1
                break
            
            rd=parts[1]
            rs1=parts[2]
            rs2=parts[3]

            if rd not in reg or rs1 not in reg or rs2 not in reg:         
                print(f"INCORRECT REGISTER NAME AT LINE {lineno}")
                errcount=1
                errcode=f"INCORRECT REGISTER NAME AT LINE {lineno}"
                break

            rd_b=reg[rd]
            rs1_b=reg[rs1]
            rs2_b=reg[rs2]

            fn7_b=r_fn7[instruction]
            fn3_b=r_fn3[instruction]
            opcode_b=r_opcode[instruction]

            bInstruction=fn7_b +rs2_b +rs1_b +fn3_b +rd_b +opcode_b
            bcode.append(bInstruction)

        elif instruction in itype:

            if instruction=="lw":
             

                if len(parts) != 3:
                    print(f"SYNTAX ERROR FOR I TYPE INSTRUCTION AT LINE {lineno}")
                    errcode=f"SYNTAX ERROR FOR I TYPE INSTRUCTION AT LINE {lineno}"
                    errcount=1
                    break

                rd=parts[1]
                offprt=parts[2]

                if "(" not in offprt or ")" not in offprt:
                    print(f"SYNTAX ERROR FOR I TYPE INSTRUCTION AT LINE {lineno}")
                    errcode=f"SYNTAX ERROR FOR I TYPE INSTRUCTION AT LINE {lineno}"
                    errcount=1 
                    break

                immed=offprt[:offprt.index("(")]
                rs1=offprt[offprt.index("(")+1 : offprt.index(")")]
                if rd not in reg or rs1 not in reg:
                    print(f"INCORRECT REGISTER NAME AT LINE {lineno}")
                    errcount=1
                    errcode=f"INCORRECT REGISTER NAME AT LINE {lineno}"
                      
                    break
                rd_b=reg[rd]
                rs1_b=reg[rs1]

                try:
                    value=int(immed)
                except ValueError:
                    print(f"INVALID IMMEDIATE VALUE AT LINE {lineno}")
                    errcode=f"INVALID IMMEDIATE VALUE AT LINE {lineno}"
                    errcount=1
                    break

                if value<-2048 or value>2047:
                        print(f"IMMEDIATE VALUE OUT OF BOUNDS FOR I TYPE INSTRUCTION AT LINE {lineno}")
                        errcode=f"IMMEDIATE VALUE OUT OF BOUNDS FOR I TYPE INSTRUCTION AT LINE {lineno}"
                        errcount=1
                        break
                
                immed_b=_12bitsigned(immed)

                fn3_b=i_fn3[instruction]
                opcode_b=i_opcode[instruction]

            else:
             
                if len(parts)==3 and "(" in parts[2] and ")" in parts[2]:
                    rd=parts[1]
                    offprt=parts[2]
                    immed=offprt[:offprt.index("(")]
                    rs1=offprt[offprt.index("(")+1 : offprt.index(")")]

                elif len(parts)==4:
                    rd=parts[1]
                    rs1=parts[2]
                    immed=parts[3]

                else:
                    print(f"SYNTAX ERROR FOR I TYPE INSTRUCTION AT LINE {lineno}")
                    errcode=f"SYNTAX ERROR FOR I TYPE INSTRUCTION AT LINE {lineno}"
                    errcount=1
                    break

                if rd not in reg or rs1 not in reg:
                    print(f"INCORRECT REGISTER NAME AT LINE {lineno}")
                    errcount=1
                    errcode=f"INCORRECT REGISTER NAME AT LINE {lineno}"
                      
                    break

                rd_b=reg[rd]
                rs1_b=reg[rs1]

                try:
                    value=int(immed)
                except ValueError:
                    print(f"INVALID IMMEDIATE VALUE AT LINE {lineno}")
                    errcode=f"INVALID IMMEDIATE VALUE AT LINE {lineno}"
                    errcount=1
                    break

                if value<-2048 or value>2047:
                    print(f"IMMEDIATE VALUE OUT OF BOUNDS FOR I TYPE INSTRUCTION AT LINE {lineno}")
                    errcount=1
                    errcode=f"IMMEDIATE VALUE OUT OF BOUNDS FOR I TYPE INSTRUCTION AT LINE {lineno}"
                    break

                immed_b=_12bitsigned(immed)

                fn3_b=i_fn3[instruction]
                opcode_b=i_opcode[instruction]

            bInstruction=immed_b +rs1_b +fn3_b +rd_b +opcode_b

            bcode.append(bInstruction)



        elif instruction in stype:       

            if len(parts) != 3:
                print(f"SYNTAX ERROR FOR S TYPE INSTRUCTION AT LINE {lineno}")
                errcode=f"SYNTAX ERROR FOR S TYPE INSTRUCTION AT LINE {lineno}"
                errcount=1
                break

            rs2=parts[1]   
            offprt=parts[2]

            if "(" not in offprt or ")" not in offprt:
                print(f"SYNTAX ERROR FOR S TYPE INSTRUCTION AT LINE {lineno}")
                errcode=f"SYNTAX ERROR FOR S TYPE INSTRUCTION AT LINE {lineno}"
                errcount=1
                break

            immed=offprt[:offprt.index("(")]

            try:
                value=int(immed)
            except ValueError:
                print(f"INVALID IMMEDIATE VALUE AT LINE {lineno}")
                errcode=f"INVALID IMMEDIATE VALUE AT LINE {lineno}"
                errcount=1
                break

            if value<-2048 or value>2047:
               print(f"IMMEDIATE VALUE OUT OF BOUNDS FOR S TYPE INSTRUCTION AT LINE {lineno}")
               errcode=f"IMMEDIATE VALUE OUT OF BOUNDS FOR S TYPE INSTRUCTION AT LINE {lineno}"
               errcount=1
               break

            rs1=offprt[offprt.index("(")+1 : offprt.index(")")]

            if rs1 not in reg or rs2 not in reg:
                    print(f"INCORRECT REGISTER NAME AT LINE {lineno}")
                    errcode=f"INCORRECT REGISTER NAME AT LINE {lineno}"
                    errcount=1
                    break

            rs1_b=reg[rs1]
            rs2_b=reg[rs2]
            immed_b=_12bitsigned(immed)

        
            immed_5to11=immed_b[:7]
            immed_0to4=immed_b[7:]

            fn3_b=s_fn3[instruction]
            opcode_b=s_opcode[instruction]

            bInstruction=immed_5to11 +rs2_b +rs1_b +fn3_b +immed_0to4 +opcode_b

            bcode.append(bInstruction)


