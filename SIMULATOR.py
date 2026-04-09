import sys
if len(sys.argv)!=3:
    print("Usage: python simulator.py input_binary.txt output_trace.txt")
    sys.exit()

inFile=sys.argv[1]
outFile=sys.argv[2]

with open(inFile, 'r') as f:
    input_lines=[l.strip() for l in f.readlines() if l.strip()]

errcount=0
errcode=""


if not input_lines:
    errcount=1
    errcode="EMPTY INPUT FILE"
    
if errcount==0:
    first=input_lines[0]
    if not (len(first)==32 and all(c in '01' for c in first)):
        errcount=1
        errcode=f"Error found in your assembly code: {first}"

trace=[]
dmb=0x00010000
dm=[0]*32
regs=[0]*32
regs[2]=0x0000017C
stack_mem=[0]*32

def signed32(val):
    val &= 0xFFFFFFFF
    if val>=0x80000000:
        val-=0x100000000
    return val

def unsigned(val):
    return val & 0xFFFFFFFF

def signxtnd(val, bits):
    sign_bit=1<<(bits - 1)
    if val & sign_bit:
        val-=(1<<bits)
    return val

def regW(rd, val):
    if rd!=0:
        regs[rd]=unsigned(val)

def fmtREG(val):
    return format(unsigned(val), '032b')

def mem_R(address):
    if address & 0x3:  
        return None, f"UNALIGNED MEMORY ACCESS: address {hex(address)}"
    
    if 0x00000100<=address<=0x0000017F:          
        idx=(address - 0x00000100) // 4
        return stack_mem[idx], None
    
    elif dmb<=address < dmb + 128: 
        idx=(address - dmb) // 4
        return dm[idx], None
    
    else:
        return None, f"MEMORY ACCESS OUT OF RANGE: address {hex(address)}"

def mem_W(address, val):
    val=unsigned(val)
    if address & 0x3: 
        return f"UNALIGNED MEMORY ACCESS: address {hex(address)}"
    
    if 0x00000100<=address<=0x0000017F:              
        idx=(address - 0x00000100) // 4
        stack_mem[idx]=val
        return None
    
    elif dmb<=address < dmb + 128:  
        idx=(address - dmb) // 4
        dm[idx]=val
        return None
    
    else:
        return f"MEMORY ACCESS OUT OF RANGE: address {hex(address)}"

def decode_r(bits):
    funct7=bits[0:7]
    rs2=int(bits[7:12],  2)
    rs1=int(bits[12:17], 2)
    funct3=bits[17:20]
    rd=int(bits[20:25], 2)
    return funct7, rs2, rs1, funct3, rd

def decode_i(bits):
    imm_raw=int(bits[0:12], 2)
    imm=signxtnd(imm_raw, 12)
    rs1=int(bits[12:17], 2)
    funct3=bits[17:20]
    rd=int(bits[20:25], 2)
    return imm, rs1, funct3, rd

def decode_s(bits):
    imm_raw=int(bits[0:7] + bits[20:25], 2)
    imm=signxtnd(imm_raw, 12)
    rs2=int(bits[7:12],  2)
    rs1=int(bits[12:17], 2)
    funct3=bits[17:20]
    return imm, rs2, rs1, funct3

def decode_b(bits):
    imm12=bits[0]
    imm10_5=bits[1:7]
    imm4_1=bits[20:24]
    imm11=bits[24]
    imm_raw=int(imm12 + imm11 + imm10_5 + imm4_1 + '0', 2)
    imm=signxtnd(imm_raw, 13)
    rs2=int(bits[7:12],  2)
    rs1=int(bits[12:17], 2)
    funct3=bits[17:20]
    return imm, rs2, rs1, funct3

def decode_u(bits):
    imm_raw=int(bits[0:20], 2)
    imm=signxtnd(imm_raw, 20)
    rd=int(bits[20:25], 2)
    return imm, rd

def decode_j(bits):
    imm20=bits[0]
    imm10_1=bits[1:11]
    imm11=bits[11]
    imm19_12=bits[12:20]
    imm_raw=int(imm20 + imm19_12 + imm11 + imm10_1 + '0', 2)
    imm=signxtnd(imm_raw, 21)
    rd=int(bits[20:25], 2)
    return imm, rd

def execute(pc, bits):
    opcode=bits[25:32]
    next_pc=pc + 4
    if opcode=='0110011':
        funct7, rs2, rs1, funct3, rd=decode_r(bits)
        a=signed32(regs[rs1])
        b=signed32(regs[rs2])
        ua=unsigned(regs[rs1])
        ub=unsigned(regs[rs2])
        if   funct3=='000' and funct7=='0000000': 
            result=a + b 

        elif funct3=='000' and funct7=='0100000': 
            result=a - b  

        elif funct3=='001':
            result=ua<<(ub & 0x1F) 

        elif funct3=='010':
            result=1 if a  <  b  else 0 

        elif funct3=='011': 
            result=1 if ua < ub  else 0  

        elif funct3=='100':
            result=ua ^ ub

        elif funct3=='101' and funct7=='0000000':
            result=ua>>(ub & 0x1F)

        elif funct3=='110': 
            result=ua | ub  

        elif funct3=='111':
            result=ua & ub  
                       
        regW(rd, result)
        
    elif opcode=='0010011':
        imm, rs1, funct3, rd=decode_i(bits)
        a =signed32(regs[rs1])
        ua=unsigned(regs[rs1])
        if   funct3=='000':result=a + imm                            
        elif funct3=='011': result=1 if ua < unsigned(imm) else 0  
        regW(rd, result)
        
    elif opcode=='0000011':
        imm, rs1, funct3, rd=decode_i(bits)
        address=unsigned(regs[rs1] + imm)
        val, err=mem_R(address)
        if err:
            return None, err
        
        regW(rd, val)

    elif opcode=='0100011':
        imm, rs2, rs1, funct3=decode_s(bits)
        address=unsigned(regs[rs1] + imm)
        err=mem_W(address, regs[rs2])
        if err:
            return None, err

    elif opcode=='1100011':
        imm, rs2, rs1, funct3=decode_b(bits)
        a=signed32(regs[rs1])
        b=signed32(regs[rs2])
        ua=unsigned(regs[rs1])
        ub=unsigned(regs[rs2])
        if rs1==0 and rs2==0 and imm==0:
            return None, None
        branch=False
        if   funct3=='000': branch=(a ==b)  
        elif funct3=='001':branch=(a !=b)   
        elif funct3=='100':branch=(a <b)  
        elif funct3=='101': branch=(a >=b)   
        elif funct3=='110': branch=(ua< ub) 
        elif funct3=='111':branch=(ua>=ub)  
        if branch:
            next_pc=pc + imm
            
    elif opcode=='0110111':
        imm, rd=decode_u(bits)
        regW(rd, imm<<12)

    elif opcode=='0010111':
        imm, rd=decode_u(bits)
        regW(rd, pc + (imm<<12))

    elif opcode=='1101111':
        imm, rd=decode_j(bits)
        regW(rd, pc + 4)
        next_pc=(pc + imm) & ~1
        
    elif opcode=='1100111':
        imm, rs1, funct3, rd=decode_i(bits)
        new_pc=(unsigned(regs[rs1]) + imm) & ~1
        regW(rd, pc + 4)
        next_pc=new_pc
    
    return next_pc, None

pc_to_instr_map={}

if errcount==0:
    for idx, bits in enumerate(input_lines):
        pc_to_instr_map[idx*4]=bits
    pc=0
    while True:
        if pc not in pc_to_instr_map:
            errcount=1
            errcode=f"PC OUT OF PROGRAM RANGE: {hex(pc)} - POSSIBLE MISSING VIRTUAL HALT"
            break

        bits=pc_to_instr_map[pc]
        next_pc, err=execute(pc, bits)
        if err:
            errcount=1
            errcode=err
            break

        if next_pc is None:
            break

        pc=next_pc

        pc_bin_str=format(pc, '032b')
        reg_str=' '.join(fmtREG(regs[i]) for i in range(32))
        trace.append(f"{pc_bin_str} {reg_str}")

with open(outFile, 'w') as f:
    for line in trace:
        f.write(line + '\n')

    if errcount != 0:
        print(errcode)

    else:
        for i in range(32):
            addr=dmb + i * 4
            val=dm[i]
            f.write(f"{hex(addr)}:{format(val, '032b')}\n")
        print("SIMULATOR RAN SUCCESSFULLY")
