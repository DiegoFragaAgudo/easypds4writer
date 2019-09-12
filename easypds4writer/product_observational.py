
"""
ProductObservational Module
Public classes in the module:
  ProductObservational
"""
import xml.etree.ElementTree as ET
import ntpath
import datetime
import os
from easypds4writer.table_character import TableCharacter


class ProductObservational:
    """"
    ProductObservational class: Contains the functionality to write PDS4 compliant products.

      This class is the starting point to write PDS4 compliant products. One object of this class will be configured to
      write one specific type of PDS4 products but can be reused to write as many products of that type as desired. It
      shall not be reconfigured however to write a different product type. All products sharing the same format and
      label template are of the same type.
      Methods:
        __init__(self, template_name):          Initialize the object, optionally with a template.
        declare_table_character(self, name=""): Tells the object that this product type will contain a fixed width ASCII
                                                table (a PDS4 Table_Character) with the given name.
        new_product(self, data_file_name):      Initializes a new product product receiving as argument the data file
                                                name (not the label name).

        set_metadata(self, variable, value):    A template engine used to replace one string by another in the template.
        close_product(self):                    Writes the product (data file and label file) and leaves the object
                                                ready to call new_product again.
    """

    def __init__(self, template_name):
        """"
        Initialization method

        Arguments:
            template_name: String consisting on a template name possibly with a path. products
        """

        # Attributes which take always the same values for every product of the same type.

        # Name of the template xml file containing all the content of a normal label except for the file Area
        self._template_name = template_name
        # Holds the pds4 objects (table character, image etc) that are in the definition of this product type.
        self._list_of_objects= []

        # Attributes which values are specific of each product

        # Contains the root of the ETREE object containing a parsed representation of the label
        self.label = None
        self._data_file_name = ""
        self._product_name = ""
        self._label_file_name = ""
        # File pointer to the data file as returned by python open method
        self._fp_data_file= None
        # Dictionary (understood as the Python data structure) to hold pairs of variables and values introduced by
        # the user.
        self._metadata = {}

    def new_product(self, data_file_name):

        self._data_file_name = data_file_name
        self._product_name = os.path.splitext(data_file_name)[0]

        self._label_file_name = self._product_name + ".xml"
        # Dictionary (understood as the Python data structure) to hold pairs of variables and values introduced by
        # the user.
        self._metadata = {}
        self._initialize_label()
        self._open_files()
        # Loop on ech PDS4 object declared in this product and reset their attributes and set on them the file pointer.
        for pds4_object in self._list_of_objects:
            pds4_object.reset()
            pds4_object.set_file_pointers(self._fp_data_file)

    def declare_table_character(self, name=""):
        # TODO Check that table_character is actually of table_character type
        table_character = TableCharacter(name)
        self._append_object(table_character)
        return table_character

    def set_metadata(self, variable, value):
        """" TBW """
        if (variable[0] != '$'):
            error_message = "variables must start with $ but %s does not" % (variable)
            raise PDS4meInputError(variable, error_message)
        self._metadata[variable]= value

    def close_product(self):
        # Generate and write to file the label
        self._write_label()
        # Close file and reset other variables to ensure that if the method is called again by accident it fails.
        self.label = None
        self._data_file_name= None
        self._label_file_name = None
        self._product_name= None
        # Close the data file
        if (self._fp_data_file != None):
            self._fp_data_file.close()

    def _append_object(self, pds4_object):
        #pds4_object.set_file_pointers(self._fp_data_file)
        #pds4_object.offset= self._fp_data_file.tell()
        self._list_of_objects.append(pds4_object)

    def _open_files(self):
        # Missing to implement I/O error handling and possibly handling the cases where the product name is given
        # (by error) with an extension
        # Pending to handle right data file extension.
        # newline='\r\n' forces line ending in CR LF in both Linux and Windows. It should work in Python 3.x and > 2.6
        self._fp_data_file = open(self._data_file_name, "w", newline='\r\n')

    def _initialize_label(self):
        tree = ET.parse(self._template_name)
        # This is done to register a namespace so that the default namespace ns0: does not appear before all XML tags
        ET.register_namespace('', "http://pds.nasa.gov/pds4/pds/v1")
        #ET.register_namespace('psa', "http://psa.esa.int/psa/v1")

        #self._register_all_namespaces(self._template_name)

        self.label = tree.getroot()

    def _write_label(self):

        file_area_observational= ET.Element("File_Area_Observational")
        self.label.append(file_area_observational)

        file = ET.SubElement(file_area_observational, "File")

        file_name = ET.SubElement(file, "file_name")
        file_name.text = ntpath.basename(self._data_file_name)

        creation_date_time = ET.SubElement(file, "creation_date_time")
        creation_date_time.text = datetime.datetime.utcnow().isoformat() + "Z"

        comment = ET.SubElement(file, "comment")
        comment.text = "This product, including its data file and the label file have been generated using EasyPDS4writer library draft version"

        # Loop on ech PDS4 object. Each object is responsible of writing its own part of the label
        for pds4_object in self._list_of_objects:
            pds4_object.writte_label(file_area_observational, ET)

        # wrap it in an ElementTree instance, and save as XML
        tree = ET.ElementTree(self.label)
        self._indent(self.label,0)
        tree.write(self._label_file_name)

        # Now that the label has been written and closed, reopen it to edit the variables 9placeholders) and replace
        # them with the user provided values.
        self._replace_metadata_in_label()


    def _indent(self, elem, level=0):
        i = "\n" + level*"    "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "    "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self._indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    def _register_all_namespaces(self, filename):
        """" Register the namespaces

        It is necessary to call this method to avoid the namespaces prefixes in the template to be substituted in the
        label by the n0, n1, n2 symbols.
        This method alters the ElementTree by adding the correct prefixes
        Note: Taken from https://stackoverflow.com/questions/54439309/how-to-preserve-namespaces-when-parsing-xml-via-elementtree-in-python
        Note2: It might add a pds prefix which is unwanted.
        """

        namespaces = dict([node for _, node in ET.iterparse(filename, events=['start-ns'])])
        for ns in namespaces:
            ET.register_namespace(ns, namespaces[ns])


    def _replace_metadata_in_label(self):

        # Open for reading and writing
        fp_label_file_local = open(self._label_file_name, "r+")

        # Read the label file to a string and replace in the string the variables with the values provided by the user
        label_in_a_string= fp_label_file_local.read()
        for variable, value in self._metadata.items():
            label_in_a_string= label_in_a_string.replace(variable, value)

        # Place the write file pointer to the beginning of the file, write the string containing the updated label and
        # close the file.
        fp_label_file_local.seek(0)
        fp_label_file_local.write(label_in_a_string)
        fp_label_file_local.close()

class PDS4meInputError(Exception):
    """Exception raised for errors in the input.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message