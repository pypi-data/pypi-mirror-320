from .icb import icb
from .supported_features import ELEN, VLEN

class vector:
    def __init__(self, vreg: int = 0, vect: list[icb] = None, elen: int = ELEN, vlen: int = VLEN) -> None:
        if vect != None:
            if len(vect) != vlen // elen:
                raise ValueError('Mismatch in size between source vector and configs (elen, vlen parameters)')
            
            self.elms = vect
        else:
            self.elms = vector.vectorize(vreg, elen, vlen)
        self.elen = elen
        self.vlen = vlen
    
    
    def __vadd__(self, other: 'vector', masks: list[int] = None) -> 'vector':
        masks = masks or [1] * (self.vlen // self.elen)

        # Check mismatch
        if self.elen != other.elen or self.vlen != other.vlen:
            raise ValueError('Mismatch in size between two vector')

        result_vect = [
            self_elm.__add__(other_elm) if mask else icb(0, self.elen)
            for self_elm, other_elm, mask in zip(self.elms, other.elms, masks)
        ]

        return vector(vect=result_vect, elen=self.elen, vlen=self.vlen)


    def __vsub__(self, other: 'vector', masks: list[int] = None) -> 'vector':
        masks = masks or [1] * (self.vlen // self.elen)

        # Check mismatch
        if self.elen != other.elen or self.vlen != other.vlen:
            raise ValueError('Mismatch in size between two vector')

        result_vect = [
            self_elm.__sub__(other_elm) if mask else icb(0, self.elen)
            for self_elm, other_elm, mask in zip(self.elms, other.elms, masks)
        ]

        return vector(vect=result_vect, elen=self.elen, vlen=self.vlen)


    def __vrsub__(self, other: 'vector', masks: list[int] = None) -> 'vector':
        masks = masks or [1] * (self.vlen // self.elen)

        # Check mismatch
        if self.elen != other.elen or self.vlen != other.vlen:
            raise ValueError('Mismatch in size between two vector')

        result_vect = [
            other_elm.__sext__(self_elm.width).__sub__(self_elm) if mask else icb(0, self.elen)
            for self_elm, other_elm, mask in zip(self.elms, other.elms, masks)
        ]

        return vector(vect=result_vect, elen=self.elen, vlen=self.vlen)


    def __vand__(self, other: 'vector', masks: list[int] = None) -> 'vector':
        masks = masks or [1] * (self.vlen // self.elen)

        # Check mismatch
        if self.elen != other.elen or self.vlen != other.vlen:
            raise ValueError('Mismatch in size between two vector')

        result_vect = [
            self_elm.__and__(other_elm) if mask else icb(0, self.elen)
            for self_elm, other_elm, mask in zip(self.elms, other.elms, masks)
        ]

        return vector(vect=result_vect, elen=self.elen, vlen=self.vlen)


    def __vor__(self, other: 'vector', masks: list[int] = None) -> 'vector':
        masks = masks or [1] * (self.vlen // self.elen)

        # Check mismatch
        if self.elen != other.elen or self.vlen != other.vlen:
            raise ValueError('Mismatch in size between two vector')

        result_vect = [
            self_elm.__or__(other_elm) if mask else icb(0, self.elen)
            for self_elm, other_elm, mask in zip(self.elms, other.elms, masks)
        ]

        return vector(vect=result_vect, elen=self.elen, vlen=self.vlen)


    def __vxor__(self, other: 'vector', masks: list[int] = None) -> 'vector':
        masks = masks or [1] * (self.vlen // self.elen)

        # Check mismatch
        if self.elen != other.elen or self.vlen != other.vlen:
            raise ValueError('Mismatch in size between two vector')

        result_vect = [
            self_elm.__xor__(other_elm) if mask else icb(0, self.elen)
            for self_elm, other_elm, mask in zip(self.elms, other.elms, masks)
        ]

        return vector(vect=result_vect, elen=self.elen, vlen=self.vlen)


    def __vsll__(self, other: 'vector', masks: list[int] = None) -> 'vector':
        masks = masks or [1] * (self.vlen // self.elen)

        # Check mismatch
        if self.elen != other.elen or self.vlen != other.vlen:
            raise ValueError('Mismatch in size between two vector')

        result_vect = [
            self_elm.__sll__(other_elm) if mask else icb(0, self.elen)
            for self_elm, other_elm, mask in zip(self.elms, other.elms, masks)
        ]

        return vector(vect=result_vect, elen=self.elen, vlen=self.vlen)


    def __vsrl__(self, other: 'vector', masks: list[int] = None) -> 'vector':
        masks = masks or [1] * (self.vlen // self.elen)

        # Check mismatch
        if self.elen != other.elen or self.vlen != other.vlen:
            raise ValueError('Mismatch in size between two vector')

        result_vect = [
            self_elm.__srl__(other_elm) if mask else icb(0, self.elen)
            for self_elm, other_elm, mask in zip(self.elms, other.elms, masks)
        ]

        return vector(vect=result_vect, elen=self.elen, vlen=self.vlen)


    def __vsra__(self, other: 'vector', masks: list[int] = None) -> 'vector':
        masks = masks or [1] * (self.vlen // self.elen)

        # Check mismatch
        if self.elen != other.elen or self.vlen != other.vlen:
            raise ValueError('Mismatch in size between two vector')

        result_vect = [
            self_elm.__sra__(other_elm) if mask else icb(0, self.elen)
            for self_elm, other_elm, mask in zip(self.elms, other.elms, masks)
        ]

        return vector(vect=result_vect, elen=self.elen, vlen=self.vlen)


    def __vmseq__(self, other: 'vector', masks: list[int] = None) -> 'vector':
        masks = masks or [1] * (self.vlen // self.elen)

        # Check mismatch
        if self.elen != other.elen or self.vlen != other.vlen:
            raise ValueError('Mismatch in size between two vector')

        result_vect = [
            self_elm.__seq__(other_elm) if mask else icb(0, self.elen)
            for self_elm, other_elm, mask in zip(self.elms, other.elms, masks)
        ]

        return vector(vect=result_vect, elen=self.elen, vlen=self.vlen)


    def __vmsne__(self, other: 'vector', masks: list[int] = None) -> 'vector':
        masks = masks or [1] * (self.vlen // self.elen)

        # Check mismatch
        if self.elen != other.elen or self.vlen != other.vlen:
            raise ValueError('Mismatch in size between two vector')

        result_vect = [
            self_elm.__sne__(other_elm) if mask else icb(0, self.elen)
            for self_elm, other_elm, mask in zip(self.elms, other.elms, masks)
        ]

        return vector(vect=result_vect, elen=self.elen, vlen=self.vlen)


    def __vmsltu__(self, other: 'vector', masks: list[int] = None) -> 'vector':
        masks = masks or [1] * (self.vlen // self.elen)

        # Check mismatch
        if self.elen != other.elen or self.vlen != other.vlen:
            raise ValueError('Mismatch in size between two vector')

        result_vect = [
            self_elm.__sltu__(other_elm) if mask else icb(0, self.elen)
            for self_elm, other_elm, mask in zip(self.elms, other.elms, masks)
        ]

        return vector(vect=result_vect, elen=self.elen, vlen=self.vlen)


    def __vmslt__(self, other: 'vector', masks: list[int] = None) -> 'vector':
        masks = masks or [1] * (self.vlen // self.elen)

        # Check mismatch
        if self.elen != other.elen or self.vlen != other.vlen:
            raise ValueError('Mismatch in size between two vector')

        result_vect = [
            self_elm.__slt__(other_elm) if mask else icb(0, self.elen)
            for self_elm, other_elm, mask in zip(self.elms, other.elms, masks)
        ]

        return vector(vect=result_vect, elen=self.elen, vlen=self.vlen)


    def __vmsleu__(self, other: 'vector', masks: list[int] = None) -> 'vector':
        masks = masks or [1] * (self.vlen // self.elen)

        # Check mismatch
        if self.elen != other.elen or self.vlen != other.vlen:
            raise ValueError('Mismatch in size between two vector')

        result_vect = [
            self_elm.__sleu__(other_elm) if mask else icb(0, self.elen)
            for self_elm, other_elm, mask in zip(self.elms, other.elms, masks)
        ]

        return vector(vect=result_vect, elen=self.elen, vlen=self.vlen)


    def __vmsle__(self, other: 'vector', masks: list[int] = None) -> 'vector':
        masks = masks or [1] * (self.vlen // self.elen)

        # Check mismatch
        if self.elen != other.elen or self.vlen != other.vlen:
            raise ValueError('Mismatch in size between two vector')

        result_vect = [
            self_elm.__sle__(other_elm) if mask else icb(0, self.elen)
            for self_elm, other_elm, mask in zip(self.elms, other.elms, masks)
        ]

        return vector(vect=result_vect, elen=self.elen, vlen=self.vlen)


    def __vmsgtu__(self, other: 'vector', masks: list[int] = None) -> 'vector':
        masks = masks or [1] * (self.vlen // self.elen)

        # Check mismatch
        if self.elen != other.elen or self.vlen != other.vlen:
            raise ValueError('Mismatch in size between two vector')

        result_vect = [
            self_elm.__sgtu__(other_elm) if mask else icb(0, self.elen)
            for self_elm, other_elm, mask in zip(self.elms, other.elms, masks)
        ]

        return vector(vect=result_vect, elen=self.elen, vlen=self.vlen)


    def __vmsgt__(self, other: 'vector', masks: list[int] = None) -> 'vector':
        masks = masks or [1] * (self.vlen // self.elen)

        # Check mismatch
        if self.elen != other.elen or self.vlen != other.vlen:
            raise ValueError('Mismatch in size between two vector')

        result_vect = [
            self_elm.__sgt__(other_elm) if mask else icb(0, self.elen)
            for self_elm, other_elm, mask in zip(self.elms, other.elms, masks)
        ]

        return vector(vect=result_vect, elen=self.elen, vlen=self.vlen)


    def __vminu__(self, other: 'vector', masks: list[int] = None) -> 'vector':
        masks = masks or [1] * (self.vlen // self.elen)

        # Check mismatch
        if self.elen != other.elen or self.vlen != other.vlen:
            raise ValueError('Mismatch in size between two vector')

        result_vect = [
            self_elm.__minu__(other_elm) if mask else icb(0, self.elen)
            for self_elm, other_elm, mask in zip(self.elms, other.elms, masks)
        ]

        return vector(vect=result_vect, elen=self.elen, vlen=self.vlen)


    def __vmin__(self, other: 'vector', masks: list[int] = None) -> 'vector':
        masks = masks or [1] * (self.vlen // self.elen)

        # Check mismatch
        if self.elen != other.elen or self.vlen != other.vlen:
            raise ValueError('Mismatch in size between two vector')

        result_vect = [
            self_elm.__min__(other_elm) if mask else icb(0, self.elen)
            for self_elm, other_elm, mask in zip(self.elms, other.elms, masks)
        ]

        return vector(vect=result_vect, elen=self.elen, vlen=self.vlen)


    def __vmaxu__(self, other: 'vector', masks: list[int] = None) -> 'vector':
        masks = masks or [1] * (self.vlen // self.elen)

        # Check mismatch
        if self.elen != other.elen or self.vlen != other.vlen:
            raise ValueError('Mismatch in size between two vector')

        result_vect = [
            self_elm.__maxu__(other_elm) if mask else icb(0, self.elen)
            for self_elm, other_elm, mask in zip(self.elms, other.elms, masks)
        ]

        return vector(vect=result_vect, elen=self.elen, vlen=self.vlen)


    def __vmax__(self, other: 'vector', masks: list[int] = None) -> 'vector':
        masks = masks or [1] * (self.vlen // self.elen)

        # Check mismatch
        if self.elen != other.elen or self.vlen != other.vlen:
            raise ValueError('Mismatch in size between two vector')

        result_vect = [
            self_elm.__max__(other_elm) if mask else icb(0, self.elen)
            for self_elm, other_elm, mask in zip(self.elms, other.elms, masks)
        ]

        return vector(vect=result_vect, elen=self.elen, vlen=self.vlen)


    def __vmerge__(self, other: 'vector', masks: list[int] = None) -> 'vector':
        masks = masks or [1] * (self.vlen // self.elen)

        # Check mismatch
        if self.elen != other.elen or self.vlen != other.vlen:
            raise ValueError('Mismatch in size between two vector')

        result_vect = [
            other_elm.__sext__(self.elen) if mask else self_elm
            for self_elm, other_elm, mask in zip(self.elms, other.elms, masks)
        ]

        return vector(vect=result_vect, elen=self.elen, vlen=self.vlen)
    

    def to_register(self) -> int:
        '''
        Convert the vector as list of 'icb' type to a vector register as integer
        '''
        vreg = 0
        for index, elm in enumerate(self.elms):
            vreg |= (elm.repr << (self.elen * index))
        
        return vreg
    
    
    def get_element(self, index: int) -> icb:
        if index < 0 or index > self.vlen // self.elen:
            raise ValueError('Invalid index')
        
        return self.elms[index]
    

    @staticmethod
    def vectorize(vreg: int, elen: int, vlen: int) -> list[icb]:
        '''
        Convert a vector register as integer (it codes binary - icb) to list of 'icb' type
        '''
        vect = []
        for i in range(vlen // elen):
            elm = icb.get_bits(vreg, start=(i * elen), width=elen)
            vect.append(icb(elm, elen))
        return vect