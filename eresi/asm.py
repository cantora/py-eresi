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
		("ptr_instr", 			c_ubyte			),
		("proc",				c_void_p		),
		("name", 				c_void_p		),
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

class Instr(object):

	def __init__(self, eresi_instr, proc):
		self.ei = eresi_instr
		self.proc = proc

	def __len__(self):
		return instr_len(self.ei)
	
	def mnemonic(self):
		return self.proc.mnemonic(self.ei)

	def att(self):
		return att(self.ei, 0x8048000)


ARCH_IA32 = 0
ARCH_SPARC = 1
ARCH_MIPS = 2
ARCH_ARM = 3

def instr_len(e_instr):
	global libasm

	return libasm.call("asm_instr_len", pointer(e_instr))

def att(e_instr, addr):
	global libasm
	
	return libasm.call("asm_display_instr_att", pointer(e_instr), eresi.aspect.eresi_addr(addr))

class Asm(object):
	
	def __init__(self, arch):
		global libasm

		self.lib = libasm
		self.arch = arch
		self.proc = eresi_Processor()
		self.init_processor()

	def call(self, fn_name, *args):
		#print "call %s(%s)" % (fn_name, ", ".join([repr(x) for x in args]))
		return self.lib.call(fn_name, *args)

	def init_processor(self):
		result = self.call("asm_init_arch", pointer(self.proc), c_int(self.arch))

		if result != 1:
			raise LibStatusErr("error initializing asm processor: %r" % result)

			
	def read_instr(self, bytes):
		if len(bytes) < 1:
			return None

		l = c_uint(len(bytes))
		buf = (c_ubyte * l.value)(*[ord(b) for b in bytes])
		instr = eresi_Instr()

		result = self.call("asm_read_instr", pointer(instr), pointer(buf), l, pointer(self.proc))
		if result < 0:
			raise LibStatusErr("result from asm_read_instr was failure: %r" % result)

		return Instr(instr, self)


	def mnemonic(self, e_instr):
		return self.call(
			"asm_instr_get_memonic",
			pointer(e_instr), 
			pointer(self.proc)
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
		)
	}

	for (fn, proto) in protos.items():
		libasm.prototype(fn, *proto)

def init():
	global libasm
	libasm = Library(eresi_lib("libasm"))
	init_libasm_prototypes(libasm)
