from ctypes import *
from eresi import *

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
		return self.proc.__class__.instr_len(self.ei)
	
ARCH_IA32 = 0
ARCH_SPARC = 1
ARCH_MIPS = 2
ARCH_ARM = 3

class Asm(object):
	
	def __init__(self, arch):
		global libasm
		if not libasm:
			libasm = Library(eresi_lib("libasm"))

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

	@staticmethod
	def instr_len(e_instr):
		global libasm

		return libasm.call("asm_instr_len", pointer(e_instr))
