import re

DEFAULT_WIDTH = 32 # bits


class icb: # int-coded-binary
    def __init__(self, value: int | str = 0, width: int = DEFAULT_WIDTH):
        if isinstance(value, str):
            temp = icb.parse_from_str(str)
            self.repr = icb._sign_mag_to_two_comp(temp, width)
        elif isinstance(value, int):
            self.repr = icb._sign_mag_to_two_comp(value, width)
        self.width = width

  
    # zero-extend
    def __zext__(self, new_width: int) -> 'icb':
        if self.width > new_width:
            raise ValueError(f"New width ({new_width}) must be greater than current width ({self.width})")
        
        return icb(self.repr, new_width)


    # sign-extend
    def __sext__(self, new_width: int) -> 'icb':
        if self.width > new_width:
            raise ValueError(f"New width ({new_width}) must be greater than current width ({self.width})")
        
        if self.width == new_width:
            return icb(self.repr, self.width)
        
        sign_bit = self.repr >> (self.width - 1) 
        if sign_bit:
            new_repr = (self.repr | (~0 << self.width)) % (1 << new_width)
        else:
            new_repr = self.repr
        
        return icb(new_repr, new_width)

    
    def __add__(self, other: 'icb') -> 'icb':
        if self.width < other.width:
            raise ValueError(f"The width of the first operand ({self.width}) must be greater than or equal the width of the second operand ({other.width}).")
        
        ext_other = other.__sext__(self.width)
        
        return icb(self.repr + ext_other.repr, self.width)
    

    def __sub__(self, other: 'icb') -> 'icb':
        if self.width < other.width:
            raise ValueError(f"The width of the first operand ({self.width}) must be greater than or equal the width of the second operand ({other.width}).")
        
        ext_other = other.__sext__(self.width)
        one_comp = ext_other.__xor__(icb((1 << ext_other.width) - 1, ext_other.width))
        two_comp = one_comp.__add__(icb(1, one_comp.width))

        return icb(self.repr + two_comp.repr, self.width)
    

    def __and__(self, other: 'icb') -> 'icb':
        if self.width < other.width:
            raise ValueError(f"The width of the first operand ({self.width}) must be greater than or equal the width of the second operand ({other.width}).")
        
        ext_other = other.__sext__(self.width)
        
        return icb(self.repr & ext_other.repr, self.width)
    

    def __or__(self, other: 'icb') -> 'icb':
        if self.width < other.width:
            raise ValueError(f"The width of the first operand ({self.width}) must be greater than or equal the width of the second operand ({other.width}).")
        
        ext_other = other.__sext__(self.width)
        
        return icb(self.repr | ext_other.repr, self.width)
    

    def __xor__(self, other: 'icb') -> 'icb':
        if self.width < other.width:
            raise ValueError(f"The width of the first operand ({self.width}) must be greater than or equal the width of the second operand ({other.width}).")
        
        ext_other = other.__sext__(self.width)
        
        return icb(self.repr ^ ext_other.repr, self.width)
    

    def __sll__(self, other: 'icb') -> 'icb':
        ext_other = other.__zext__(self.width)
        
        return icb(self.repr << (ext_other.repr & 31), self.width)
    

    def __srl__(self, other: 'icb') -> 'icb':
        ext_other = other.__zext__(self.width)
        
        return icb(self.repr >> (ext_other.repr & 31), self.width)
    

    def __sra__(self, other: 'icb') -> 'icb':
        sign = (self.repr >> (self.width - 1)) & 1
        shamt = other.repr & 31

        sign_ext_part = (((sign << shamt) - 1) << (self.width - shamt)) if sign else 0
        
        temp = self.__srl__(other)

        return icb(temp.repr | sign_ext_part, temp.width) 
    

    def __seq__(self, other: 'icb') -> 'icb':
        if self.width < other.width:
            raise ValueError(f"The width of the first operand ({self.width}) must be greater than or equal the width of the second operand ({other.width}).")
        
        ext_other = other.__sext__(self.width)
        
        return icb(1 if self.repr == ext_other.repr else 0, self.width)
    

    def __sne__(self, other: 'icb') -> 'icb':
        if self.width < other.width:
            raise ValueError(f"The width of the first operand ({self.width}) must be greater than or equal the width of the second operand ({other.width}).")
        
        ext_other = other.__sext__(self.width)
        
        return icb(1 if self.repr != ext_other.repr else 0, self.width)
    

    def __sltu__(self, other: 'icb') -> 'icb':
        if self.width < other.width:
            raise ValueError(f"The width of the first operand ({self.width}) must be greater than or equal the width of the second operand ({other.width}).")
        
        ext_other = other.__zext__(self.width)
        
        return icb(1 if self.repr < ext_other.repr else 0, self.width)


    def __slt__(self, other: 'icb') -> 'icb':
        if self.width < other.width:
            raise ValueError(f"The width of the first operand ({self.width}) must be greater than or equal the width of the second operand ({other.width}).")
        
        ext_other = other.__sext__(self.width)

        self_sign_bit = self.repr >> (self.width - 1)
        other_sign_bit = ext_other.repr >> (ext_other.width - 1)
        if self_sign_bit > other_sign_bit:
            return icb(1, self.width)
        elif self_sign_bit < other_sign_bit:
            return icb(0, self.width)
        else:
            return self.__sltu__(ext_other)


    def __sleu__(self, other: 'icb') -> 'icb':
        if self.width < other.width:
            raise ValueError(f"The width of the first operand ({self.width}) must be greater than or equal the width of the second operand ({other.width}).")
        
        ext_other = other.__zext__(self.width)
        
        return icb(1 if self.repr <= ext_other.repr else 0, self.width)

    
    def __sle__(self, other: 'icb') -> 'icb':
        if self.width < other.width:
            raise ValueError(f"The width of the first operand ({self.width}) must be greater than or equal the width of the second operand ({other.width}).")
        
        ext_other = other.__sext__(self.width)

        self_sign_bit = self.repr >> (self.width - 1)
        other_sign_bit = ext_other.repr >> (ext_other.width - 1)
        if self_sign_bit > other_sign_bit:
            return icb(1, self.width)
        elif self_sign_bit < other_sign_bit:
            return icb(0, self.width)
        else:
            return self.__sleu__(ext_other)


    def __sgtu__(self, other: 'icb') -> 'icb':
        if self.width < other.width:
            raise ValueError(f"The width of the first operand ({self.width}) must be greater than or equal the width of the second operand ({other.width}).")
        
        ext_other = other.__zext__(self.width)
        
        return icb(1 if self.repr > ext_other.repr else 0, self.width)
    

    def __sgt__(self, other: 'icb') -> 'icb':
        if self.width < other.width:
            raise ValueError(f"The width of the first operand ({self.width}) must be greater than or equal the width of the second operand ({other.width}).")
        
        ext_other = other.__sext__(self.width)
        
        self_sign_bit = self.repr >> (self.width - 1)
        other_sign_bit = ext_other.repr >> (ext_other.width - 1)
        if self_sign_bit < other_sign_bit:
            return icb(1, self.width)
        elif self_sign_bit > other_sign_bit:
            return icb(0, self.width)
        else:
            return self.__sgtu__(ext_other)
        

    def __minu__(self, other: 'icb') -> 'icb':
        if self.width < other.width:
            raise ValueError(f"The width of the first operand ({self.width}) must be greater than or equal the width of the second operand ({other.width}).")
        
        ext_other = other.__zext__(self.width)

        return icb(self.repr if self.repr < ext_other.repr else ext_other.repr, self.width)
    

    def __min__(self, other: 'icb') -> 'icb':
        if self.width < other.width:
            raise ValueError(f"The width of the first operand ({self.width}) must be greater than or equal the width of the second operand ({other.width}).")
        
        ext_other = other.__sext__(self.width)

        self_sign_bit = self.repr >> (self.width - 1)
        other_sign_bit = ext_other.repr >> (ext_other.width - 1)
        if self_sign_bit > other_sign_bit:
            return icb(self.repr, self.width)
        elif self_sign_bit < other_sign_bit:
            return icb(ext_other.repr, ext_other.width)
        else:
            return self.__minu__(ext_other)
        

    def __maxu__(self, other: 'icb') -> 'icb':
        if self.width < other.width:
            raise ValueError(f"The width of the first operand ({self.width}) must be greater than or equal the width of the second operand ({other.width}).")
        
        ext_other = other.__zext__(self.width)

        return icb(self.repr if self.repr > ext_other.repr else ext_other.repr, self.width)
    

    def __max__(self, other: 'icb') -> 'icb':
        if self.width < other.width:
            raise ValueError(f"The width of the first operand ({self.width}) must be greater than or equal the width of the second operand ({other.width}).")
        
        ext_other = other.__sext__(self.width)

        self_sign_bit = self.repr >> (self.width - 1)
        other_sign_bit = ext_other.repr >> (ext_other.width - 1)
        if self_sign_bit < other_sign_bit:
            return icb(self.repr, self.width)
        elif self_sign_bit > other_sign_bit:
            return icb(ext_other.repr, ext_other.width)
        else:
            return self.__maxu__(ext_other)


    def to_bin(self) -> str:
        return f'0b{bin(self.repr)[2:].zfill(self.width)}'


    def to_hex(self) -> str:
        hex_width = (self.width + 3) // 4
        return f'0x{hex(self.repr)[2:].zfill(hex_width)}'


    @staticmethod
    def _sign_mag_to_two_comp(value: int, width: int) -> int:
        '''
        Convert a sign-magnitude integer to its two's complement representation.
        
        :param value: Sign-magnitude integer
        :param width: Bit width for the representation
        :return: 2's complement as integer
        '''
        
        if value >= 0:
            return value % (2 ** width)
        else:
            return ((~(-value) | (1 << (width - 1))) + 1) % (2 ** width)


    @staticmethod
    def parse_from_str(numeric_str: str) -> int:
        '''
        Parse a numeric string in sign-magnitude binary, hexadecimal, or decimal format and convert it to an integer.    
        
        :param numeric_str: A string representation of a number. 
                            It can be in binary format (e.g., '0b1010', '-0b0110'), 
                            hexadecimal format (e.g., '0x1A3F', '-0x1C2A'), 
                            or decimal format (e.g., '40', '-99').
        :return: The integer value corresponding to the input string.
        '''

        if not isinstance(numeric_str, str):
            raise ValueError(f"{numeric_str} is not a string")

        number_match = re.match(r'(?P<bin>-?0b[01]+)|(?P<hex>-?0x[0-9a-fA-F]+)|(?P<dec>-?\d+)', numeric_str)

        if not number_match:
            raise ValueError(f"'{numeric_str}' is not a numeric string")

        if number_match.group('bin'):
            return int(number_match.group('bin'), 2)
        elif number_match.group('hex'):
            return int(number_match.group('hex'), 16)
        elif number_match.group('dec'):
            return int(number_match.group('dec'))
        

    @staticmethod
    def get_bits(src: int, start: int, width: int) -> int:
        '''
        Extract a subset of bits from the source integer-coded-binary.

        :param src: The source integer from which bits are extracted.
        :type src: int
        :param start: The starting bit position (0-indexed, from the least significant bit).
        :type start: int
        :param width: The number of bits to extract.
        :type width: int
        :return: The extracted bits as an integer.
        :rtype: int
        :raises ValueError: If `width` is not positive or `start` is negative.

        **Examples**:

        .. code-block:: python

            # Example: Binary 1101101 (decimal 109)
            src = 0b1101101

            # Extract 3 bits starting from position 2
            result = get_bits(src, 2, 3)  # Output: 3 (Binary: 011)

            # Extract 4 bits starting from position 0
            result = get_bits(src, 0, 4)  # Output: 13 (Binary: 1101)

        '''
        if width <= 0:
            raise ValueError("Width must be a positive integer.")
        if start < 0:
            raise ValueError("Start position must be non-negative.")
        
        mask = (1 << width) - 1
        return (src >> start) & mask
