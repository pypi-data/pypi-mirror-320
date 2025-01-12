"""


bpy_prop_collection_idprop
^^^^^^^^^^^^^^^^^^^^^^^^^^

class bpy_prop_collection_idprop:

  """

  built-in class used for user defined collections.

  Note: Note that :class:`bpy.types.bpy_prop_collection_idprop` is not actually available from within Blender,
it only exists for the purpose of documentation.

  """

  def find(self, key: str) -> int:

    """

    Returns the index of a key in a collection or -1 when not found
(matches Python's string find function of the same name).

    """

    ...

  def foreach_get(self, attr: typing.Any, seq: typing.Any) -> None:

    """

    This is a function to give fast access to attributes within a collection.

    """

    ...

  def foreach_set(self, attr: typing.Any, seq: typing.Any) -> None:

    """

    This is a function to give fast access to attributes within a collection.

    """

    ...

  def get(self, key: str, default: typing.Any = None) -> None:

    """

    Returns the value of the item assigned to key or default when not found
(matches Python's dictionary function of the same name).

    """

    ...

  def items(self) -> typing.Any:

    """

    Return the identifiers of collection members
(matching Python's dict.items() functionality).

    """

    ...

  def keys(self) -> typing.List[str]:

    """

    Return the identifiers of collection members
(matching Python's dict.keys() functionality).

    """

    ...

  def values(self) -> typing.List[bpy.types.bpy_struct]:

    """

    Return the values of collection
(matching Python's dict.values() functionality).

    """

    ...

"""

import typing
