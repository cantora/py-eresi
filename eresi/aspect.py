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

