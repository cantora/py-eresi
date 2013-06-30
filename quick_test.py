#!/usr/bin/env python

import eresi
import eresi.asm
import os

init_path = "%s/lib" % os.environ.get("HOME", "")
print("[*] searching for eresi in %s" % init_path)

eresi.init(init_path)
eresi.asm.init()

a = eresi.asm.Asm.ia32()

def log(s):
	for line in str(s).splitlines():
		print("\t"+line)

print "[*] try reading an x86 instruction and display some info"
log(repr(a))
i = a.read_instr("\x89\xe8")
log(repr(i))
log(len(i))
log(repr(i.mnemonic()))
log(repr(i.att(0)))

print("")
print("[*] now disassemble a list of bytes")
iseq = a.disassemble("\x52\x29\xc2\x89\xe8\xf7\xd0\x75\xfc\xc3")
log(repr(iseq))
log(repr(iseq[1:3]))
log(repr(iseq[1]))
log(repr([x.instr.operand_count() for x in iseq]))
log(repr([x.instr.types() for x in iseq]))
log(repr([len(x.instr) for x in iseq]))
log(repr([x.instr.bytes() for x in iseq]))
log(str(iseq))

print("")

