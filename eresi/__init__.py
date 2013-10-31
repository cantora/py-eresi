# Copyright 2013 anthony cantor
# This file is part of py-eresi.
# 
# py-eresi is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#  
# py-eresi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#  
# You should have received a copy of the GNU General Public License
# along with py-eresi.  If not, see <http://www.gnu.org/licenses/>.
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

class EresiDoesntImplement(PyEresiErr):
	''' 
	raise when a function of a library is invoked which isnt yet fully
	implemented by the ERESI library.
	'''
	pass

install_dir = None
bits = 64

def init(path, eresi_bits=64):
	global install_dir
	global bits

	install_dir = path
	if eresi_bits == 32:
		bits = 32
	elif eresi_bits == 64:
		bits = 64
	else:
		raise PyEresiErr("invalid bits value %r: must be 32 or 64")

def lib_paths(lib):
	global install_dir
	global bits

	if not install_dir:
		raise PyEresiErr("install location of eresi has not been set. " + \
							"call eresi.install_path(\"/path/to/eresi/libs\").")

	yield os.path.join(install_dir, lib + str(bits) + ".so")

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
		self.fn_map = {}

	@staticmethod
	def set_fn_attrs(fn_obj, arg_types, res_type):
		if arg_types:
			fn_obj.argtypes = arg_types
		if res_type:
			fn_obj.restype = res_type

	def prototype(self, fn_name, arg_types, res_type):
		if fn_name in self.fn_map:
			if self.fn_map[fn_name][0]:
				self.__class__.set_fn_attrs(self.fn_map[fn_name][0], arg_types, res_type)

			self.fn_map[fn_name] = (self.fn_map[fn_name][0], arg_types, res_type)
		else: 
			self.fn_map[fn_name] = (None, arg_types, res_type)
		
	def call(self, fn_name, *args):
		if fn_name not in self.fn_map:
			self.fn_map[fn_name] = (None, None, None)

		tpl = self.fn_map[fn_name]
		if not tpl[0]:
			try:
				fn_obj = self.handle.__getattr__(fn_name)
			except AttributeError as e:
				raise UnknownFn("unknown function %r in library %r: %s" % (fn_name, self.handle, e))

			self.fn_map[fn_name] = (fn_obj, tpl[1], tpl[2])
			self.__class__.set_fn_attrs(*self.fn_map[fn_name])

		return self.fn_map[fn_name][0](*args)
