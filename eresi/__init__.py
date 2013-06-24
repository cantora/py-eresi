from ctypes import *
import os.path 
import eresi.aspect

class PyEresiErr(Exception):
	pass

class LibLoadErr(PyEresiErr):
	pass

class LibNotFound(PyEresiErr):
	pass

class UnknownFn(LibLoadErr):
	pass

class LibStatusErr(PyEresiErr):
	pass

install_dir = None

def install_path(path):
	global install_dir
	install_dir = path

def lib_paths(lib):
	global install_dir

	if not install_dir:
		raise PyEresiErr("install location of eresi has not been set. " + \
							"call eresi.install_path(\"/path/to/eresi/libs\").")

	for x in ["64", "32"]:
		yield os.path.join(install_dir, lib + x + ".so")

def eresi_lib(lib):
	if lib != "libaspect":
		eresi.aspect.init()

	return load_eresi_lib(lib)


def load_eresi_lib(lib):
	handle = None

	for path in lib_paths(lib):
		try:
			(open(path)).close()
		except IOError:
			continue

		try:
			print "path: %s" % path
			handle = CDLL(path, mode=RTLD_GLOBAL)
			break
		except OSError as e:
			raise LibLoadErr("failed to load %r: %s" % (lib, e))

	if not handle:
		raise LibNotFound("could not find eresi lib %r" % lib)

	return handle

class Library(object):
	def __init__(self, handle):
		self.handle = handle

	def call(self, fn_name, *args):
		try:
			return self.handle.__getattr__(fn_name)(*args)
		except AttributeError as e:
			raise UnknownFn("unknown function %r in library %r: %s" % (fn_name, self.handle, e))

