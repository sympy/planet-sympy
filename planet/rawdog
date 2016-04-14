#!/usr/bin/env python
# rawdog: RSS aggregator without delusions of grandeur.
# Copyright 2003, 2004, 2005, 2006 Adam Sampson <ats@offog.org>
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

from rawdoglib.rawdog import main
import sys, os

def launch():
	sys.exit(main(sys.argv[1:]))

if __name__ == "__main__":
	if os.getenv("RAWDOG_PROFILE") is not None:
		import profile
		profile.run("launch()")
	else:
		launch()

