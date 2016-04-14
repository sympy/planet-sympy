# plugins: handle add-on modules for rawdog.
# Copyright 2004, 2005, 2013 Adam Sampson <ats@offog.org>
#
# rawdog is free software; you can redistribute and/or modify it
# under the terms of that license as published by the Free Software
# Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# rawdog is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with rawdog; see the file COPYING. If not, write to the Free
# Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA, or see http://www.gnu.org/.

# The design of rawdog's plugin API was inspired by Stuart Langridge's
# Vellum weblog system:
#   http://www.kryogenix.org/code/vellum/

import imp
import os

class Box:
	"""Utility class that holds a mutable value. Useful for passing
	immutable types by reference."""
	def __init__(self, value=None):
		self.value = value

plugin_count = 0

def load_plugins(dir, config):
	global plugin_count

	try:
		files = os.listdir(dir)
	except OSError:
		# Ignore directories that can't be read.
		return

	for file in files:
		if file == "" or file[0] == ".":
			continue

		desc = None
		for d in imp.get_suffixes():
			if file.endswith(d[0]) and d[2] == imp.PY_SOURCE:
				desc = d
		if desc is None:
			continue

		fn = os.path.join(dir, file)
		config.log("Loading plugin ", fn)
		f = open(fn, "r")
		imp.load_module("plugin%d" % (plugin_count,), f, fn, desc)
		plugin_count += 1
		f.close()

attached = {}

def attach_hook(hookname, func):
	"""Attach a function to a hook. The function should take the
	appropriate arguments for the hook, and should return either True or
	False to indicate whether further functions should be processed."""
	attached.setdefault(hookname, []).append(func)

def call_hook(hookname, *args):
	"""Call all the functions attached to a hook with the given
	arguments, in the order they were added, stopping if a hook function
	returns False. Returns True if any hook function returned False (i.e.
	returns True if any hook function handled the request)."""
	for func in attached.get(hookname, []):
		if not func(*args):
			return True
	return False

