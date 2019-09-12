
from easypds4writer.private.pds4_object import PDS4Object

"""The Table Base class defines a heterogeneous repeating record of scalars. The Table Base class is the parent class
for all heterogeneous repeating record of scalars."""


class TableBase(PDS4Object):
    def __init__(self):
        super().__init__()
        # The offset attribute provides the displacement of the object starting position from the beginning of the
        # parent structure (file, record, etc.). If there is no displacement, offset=0
        #self._offset = 0

        # The records attribute provides a count of records.
        self._records = 0
        self._name = ""

    def reset(self):
        self._records = 0

