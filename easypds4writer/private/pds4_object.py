
class PDS4Object():
    _already_being_written= False
    _offset= -1

    def __init__(self):
        self._fp_data_file= None

    def set_file_pointers(self, fp_data_file):
        self._fp_data_file = fp_data_file

    def _update_start_end_bytes(self):
        if not self._already_being_written:
            self._already_being_written= True
            self._start_byte= self._fp_data_file.tell()

    def reset(self):
        # All types of objects must implement a method reset that resets all attributes that are variable for each
        # instance of the object. For example the "records" has to be reset to 0 every time a new use is made of the
        # TableCharacterObject in a new product instance (product file), otherwise the number of records in the second
        # file will continue the count from the previous file.
        raise NotImplementedError()

