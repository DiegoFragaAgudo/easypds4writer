
from collections import namedtuple

from easypds4writer.private.table_base import TableBase

"""The Table Character class is an extension of table base and defines a simple character table."""

class TableCharacter(TableBase):
    def __init__(self, name = ""):
        super().__init__()
        # The record_delimiter attribute provides the character or characters used to indicate the end of a record.
        # Records in the delimited table are delimited by ASCII carriage-return line-feed pairs (0x0D_0x0A)
        self._record_delimiter = "Carriage-Return Line-Feed"
        # The Record_Character class is a component of the table class and defines a record of the table.
        self._record_character = RecordCharacter()
        self._name = name

    """This function adds a new field definition to the record. This implies appending a new field_character object
    to the record_character object"""
    def declare_field(self, field_format, data_type, name, unit, description):
        # Pending to implement validation of inputs
        self._record_character.fields += 1
        field_character=             FieldCharacter()
        field_character.name=        name
        field_character.data_type=   data_type

        # When this is done field_format is validated and exceptions raised if needed
        field_character.field_format=field_format

        field_character.unit = unit
        field_character.description = description
        self._record_character.field_character.append(field_character)

    """"Writes in the data file a new record (line of text). To do that it has to format the inputs into a single line
    of text and end the line with appropriate line ending (e.g. CR LF)"""
    def add_record(self, record):
        # TODO. Validate inputs
        #    - if it is a list and the number of items matches the number and type of the fields)
        #    - If the size of the number or string fits in the space defined in the field format etc

        # Check if it is the first time new data is written in this object and if so change the status of
        # _already_being_written variable and save which is the byte number of the beginning of the object (offset)
        if not self._already_being_written:
            self._already_being_written = True
            self._offset= self._fp_data_file.tell()

        # Prepare a template for the record where the values will be substituted. Example of a template
        # with two strings and one number: %-23s, %+6s, %7.3f
        i= 0
        formatted_record_template= ""
        for field in record:
            # Check that the provided value fits in the field width and raise a exception if not
            field_width = int(self._record_character.field_character[i].parsed_field_format.width)
            field_format = self._record_character.field_character[i].field_format
            formatted_field= field_format % field
            if len(formatted_field) > field_width:
                error_message = "Value %s is wider than the width of field %s which is %d" % (formatted_field, self._record_character.field_character[i].name, field_width)
                raise PDS4meInputError(field, error_message)

            # Concatenate field formats
            if i==0:
                formatted_record_template = field_format
            else:
                formatted_record_template = formatted_record_template + ", " + field_format
            i= i+1

        # Add line ending
        # \n is supposed to introduce a CR LF line ending in both Windows and Linus if the file was opened with
        # the parameter newline='\r\n'
        formatted_record_template += "\n"
        formatted_record= formatted_record_template % record

        # Write the formatted record to the file
        self._fp_data_file.write(formatted_record)

        # Calculate the record length including the line ending character. len function only counts one character as
        # line ending when actually there are two that is way +1 is added
        self._record_character._record_length= len(formatted_record) + 1
        self._records = self._records + 1

    def writte_label(self, child, ET):

        # Write Table_Character and its children

        table_character = ET.SubElement(child, "Table_Character")

        offset = ET.SubElement(table_character, "offset")
        offset.text = str(self._offset)
        offset.set('unit', 'byte')

        records = ET.SubElement(table_character, "records")
        records.text = str(self._records)

        record_delimiter = ET.SubElement(table_character, "record_delimiter")
        record_delimiter.text = self._record_delimiter

        # Write Record_Character and its children

        record_character = ET.SubElement(table_character, "Record_Character")

        fields = ET.SubElement(record_character, "fields")
        fields.text = str(self._record_character.fields)

        groups = ET.SubElement(record_character, "groups")
        groups.text = '0'

        record_length = ET.SubElement(record_character, "record_length")
        record_length.text = str(self._record_character._record_length)
        record_length.set('unit', 'byte')

        # Write the Record_Character objectS and its children. There will be as many as fields (columns) in the table

        # The field_number attribute provides the position of a field, within a series of fields, counting from 1
        field_number= 1

        # The field_location attribute provides the starting byte for a field within a record or group,
        # counting from '1'
        field_location= 1

        for field_character in self._record_character.field_character:

            field_character_xml = ET.SubElement(record_character, "Field_Character")

            name = ET.SubElement(field_character_xml, "name")
            name.text = field_character.name

            field_number_xml = ET.SubElement(field_character_xml, "field_number")
            field_number_xml.text = str(field_number)

            field_location_xml = ET.SubElement(field_character_xml, "field_location")
            field_location_xml.text = str(field_location)
            field_location_xml.set('unit', 'byte')

            data_type = ET.SubElement(field_character_xml, "data_type")
            data_type.text = field_character.data_type

            # parsed_field_format= self._parse_field_format(field_character.field_format)

            # field_length= parsed_field_format.width
            field_length = field_character.parsed_field_format.width
            field_length_xml = ET.SubElement(field_character_xml, "field_length")
            field_length_xml.text = field_length
            field_length_xml.set('unit', 'byte')

            field_format = ET.SubElement(field_character_xml, "field_format")
            field_format.text = field_character.field_format

            unit = ET.SubElement(field_character_xml, "unit")
            unit.text = field_character.unit

            description = ET.SubElement(field_character_xml, "description")
            description.text = field_character.description

            field_number = field_number + 1
            field_location= field_location + int(field_length) + 2 #The 2 is for two field delimiter characters ", ". To be removed the hard coding of this value

"""The Record_Character class is a component of the table class and defines a record of the table."""
class RecordCharacter:
    def __init__(self):
        # The fields attribute provides a count of the total number of scalar fields directly associated with a table
        # record. Fields within groups within the record are not included in this count.
        self.fields = 0
        self._groups = 0  # 0 It is a PDS4Me choice not to use groups TBC
        # The record_length attribute provides the length of a record, including the record delimiter.
        self._record_length = 0
        self.field_character = []
        self._group_field_character = []


"""The Field_Character class defines a field of a character record or a field of a character group."""
class FieldCharacter:
    def __init__(self):
        self.name = ""
        self._data_type = ""
        self.unit = ""           # This attribute is PDS4 optional but PDS4Me mandatory
        self.description = ""    # This attribute is PDS4 optional but PDS4Me mandatory

    @property
    def field_format(self):
        return self._field_format

    @field_format.setter
    def field_format(self, field_format):
        self._field_format = field_format
        self.parsed_field_format= self._parse_field_format(field_format)


    def _parse_field_format(self, field_format):
        """Parses and validates a field_format. It will produce exceptions if not valid

        Attributes:
            field_format: should have the format %[+|-]width[.precision]specifier
        Return: Named temple
                  parsed_field_format.sign: +, - or empty (not specified)
                  parsed_field_format.width: Width including all characters and the decimal point
                  parsed_field_format.precision: a positive integer or 0 if not specified
                  parsed_field_format.specifier: A valid PDS4 specifier (e.g. d, f, etc)
        """

        field_format_2 = field_format  # Stores the remaining part of the field_format that has not been parsed yet

        # Check that it starts with a % and remove it from the string
        if field_format_2[0] == "%":
            field_format_2 = field_format_2[1:]
        else:
            raise PDS4meInputError(field_format, "field_format must start with %")

        # If it continues with a + or -, store the sign and remove it from the string
        if field_format_2[0] == "+" or field_format_2[0] == "-":
            sign = field_format_2[0]
            field_format_2 = field_format_2[1:]
        else:
            sign = ""

        # Extract the specifier and check that is PDS4 compliant. All PDS4 specifiers are valid in Python but not
        # all Python specifiers are valid in PDS4.
        specifier = field_format_2[-1]
        field_format_2 = field_format_2[:-1]
        if not (specifier == "d" or specifier == "0" or specifier == "x" or specifier == "f" or specifier == "e" or specifier == "E" or specifier == "s"):
            raise PDS4meInputError(field_format,
                                   "field_format must end with one of the following PDS4 specifiers: d, o, f, e, E or s")

        # Extract the width and precision
        dot_position = field_format_2.find(".")
        # If there is no dot there is no precision specified which is acceptable
        if dot_position == -1:
            if field_format_2.isdigit():
                width = field_format_2
                precision = -1
            else:
                raise PDS4meInputError(field_format,
                                       "Error in the format of field_format. The width must be an integer number")
        # Both the width and the precision where provided
        else:
            width = field_format_2[:dot_position]
            precision = field_format_2[dot_position + 1:]
            if not width.isdigit():
                raise PDS4meInputError(field_format, "The width must be an integer number")
            if not precision.isdigit():
                raise PDS4meInputError(field_format,
                                       "If there is a dot, the dot must be followed by a precision which has to be an integer number")
            if precision == "0":
                raise PDS4meInputError(field_format,
                                       "PDS4me restriction: In scientific notation the precision cannot be 0")

        # Other validation checks
        if specifier == "s":
            if precision != -1 and precision != width:
                raise PDS4meInputError(field_format, "In strings do not indicate the precision or make it equal to the width")

        if sign == "-" and specifier != "s":
            raise PDS4meInputError(field_format,
                                   "The - prefix is forbidden for all numeric fields")

        parsed_field_format = namedtuple("parsed_field_format", "sign width precision specifier")
        parsed_field_format.sign = sign
        parsed_field_format.width = width
        parsed_field_format.precision = precision
        parsed_field_format.specifier = specifier

        return parsed_field_format


class PDS4meInputError(Exception):
    """Exception raised for errors in the input.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message





