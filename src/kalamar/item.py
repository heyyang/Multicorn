# -*- coding: utf-8 -*-
# This file is part of Dyko
# Copyright © 2008-2009 Kozea
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
# along with Kalamar library.  If not, see <http://www.gnu.org/licenses/>.

"""This module contains base classes to make kalamar items.

You probably want to inherit from one of the followings :
 - CapsuleItem
 - AtomItem

"""

# This gotta change for a Storage class (undefined yet)
#from accesspoint import AccessPoint
import kalamar

class BaseItem:
    """An abstract class used by CapsuleItem and AtomItem.

    It represents every item you can get with kalamar.
    Data :
     - properties : acts like a defaultdict. The keys are strings and the values
       are python objects (for curious ones : this is a lazy implementation).
     - _access_point : where, in kalamar, is stored the item. It is an instance
       of AccessPoint.

    """

    def __init__(self, access_point, accessor_properties, opener):
        """Return an instance of BaseItem
        
        Parameters :
        - access_point : an instance of the AccessPoint class.
        - accessor_properties : properties generated by the accessor for this
          item.
        - opener : a function taking no parameters and returning file-like
          object.
        
        """
        self._opener = opener
        self._stream = None
        self.properties = ItemProperties(self, accessor_properties)
        self._access_point = access_point

    def matches(self, prop_name, operator, value):
        """Return boolean

        Check if the item's property <prop_name> matches <value> for the given
        operator.

        Availables operators are :
        - "=" -> equal
        - "!=" -> different
        - ">" -> greater than (alphabetically)
        - "<" -> lower than (alphabetically)
        - ">=" -> greater or equal (alphabetically)
        - "<=" -> lower or equal (alphabetically)
        - "~=" -> matches the given regexp
        - "~!=" -> does not match the given regexp
            availables regexp are python's re module's regexp

        Some descendants of Item class may overload _convert_value_type to get
        the "greater than/lower than" operators working with a numerical
        order (for instance).

        """

        prop_val = self.properties[prop_name]
        value = _convert_value_type(prop_name, value)
        
        try:
            kalamar.operators[operator](prop_val, value)
        except KeyError:
            raise OperatorNotAvailable(operator)

    def serialize(self):
        """Return the item serialized into a string"""
        raise NotImplementedError("Abstract class")

    def _convert_value_type(self, prop_name, value):
        """Do nothing by default"""
        return value
    
    @property
    def properties_aliases():
        """
        This is meant to hide the access_point to the ItemProperties class.
        """
        return access_point.properties_aliases

    @property
    def encoding(self):
        """Return a string

        Return the item's encoding, based on what the extractor can know from
        the items's data or, if unable to do so, on what is specified in the
        access_point.

        """
        return access_point.default_encoding

    def _read_property_from_data(self, prop_name):
        """Read a property form the item data and return a string

        If the property does not exist, returns None.
        ***This method have to be overloaded***

        """
        raise NotImplementedError("Abstract class")

    def _open(self):
        """Open the stream when called for the first time."""
        if not(self._stream):
            self._stream = self._opener()

class AtomItem(BaseItem):
    """An indivisible block of data
    
    This is an abstract class.
    
    """

    def read(self):
        """Alias for properties["_content"]"""
        return self.properties["_content"]

    def write(self, value):
        """Alias for properties["_content"] = value"""
        self.properties["_content"] = value

class CapsuleItem(BaseItem, list):
    """An ordered list of Items (atoms or capsules)

    A capsule is a multiparts item.
    This is an abstract class.

    """
    pass

class ItemProperties(dict):
    """A class that acts like a defaultdict used as a properties storage.

    You have to give a reference to the item to the constructor.
    You can force some properties to a value using the forced_values argument.
    
    >>> from _test.corks import CorkItem
    >>> item = CorkItem()
    >>> prop = ItemProperties(item, {"a" : "A", "b" : "B"})
    
    It works as a dictionnary :
    >>> prop["cork_prop"]
    'I am a cork prop'
    
    This key has been forced
    >>> prop["b"]
    'B'
    
    Return None if the key does not exist
    >>> prop["I do not exist"]
    
    If the item has aliases, they are resolved.
    >>> prop["I am aliased"]
    'I am not aliased'
    >>> prop ["I am not aliased"]
    'I am not aliased'

    """

    def __init__(self, item, forced_values = {}):
        self._item = item
        self.forced_values = forced_values

    def __getitem__(self, key):
        try:
            # forced_values are already aliased
            res = self.forced_values[key]
        except KeyError:
            try:
                res = super(ItemProperties, self).__getitem__(self._alias(key))
            except KeyError:
                self[self._alias(key)] = self._item._read_property_from_data(
                                                            self._alias(key))
                res = super(ItemProperties, self).__getitem__(self._alias(key))
        return res
    
    def _alias(self, prop_name):
        return self._item._properties_aliases.get(prop_name, prop_name)

