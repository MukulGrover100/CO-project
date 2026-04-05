import sys
if len(sys.argv) != 3:
    print("Usage: python simulator.py input_binary.txt output_trace.txt")
    sys.exit()

inFile  = sys.argv[1]
outFile = sys.argv[2]

with open(inFile, 'r') as f:
    raw_lines = [l.strip() for l in f.readlines() if l.strip()]

errcount = 0
errcode  = ""


if not raw_lines:
    errcount = 1
    errcode  = "EMPTY INPUT FILE"
trace=[]
dmb=0x00010000
dm=[]

with open(outFile, 'w') as f:
    if errcount != 0:
        print(errcode)
        f.write(errcode + '\n')
    else:
        for line in trace:
            f.write(line + '\n')
        for i in range(32):
            addr  = dmb + i * 4
            value = dm[i]
            f.write(f"{hex(addr)}:{format(value, '032b')}\n")

def decode_r(bits):
    funct7 = bits[0:7]
    rs2 = int(bits[7:12], 2)
    rs1 = int(bits[12:17], 2)
    funct3 = bits[17:20]
    rd = int(bits[20:25], 2)
    return funct7, rs2, rs1, funct3, rd

def decode_i(bits):
    imm_raw = int(bits[0:12], 2)
    imm = sign_extend(imm_raw, 12)
    rs1 = int(bits[12:17], 2)
    funct3 = bits[17:20]
    rd = int(bits[20:25], 2)
    return imm, rs1, funct3, rd

def decode_s(bits):
    imm_raw = int(bits[0:7] + bits[20:25], 2)
    imm = sign_extend(imm_raw, 12)
    rs2 = int(bits[7:12], 2)
    rs1 = int(bits[12:17], 2)
    funct3 = bits[17:20]
    return imm, rs2, rs1, funct3

def decode_b(bits):
    imm12   = bits[0]
    imm10_5 = bits[1:7]
    imm4_1  = bits[20:24]
    imm11   = bits[24]
    imm_raw = int(imm12 + imm11 + imm10_5 + imm4_1 + '0', 2)
    imm     = sign_extend(imm_raw, 13)
    rs2     = int(bits[7:12],  2)
    rs1     = int(bits[12:17], 2)
    funct3  = bits[17:20]
    return imm, rs2, rs1, funct3

def decode_u(bits):
    imm_raw = int(bits[0:20], 2)
    imm     = sign_extend(imm_raw, 20)
    rd      = int(bits[20:25], 2)
    return imm, rd

def decode_j(bits):
    imm20    = bits[0]
    imm10_1  = bits[1:11]
    imm11    = bits[11]
    imm19_12 = bits[12:20]
    imm_raw  = int(imm20 + imm19_12 + imm11 + imm10_1 + '0', 2)
    imm      = sign_extend(imm_raw, 21)
    rd       = int(bits[20:25], 2)
    return imm, rd

def execute(pc, bits):
    opcode  = bits[25:32]
    next_pc = pc + 4

    
    if opcode == '0110011':
        funct7, rs2, rs1, funct3, rd = decode_r(bits)
        a  = to_signed_32(regs[rs1])
        b  = to_signed_32(regs[rs2])
        ua = to_unsigned(regs[rs1])
        ub = to_unsigned(regs[rs2])

        if   funct3 == '000' and funct7 == '0000000':  result = a + b               
        elif funct3 == '000' and funct7 == '0100000':  result = a - b               
        elif funct3 == '001':  result = ua << (ub & 0x1F)   
        elif funct3 == '010':  result = 1 if a  <  b  else 0  
        elif funct3 == '011':  result = 1 if ua < ub  else 0  
        elif funct3 == '100':  result = ua ^ ub             
        elif funct3 == '101' and funct7 == '0000000':  result = ua >> (ub & 0x1F)   
        elif funct3 == '110':  result = ua | ub            
        elif funct3 == '111':  result = ua & ub             

        reg_write(rd, result)

    
    elif opcode == '0010011':
        imm, rs1, funct3, rd = decode_i(bits)
        a  = to_signed_32(regs[rs1])
        ua = to_unsigned(regs[rs1])

        if   funct3 == '000':  result = a + imm                           
        elif funct3 == '011':  result = 1 if ua < to_unsigned(imm) else 0 

        reg_write(rd, result)


    elif opcode == '0000011':
        imm, rs1, funct3, rd = decode_i(bits)
        address = to_unsigned(regs[rs1] + imm)
        value, err = mem_read(address)
        if err:
            return None, err
        reg_write(rd, value)
    elif opcode == '1100011':
        imm, rs2, rs1, funct3 = decode_b(bits)
        a  = to_signed_32(regs[rs1])
        b  = to_signed_32(regs[rs2])
        ua = to_unsigned(regs[rs1])
        ub = to_unsigned(regs[rs2])
        if rs1 == 0 and rs2 == 0 and imm == 0:
            return None, None
        branch = False
        if   funct3 == '000':  branch = (a  == b)   # beq
        elif funct3 == '001':  branch = (a  != b)   # bne
        elif funct3 == '100':  branch = (a  <  b)   # blt
        elif funct3 == '101':  branch = (a  >= b)   # bge
        elif funct3 == '110':  branch = (ua <  ub)  # bltu
        elif funct3 == '111':  branch = (ua >= ub)  # bgeu

        if branch:
            next_pc = pc + imm

    elif opcode == '0110111':
        imm, rd = decode_u(bits)
        reg_write(rd, imm << 12)

    elif opcode == '0010111':
        imm, rd = decode_u(bits)
        reg_write(rd, pc + (imm << 12))

    elif opcode == '1101111':
        imm, rd = decode_j(bits)
        reg_write(rd, pc + 4)
        next_pc = (pc + imm) & ~1

    elif opcode == '1100111':
        imm, rs1, funct3, rd = decode_i(bits)
        new_pc = (to_unsigned(regs[rs1]) + imm) & ~1
        reg_write(rd, pc + 4)
        next_pc = new_pc
    return next_pc, None
