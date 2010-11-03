# -*- coding: utf-8 -*-
# This file is part of Dyko
# Copyright © 2008-2010 Kozea
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Kalamar.  If not, see <http://www.gnu.org/licenses/>.

"""
Site test.

Test registering access points to a Site.

"""

from nose.tools import eq_, raises

from kalamar import Site


class DummyAccessPoint(object):
    """Dummy access point for testing purpose."""
    properties = identity_properties = site = None


def test_simple_setup():
    """Setup a Site with a single access point, no exception raised."""
    site = Site()
    access_point = DummyAccessPoint()
    site.register("things", access_point)
    eq_(site.access_points, {"things": access_point})
    
@raises(RuntimeError)
def test_double_register():
    """Registering the same AP twice raises an exception."""
    site = Site()
    access_point = DummyAccessPoint()
    site.register("things", access_point)
    site.register("stuff", access_point)
    
@raises(RuntimeError)
def test_ap_name_conflict():
    """Registering two APs with the same name raises an exception."""
    site = Site()
    site.register("things", DummyAccessPoint())
    site.register("things", DummyAccessPoint())
    

