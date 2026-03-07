import sys

InputFile=sys.argv[1]
OutputFile=sys.argv[2]


with open(InputFile, 'r') as filein:
    lines =filein.readlines()


assembly_codelines= []
for line in lines:
    line=line.strip()
    if line!="":
        assembly_codelines.append(line)

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

    if value<-2048 or value>2047:
        print("Syntax Error")
        exit()

    if value>=0:
        return format(value, "012b")
    else:
        return format((1<<12) + value, "012b")     
   
    
def _13bitsigned(value):
    value=int(value)     
    if value<-4096 or value>4095:
        print("Syntax Error")
        exit()

    if value>=0:
        return format(value, "013b")
    else:
        return format((1<<13) + value, "013b")

def _20bitsigned(value): 
    value=int(value)

    if value<-524288 or value>524287:
        print("Syntax Error")
        exit()

    if value>=0:
        return format(value, "020b")
    else:
        return format((1<<20) + value, "020b")

def _21bitsigned(value): 
    value=int(value)
    if value<-1048576 or value>1048574:
        print("Syntax Error")
        exit()

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
if end_instruction.endswith(":"):
    print("Syntax Error")
    errorcount=1



else:
    checkLine=end_instruction.replace(",", " ")
    parts=checkLine.split()

    if len(parts)!=4:
        print("Syntax Error")
        errorcount=1
        

    elif parts[0]!="beq" or parts[1]!="zero" or parts[2]!="zero":
        print("Syntax Error")
        errorcount=1
        

    elif parts[3]!=assembly_codelines[-2][:-1]:
        print("Syntax Error")
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
    for line in assembly_codelines:

        if line.endswith(":"):
            continue   

        line=line.replace(",", " ")
        parts=line.split()
        instruction=parts[0]

        if instruction in rtype:
            rd=parts[1]
            rs1=parts[2]
            rs2=parts[3]

            if rd not in registers or rs1 not in registers or rs2 not in registers:         
                print("Syntax Error")
                errorcount=1
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