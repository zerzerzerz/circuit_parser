class LUT:
    lut_size = 7
    num_luts = 8

    @staticmethod
    def _display():
        for attr in dir(LUT):
            if not attr.startswith('_'):
                print("{:20}\t{}".format(attr, getattr(LUT, attr)))

# this separator is to connect cell and pin
# __504__@A
CELL_PIN_SEP = '@'

# this separator is to indicate connection direction
# _345_@A>>>_345_@ZN
CONNECTION_SEP = '>>>'

# whether to print all information
VERBOSE = False

# for field in this variable, filter will ignore it
IGNORED_KEYS_FOR_FILTERATING_INVALID_DATA = []

FORWARD_SLASH = '/'
BACKWARD_SLASH = '\\'
LINE = '\n' + '*' * 100
