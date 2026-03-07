import sys

InputFile=sys.argv[1]
OutputFile=sys.argv[2]


with open(InputFile, 'r') as filein:
    lines =filein.readlines()


assembly_codelines= []
assembly_linenos=[] 
for lineno, line in enumerate(lines, start=1):
    line=line.strip()
    if line!="":
        assembly_codelines.append(line)
        assembly_linenos.append(lineno)

        

errorcount=0


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
        return format((1<<12) + value, "012b")     
   
    
def _13bitsigned(value):
    value=int(value)     

    if value>=0:
        return format(value, "013b")
    else:
        return format((1<<13) + value, "013b")

def _20bitsigned(value): 
    value=int(value)

    if value>=0:
        return format(value, "020b")
    else:
        return format((1<<20) + value, "020b")

def _21bitsigned(value): 
    value=int(value)

    if value>=0:
        return format(value, "021b")
    else:
        return format((1<<21) + value, "021b")

labels={}     
pc=0

for line in assembly_codelines:
    if line.endswith(":"):
        labelname=line[:-1]
        labels[labelname]=pc
    else:
        pc+=4


end_instruction=assembly_codelines[-1]
last_lineno=assembly_linenos[-1]
if end_instruction.endswith(":"):
    print(f"NO VIRTUAL HALT AT END OF CODE (i.e at line {last_lineno})")
    errorcode=f"NO VIRTUAL HALT AT END OF CODE (i.e at line {last_lineno})"
      
    errorcount=1



else:
    checkLine=end_instruction.replace(",", " ")
    parts=checkLine.split()

    if len(parts)!=4:
       print(f"NO VIRTUAL HALT AT END OF CODE (i.e at line {last_lineno})")
       errorcode=f"NO VIRTUAL HALT AT END OF CODE (i.e at line {last_lineno})"
         
       errorcount=1
        

    elif parts[0]!="beq" or parts[1]!="zero" or parts[2]!="zero":
        print(f"NO VIRTUAL HALT AT END OF CODE (i.e at line {last_lineno})")
        errorcode=f"NO VIRTUAL HALT AT END OF CODE (i.e at line {last_lineno})"
          
        errorcount=1
        

    elif parts[3] not in labels or labels[parts[3]]!=(pc - 4):
        print(f"VIRTUAL HALT DOES NOT ENTER INFINITE LOOP (INCORRECT LABEL NAME AT LINE {last_lineno})")
        errorcode=f"VIRTUAL HALT DOES NOT ENTER INFINITE LOOP (INCORRECT LABEL NAME AT LINE {last_lineno})"
          
        errorcount=1
        

binarycode=[]


registers = {
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
    "t6":"11111"
}

if(errorcount==0):
    pc=0
    for idx, line in enumerate(assembly_codelines):
        lineno=assembly_linenos[idx]

        if line.endswith(":"):
            continue   
        
        line=line.replace(",", " ")
        
        parts=line.split()

        instruction=parts[0]

        if instruction in rtype:
            rd=parts[1]
            rs1=parts[2]
            rs2=parts[3]

            if len(parts)!=4:
                    print(f"SYNTAX ERROR FOR R TYPE INSTRUCTION AT LINE {lineno}")
                    errorcode=f"SYNTAX ERROR FOR R TYPE INSTRUCTION AT LINE {lineno}"
                     
                    errorcount=1
                    break
            if rd not in registers or rs1 not in registers or rs2 not in registers:         
                print(f"INCORRECT REGISTER NAME AT LINE {lineno}")
                errorcount=1
                errorcode=f"INCORRECT REGISTER NAME AT LINE {lineno}"
                  
                break

            rd_binary=registers[rd]
            rs1_binary=registers[rs1]
            rs2_binary=registers[rs2]

            fn7_binary=r_fn7[instruction]
            fn3_binary=r_fn3[instruction]
            opcode_binary=r_opcode[instruction]

            BinaryInstruction=(
                fn7_binary +
                rs2_binary +
                rs1_binary +
                fn3_binary +
                rd_binary +
                opcode_binary
            )

            binarycode.append(BinaryInstruction)
        elif instruction in itype:

            if instruction=="lw":
             

                if len(parts)!=3:
                    print(f"SYNTAX ERROR FOR I TYPE INSTRUCTION AT LINE {lineno}")
                    errorcode=f"SYNTAX ERROR FOR I TYPE INSTRUCTION AT LINE {lineno}"
                     
                    errorcount=1
                    break

                rd=parts[1]
                offsetpart=parts[2]

                if "(" not in offsetpart or ")" not in offsetpart:
                    print(f"SYNTAX ERROR FOR I TYPE INSTRUCTION AT LINE {lineno}")
                    errorcode=f"SYNTAX ERROR FOR I TYPE INSTRUCTION AT LINE {lineno}"
                     
                    errorcount=1
                    break
                immed=offsetpart[:offsetpart.index("(")]
                rs1=offsetpart[offsetpart.index("(")+1 : offsetpart.index(")")]
                if rd not in registers or rs1 not in registers:
                    print(f"INCORRECT REGISTER NAME AT LINE {lineno}")
                    errorcount=1
                    errorcode=f"INCORRECT REGISTER NAME AT LINE {lineno}"
                      
                    break
                rd_binary=registers[rd]
                rs1_binary=registers[rs1]
                value=int(immed)
                if value<-2048 or value>2047:
                        print(f"IMMEDIATE VALUE OUT OF BOUNDS FOR I TYPE INSTRUCTION AT LINE{lineno}")
                        errorcode=f"IMMEDIATE VALUE OUT OF BOUNDS FOR I TYPE INSTRUCTION AT LINE{lineno}"
                        errorcount=1
                        break
                



                immed_binary=_12bitsigned(immed)

                fn3_binary=i_fn3[instruction]
                opcode_binary=i_opcode[instruction]

            else:
             
                if len(parts)!=4:
                    print(f"SYNTAX ERROR FOR I TYPE INSTRUCTION AT LINE {lineno}")
                    errorcode=f"SYNTAX ERROR FOR I TYPE INSTRUCTION AT LINE {lineno}"
                     
                    errorcount=1
                    break

                rd=parts[1]
                rs1=parts[2]
                immed=parts[3]

                if rd not in registers or rs1 not in registers:
                    print(f"INCORRECT REGISTER NAME AT LINE {lineno}")
                    errorcount=1
                    errorcode=f"INCORRECT REGISTER NAME AT LINE {lineno}"
                      
                    break

                rd_binary=registers[rd]
                rs1_binary=registers[rs1]
                value=int(immed)
                if value<-2048 or value>2047:
                        print(f"IMMEDIATE VALUE OUT OF BOUNDS FOR I TYPE INSTRUCTION AT LINE{lineno}")
                        errorcount=1
                        errorcode=f"IMMEDIATE VALUE OUT OF BOUNDS FOR I TYPE INSTRUCTION AT LINE{lineno}"
                        break
                immed_binary=_12bitsigned(immed)

                fn3_binary=i_fn3[instruction]
                opcode_binary=i_opcode[instruction]

            BinaryInstruction=(
                immed_binary +
                rs1_binary +
                 fn3_binary +
                rd_binary +
                opcode_binary
            )

            binarycode.append(BinaryInstruction)



        elif instruction in stype:       

            if len(parts)!=3:
                print(f"SYNTAX ERROR FOR S TYPE INSTRUCTION AT LINE {lineno}")
                errorcode=f"SYNTAX ERROR FOR S TYPE INSTRUCTION AT LINE {lineno}"
                 
                errorcount=1
                break

            rs2=parts[1]   
            offsetpart=parts[2]

            if "(" not in offsetpart or ")" not in offsetpart:
                print(f"SYNTAX ERROR FOR S TYPE INSTRUCTION AT LINE {lineno}")
                errorcode=f"SYNTAX ERROR FOR S TYPE INSTRUCTION AT LINE {lineno}"
                 
                errorcount=1
                break

            immed=offsetpart[:offsetpart.index("(")]
            rs1=offsetpart[offsetpart.index("(")+1 : offsetpart.index(")")]

            if rs1 not in registers or rs2 not in registers:
                    print(f"INCORRECT REGISTER NAME AT LINE {lineno}")
                    errorcode=f"INCORRECT REGISTER NAME AT LINE {lineno}"
                    errorcount=1
                      
                    break

            rs1_binary=registers[rs1]
            rs2_binary=registers[rs2]
            value=int(immed)
            if value<-2048 or value>2047:
                print(f"IMMEDIATE VALUE OUT OF BOUNDS FOR S TYPE INSTRUCTION AT LINE{lineno}")
                errorcode=f"IMMEDIATE VALUE OUT OF BOUNDS FOR S TYPE INSTRUCTION AT LINE{lineno}"
                errorcount=1
                break
            immed_binary=_12bitsigned(immed)

        
            immed_5to11=immed_binary[:7]
            immed_0to4=immed_binary[7:]

            fn3_binary=s_fn3[instruction]
            opcode_binary=s_opcode[instruction]

            BinaryInstruction=(
            immed_5to11 +
            rs2_binary +
            rs1_binary +
            fn3_binary +
            immed_0to4 +
            opcode_binary
            )

            binarycode.append(BinaryInstruction)