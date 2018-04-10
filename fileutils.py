EMPTY = ""

INVALID_INT = "ERROR: [{:s}]\n       Cannot convert \"{:s}\" to an Integer."
EXCESS_WARNING = "WARNING: [{:s}]\n         Requesting {:d} {:s}s, only {:d} remain."

class FileReader(object):
    """
    Custom buffered filereader to be passed along when trying to load data
    from files.

    To go to the next line, use reader.read_line().  This class will hold the
    contents of this line until next line is read.  Data may be extracted by
    utilizing the get_next_<Datatype>() functions.

    NOTE: If a value cannot be cast properly, :None: will be returned.  Also,
          :None: will be returned if there is no more items left in the line.
    """

    def __init__(self, filename, delim="\t"):
        """ Constructor.

        Parameters:
        ===========
        filename (:obj:`string`): File path and name for the input file.
        delim (:obj:`string`): Deliminator used to split data. Default = `tab`.
        """

        self._filename = filename
        self._delim = delim

        self._stream = None
        self._line = ""
        self._items = []
        self._index = 0
        self._line_no = 0

    def start(self):
        """ Attempt to load the input file into a python file object. """

        try:
            self._stream = open(self._filename, "rb")
            return True
        except IOError as e:
            errmsg = "ERROR: Could not open \"{:s}\" ...\n\t{:s}"
            print errmsg.format(self._filename, e)
        return False

    def destroy(self):
        """ Close the file object. """

        self._stream.close()
        self._stream = None
        self._items = []
        self._index = 0
        self._line = ""

    def read_line(self):
        """ Load the next line into the local buffer. """

        self._line = self._stream.readline()
        self._items = self._line.strip().split(self._delim)
        self._index = 0
        self._line_no += 1

    def get_next_float(self):
        """ Retrieve the next item in the current line as a float. """

        if self.__not_valid(): return None

        self._index += 1
        return float(self._items[self._index - 1])

    def get_next_floats(self, num):
        """ Retrieve the next `num`ber of items in the current line as floats. """

        if self.__not_valid(): return None

        index = self._index
        if num + index >= len(self._items):
            amount = len(self._items) - index
            print EXCESS_WARNING.format(self, num, "Float", amount)
        else:
            amount = num

        arr = map(float, [x for x in self._items[index:index + amount]])
        self._index += amount

        return arr

    def get_next_int(self):
        """ Retrieve the next item in the current line as an integer. """

        if self.__not_valid(): return None

        self._index += 1
        try:
            return int(self._items[self._index - 1])
        except ValueError:
            try:
                return int(float(self._items[self._index - 1]))
            except ValueError as e:
                print INVALID_INT.format(self, self._items[self._index - 1])
                return None

    def get_next_ints(self, num):
        """ Retrieve the next `num`ber of items in the current line as intergers. """

        if self.__not_valid(): return None

        index = self._index
        if num + index >= len(self._items):
            amount = len(self._items) - index
            print EXCESS_WARNING.format(self, num, "Float", amount)
        else:
            amount = num

        arr = [self.get_next_int() for _ in xrange(amount)]
        self._index += amount

        return arr


    def is_eol(self):
        """ Check if the file cursor is at the end of the line (EOL). """

        return self._index == len(self._items)

    def __not_valid(self):
        """ Check if it is valid to pull a non string type for data. """

        return self.is_eol() or self._line == ""

    def __str__(self):

        message = "FileReader for \"{:s}\" currently at line {:d}"
        return message.format(self._filename, self._line_no)

if __name__ == "__main__":

    filename = "fu_test.txt"
    test_file = FileReader(filename)
    test_file.start()
    test_file.read_line()
    print test_file.get_next_floats(3)
    print test_file.get_next_float()
    test_file.read_line()
    print test_file.get_next_ints(3)
    test_file.read_line()
    print test_file.get_next_ints(3)
    test_file.read_line()
    print test_file._line is None
    test_file.destroy()
