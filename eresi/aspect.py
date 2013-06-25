from ctypes import *
import eresi

aspect = None

def eresi_addr(num):
	return eresi_addr_class()(num)

def eresi_addr_class():
	if eresi.bits == 32:
		return c_uint32
	else:
		return c_uint64
	
def init():
	global aspect
	
	if not aspect:
		aspect = eresi.Library(eresi.eresi_lib("libaspect"))
		
		result = call("aspect_init")
		if result != 0:
			raise eresi.LibStatusErr("failed to initialize libaspect: %r" % result)
	
	
def call(fn_name, *args):
	global aspect

	return aspect.call(fn_name, *args)

