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
