from ctypes import *
from eresi import *

#asm.init() must be called before this module can be used.
libasm = None 

class eresi_Processor(Structure):
	_fields_ = [
		("resolve_immediate", 	c_void_p	),
		("resolve_data", 		c_void_p	),
		("type",				c_int		),
		("instr_table",			c_void_p	),
		("fetch",				c_void_p	),
		("display_handle",		c_void_p	),
		("internals",			c_void_p	),
		("error_code",			c_int		)
	]

class eresi_Operand(Structure):
	_fields_ = [
		("len", 				c_uint		),
		("ptr",					c_void_p	),
		("type",				c_uint		),
		("name",				c_void_p	),
		("size",				c_uint		),
		("content",				c_uint		),
		("regset",				c_int		),
		("prefix",				c_int		),
		("imm",					c_int		),
		("baser",				c_int		),
		("indexr",				c_int		),
		("sbaser",				c_void_p	),
		("sindex",				c_void_p	),
		("destination",			c_int		),
		("address_space",		c_int		),
		("scale",				c_uint		),
		("shift_type",			c_uint		),
		("indexing",			c_uint		),
		("offset_added",		c_uint		)
	]

class eresi_Instr(Structure):
	_fields_ = [
		("ptr_instr", 			c_void_p		),
		("proc",				c_void_p		),
		("name", 				c_char_p		),
		("instr",				c_int			),
		("type",				c_int			),
		("prefix",				c_int			),
		("spdiff",				c_int			),
		("flagswritten",		c_int			),
		("flagsread",			c_int			),
		("ptr_prefix",			c_void_p		),
		("annul",				c_int			),
		("prediction",			c_int			),
		("nb_op",				c_int			),
		("op",					eresi_Operand*6	),
		("len",					c_uint			),
		("arith",				c_uint			)
	]


def matching_flags(flag_dict, value):
	matches = []
	for (name, bit) in flag_dict.items():
		if (value & bit):
			matches.append(name)

	return set(matches)


class Operand(object):
	
	TYPES = {
		'NONE':	0x0, # Undefined operand type
		'IMM':	0x1, # Immediate operand type
		'REG':	0x2, # Register operand type
		'MEM':	0x4  # Memory access operand type
	}

	def __init__(self, e_operand):
		self.eop = e_operand

	def __len__(self):
		return self.eop.len

	def types(self):
		raise EresiDoesntImplement("operand types dont seem to be accurate")
		return matching_flags(self.__class__.TYPES, self.eop.type)

	def type(self):
		return operand_type_string(self.eop.type)

	def name(self):
		return str(self.eop.name)

class Instr(object):

	TYPES = {
		'NONE':				0x0, # Undefined instruction type.
		'BRANCH':			0x1, # Branching instruction.
		'CALLPROC':			0x2, # Sub Procedure calling instruction.
		'RETPROC':			0x4, # Return instruction
		'ARITH':			0x8, # Arithmetic (or logic) instruction.
		'LOAD':				0x10, # Instruction that reads from memory.
		'STORE':			0x20, # Instruction that writes in memory.
		'ARCH':				0x40, # Architecture dependent instruction.
		'WRITEFLAG':		0x80, # Flag-modifier instruction.
		'READFLAG':			0x100, # Flag-reader instruction.
		'INT':				0x200, # Interrupt/call-gate instruction.
		'ASSIGN':			0x400, # Assignment instruction.
		'COMPARISON':		0x800, # Instruction that performs comparison or test.
		'CONTROL':			0x1000, # Instruction modifies control registers.
		'NOP':				0x2000, # Instruction that does nothing.
		'TOUCHSP':			0x4000, # Instruction modifies stack pointer.
		'BITTEST':			0x8000, # Instruction investigates values of bits in the operands.
		'BITSET':			0x10000, # Instruction modifies values of bits in the operands.
		'INCDEC':			0x20000, # Instruction does an increment or decrement
		'PROLOG':			0x40000, # Instruction creates a new function prolog
		'EPILOG':			0x80000, # Instruction creates a new function epilog
		'STOP':				0x100000, # Instruction stops the program
		'IO':				0x200000, # Instruction accesses I/O locations (e.g. ports).
		'CONDCONTROL':		0x400000, # Instruction executes conditionally.
		'INDCONTROL':		0x800000, # Instruction changes control indirectly.
		'OTHER':			0x1000000 # Type that doesn't fit the ones above.
	}

	ARITH_TYPES = {
		'ADD':		0x1,
		'SUB':		0x2,
		'MUL':		0x4,
		'DIV':		0x8,
		'OR':		0x10,
		'XOR':		0x20,
		'AND':		0x40,
		'SL':		0x80,
		'SR':		0x100,
		'NOT':		0x200
	}

	def __init__(self, eresi_instr, op_buf, proc):
		self.ei = eresi_instr
		self.proc = proc
		self.op_buf = op_buf

	def __len__(self):
		return instr_len(self.ei)
	
	def bytes(self):
		return string_at(self.ei.ptr_instr, len(self))

	def mnemonic(self):
		return self.proc.mnemonic(self.ei)

	def att(self, addr):
		return att(self.ei, addr)

	def __repr__(self):
		return repr(self.att(0))

	def __str__(self):
		return self.att(0)

	def operand_count(self):
		return operand_count(self.ei)

	def operands(self):
		for i in xrange(0, self.operand_count()):
			yield Operand(self.ei.op[i])

	def types(self):
		return matching_flags(
			self.__class__.TYPES,
			self.ei.type
		)

	def is_type(self, t):
		return ((self.ei.type & self.__class__.TYPES[t]) != 0)

	def arith_types(self):
		if self.proc.is_ia32():
			raise EresiDoesntImplement("eresi doesnt seem to mark the arith type correctly for ia32")

		if self.is_arith(): #this method is dynamically generated below
			return matching_flags(
				self.__class__.ARITH_TYPES,
				self.ei.arith
			)
		
		return set([])

	@staticmethod
	def add_type_check_method(t):
		def tmp(self):
			return self.is_type(t)
		
		tmp.__name__ = "is_%s" % t.lower()
		setattr(Instr, tmp.__name__, tmp)
		
	
for t in Instr.TYPES:
	Instr.add_type_check_method(t)

ARCH_IA32 = 0
ARCH_SPARC = 1
ARCH_MIPS = 2
ARCH_ARM = 3

def instr_len(e_instr):
	global libasm

	return libasm.call("asm_instr_len", byref(e_instr))

def att(e_instr, addr):
	global libasm
	
	return libasm.call("asm_display_instr_att", byref(e_instr), eresi.aspect.eresi_addr(addr))

def operand_count(e_instr):
	global libasm

	return libasm.call(
		"asm_operand_get_count", 
		byref(e_instr), 
		c_int(0),
		c_int(0),
		c_void_p(0)
	)

def operand_type_string(typ):
	global libasm

	return libasm.call(
		"asm_operand_type_string", 
		c_int(typ)
	)

class InstrSeqMember(object):
	def __init__(self, base, offset, instr):
		self.base = base
		self.offset = offset
		self.instr = instr

	def __repr__(self):
		return repr((
			self.base,
			self.offset,
			self.instr
		))

	def __str__(self):
		addr_fmt = "%08x"
		addr = self.base+self.offset
		
		return "%4s%-16s%2s%-16s%s%s" % (
			"", addr_fmt % (addr),
			"", "".join(map(lambda b: "%02x" % ord(b), self.instr.bytes())),
			self.instr.att(addr), ""
		)

	
class InstrSeq(object):
	def __init__(self, base, instr_list):
		self.ilist = instr_list

		self.base = 0
		self.base_addr(base)

	def base_addr(self, new_base = None):
		if new_base:
			if new_base < 0:
				raise ValueError("invalid base addr %d" % new_base)
			self.base = new_base

		return self.base

	def __len__(self):
		return len(self.ilist)

	def __repr__(self):
		return repr((
			self.base,
			self.ilist
		))

	def __str__(self):
		return "\n".join([
			str(x) for x in self
		])

	def __list__(self):
		return [x for x in self]

	def __contains__(self, item):
		return list(self).__contains__(item)

	def __iter__(self):
		offset = 0
		
		for instr in self.ilist:
			yield InstrSeqMember(self.base, offset, instr)
			offset += len(instr)

	def __getitem__(self, key):
		if type(key) is int:
			return self.nth_instr(key)

		elif type(key) is slice:
			arr = [x for x in self].__getitem__(key)

			#it doesnt make sense to have an empty instruction sequence
			#slice because we cant determine the base address
			if len(arr) < 1: 
				raise KeyError("slice results in an empty instruction sequence")

			return InstrSeq(
				arr[0].base + arr[0].offset,
				[x.instr for x in arr]
			)


		raise TypeError("invalid key: %r" % key)

	def nth_instr(self, n):
		i = 0

		if n < 0 or n >= len(self.ilist):
			return IndexError("index %d out of range" % n)

		for ismember in self:
			if i == n:
				return ismember
			i += 1

		raise Exception("shouldnt get here")


class DisassembleErr(PyEresiErr):
	
	def __init__(self, msg, bytes, offset):
		super(PyEresiErr, self).__init__(msg)
		self.bytes = bytes
		self.offset = offset


class Asm(object):
	
	def __init__(self, arch):
		global libasm

		self.lib = libasm
		self.proc = eresi_Processor()
		self.init_processor(arch)

	@staticmethod
	def ia32():
		return Asm(ARCH_IA32)

	def arch(self):
		return int(self.proc.type)

	def is_ia32(self):
		return (self.arch() == ARCH_IA32)

	def call(self, fn_name, *args):
		#print "call %s(%s)" % (fn_name, ", ".join([repr(x) for x in args]))
		return self.lib.call(fn_name, *args)

	def init_processor(self, arch):
		result = self.call("asm_init_arch", byref(self.proc), c_int(arch))

		if result != 1:
			raise LibStatusErr("error initializing asm processor: %r" % result)

	def disassemble(self, bytes):
		ins = []
		amt_read = 0
		blen = len(bytes)

		while amt_read < blen:
			try:
				instr = self.read_instr(bytes[amt_read:])
			except LibStatusErr as e:
				raise DisassembleErr(
					"error disassembling at offset %d: %s" % (amt_read, e),
					bytes,
					amt_read
				)
					
			amt_read += len(instr)
			ins.append(instr)

		return InstrSeq(0, ins)

	def read_instr(self, bytes):
		if len(bytes) < 1:
			return None

		l = c_uint(len(bytes))
		buf = (c_ubyte * l.value)(*[ord(b) for b in bytes])
		instr = eresi_Instr()

		result = self.call("asm_read_instr", byref(instr), byref(buf), l, byref(self.proc))
		if result < 0:
			raise LibStatusErr("result from asm_read_instr was failure: %r" % result)

		return Instr(instr, buf, self)


	def mnemonic(self, e_instr):
		return self.call(
			"asm_instr_get_memonic",
			byref(e_instr), 
			byref(self.proc)
		)


##### init this module ####

def init_libasm_prototypes(libasm):
	protos = {
		"asm_init_arch": (
			[c_void_p, c_int],
			c_int
		),

		"asm_read_instr": (
			[c_void_p, c_void_p, c_uint, c_void_p],
			c_int
		),

		"asm_instr_get_memonic": (
			[c_void_p, c_void_p],
			c_char_p
		),

		"asm_display_instr_att": (
			[c_void_p, eresi.aspect.eresi_addr_class()],
			c_char_p
		),
	
		"asm_operand_get_count": (
			[c_void_p, c_int, c_int, c_void_p],
			c_int
		),
	
		"asm_operand_type_string": (
			[c_int],
			c_char_p
		)
	}

	for (fn, proto) in protos.items():
		libasm.prototype(fn, *proto)

def init():
	global libasm
	libasm = Library(eresi_lib("libasm"))
	init_libasm_prototypes(libasm)
