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
