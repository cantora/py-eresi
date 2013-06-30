#!/usr/bin/env python

import eresi
import eresi.asm
import os

init_path = "%s/lib" % os.environ.get("HOME", "")
print("[*] searching for eresi in %s" % init_path)

eresi.init(init_path)
eresi.asm.init()

a = eresi.asm.Asm.ia32()

def log(s, hdr=""):
	if len(hdr) > 0:
		print("  %s:" % hdr)
	for line in str(s).splitlines():
		print("    "+line)

print "[*] try reading an x86 instruction and display some info"
log(repr(a), "assembler")
i = a.read_instr("\x89\xe8")
log(repr(i), "instruction")
log(len(i), "instr len")
log(repr(i.mnemonic()), "instr mnemonic")
log(repr(i.att(0)), "att disassembly @0x0")

print("")
print("[*] now disassemble a list of x86 bytes")
iseq = a.disassemble("\x52\x29\xc2\x89\xe8\xf7\xd0\x75\xfc\xc3")
log(repr(iseq), "instr sequence")
log(repr(iseq[1:3]), "instr seq slice")
log(repr(iseq[1]), "instr seq item")
log(repr([x.instr.operand_count() for x in iseq]), "operand counts for instructions")
log(repr([x.instr.types() for x in iseq]), "types of instructions")
log(repr([len(x.instr) for x in iseq]), "lengths of instructions")
log(repr([x.instr.bytes() for x in iseq]), "bytes of instructions")
log(str(iseq), "disassembly of instructions")

print("")

a = eresi.asm.Asm.arm()
print("")
print("[*] now disassemble a list arm of bytes")
iseq = a.disassemble((
	"00482DE904B08DE210D04DE210000BE5" + \
	"14100BE534309FE5003093E50300A0E1" + \
	"0210A0E328209FE5DA4C00EB08000BE5" + \
	"08001BE51C109FE51C209FE57C4F00EB" + \
	"0030A0E30300A0E104D04BE20088BDE8" + \
	"D471020030E60100FC8D000038E60100"
).decode("hex"))

log(repr(iseq), "instr sequence")
log(repr(iseq[1:3]), "instr seq slice")
log(repr(iseq[1]), "instr seq item")
log(repr([x.instr.operand_count() for x in iseq]), "operand counts for instructions")
log(repr([x.instr.types() for x in iseq]), "types of instructions")
log(repr([len(x.instr) for x in iseq]), "lengths of instructions")
log(repr([x.instr.bytes() for x in iseq]), "bytes of instructions")
log(str(iseq), "disassembly of instructions")

print("")
