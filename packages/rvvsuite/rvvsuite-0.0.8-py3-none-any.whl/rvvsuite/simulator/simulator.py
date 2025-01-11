from ..common.icb import icb
from ..common.vector import vector
from ..common.supported_features import GROUP_OF_OPCODES, FUNCT6_TO_INST_MAP, VECTOR_INSTS, SCALAR_INSTS


DEFAULT_CONFIGS = {
    'pc_width': 10,
    'addr_width': 12,
    'elen': 32,
    'vlen': 128,
    'xlen': 32
}


class simulator:
    def __init__(self, imem: dict = {}, dmem: dict = {}, configs: dict = DEFAULT_CONFIGS, debug_mode: bool = False, log: str = '') -> None:
        self.imem = imem
        self.dmem = dmem
        self.configs = configs
        self.x_reg_file = {key: 0 for key in range(32)}
        self.v_reg_file = {key: 0 for key in range(32)}
        self.pc = 0
        self.debug_mode = debug_mode
        if debug_mode:
            self.log = log


    def __apply_changes(self, changes: dict) -> None:
        if 'pc' in changes:
            self.pc = changes['pc']
        
        if 'x_reg_file' in changes:
            for rd, value in changes['x_reg_file'].items():
                self.x_reg_file[rd] = value

        if 'v_reg_file' in changes:
            for vd, value in changes['v_reg_file'].items():
                self.v_reg_file[vd] = value

        if 'dmem' in changes:
            for addr, byte in changes['dmem'].items():
                self.dmem[addr] = byte
    
    
    def run(self):
        vlen = self.configs['vlen']
        elen = self.configs['elen']
        xlen = self.configs['xlen']
        addr_width = self.configs['addr_width']
        dmem_size = 1 << addr_width
        pc_width = self.configs['pc_width']
        imem_size = 1 << pc_width

        if self.debug_mode and self.log:
            with open(self.log, 'w') as file:
                file.write('')  # Clear if log exists

        changlog = []

        # Init stats
        vector_inst_counters =  {
            **{f"{inst}.{fmt}": 0 for inst, details in VECTOR_INSTS.items() for fmt in details.get('formats', [])},
            **{f"{inst}{width}.v": 0 for inst, details in VECTOR_INSTS.items() for width in details.get('widths', [])}
        }
        scalar_inst_counters = {inst: 0 for inst in SCALAR_INSTS}
        vector_read_counters = {v: 0 for v in range(32)}
        vector_write_counters = {v: 0 for v in range(32)}
        register_read_counters = {r: 0 for r in range(32)}
        register_write_counters = {r: 0 for r in range(32)}
        dmem_read_counters = {}
        dmem_write_counters = {}

        while True:
            changes = {} # Init changes dict for each instruction

            if  self.pc >= imem_size: # End of IMEM
                break
            
            if self.pc % 4 != 0: # Check if pc is aligned
                raise ValueError(f'Invalid PC: {self.pc}. Must be aligned to 4.')
            
            inst = self.imem.get(self.pc, 0) # 0 if pc is not in imem

            if inst == 0: # No more inst
                break

            opcode = icb.get_bits(inst, start=0, width=7)
            
            if opcode == 0b1010111: # v_arith
                opcode, vd, funct3, vs1_rs1_imm, vs2, vm, funct6 = simulator.__decode_inst_v_arith(inst)

                op = FUNCT6_TO_INST_MAP[funct6]
                if op == 'vmerge' and vm == 1:
                    op = 'vmv'
                elif op == 'vmv' and vm == 0:
                    op = 'vmerge'

                vector_write_counters[vd] += 1 # Stat
                vector_read_counters[vs2] += 1 # Stat

                vect2 = vector(self.v_reg_file[vs2], elen=elen, vlen=vlen)
                if funct3 == 0b000: # OPIVV
                    vect1 = vector(self.v_reg_file[vs1_rs1_imm], elen=elen, vlen=vlen)

                    format = 'v.v' if op == 'vmv' else 'vvm' if op == 'vmerge' else 'vv'
                    self.__debug_log(f"{op}.{format} v{vd}, {f'v{vs2}, ' if op != 'vmv' else ''}v{vs1_rs1_imm}{', v0.t' if not vm else ''}")

                    vector_inst_counters[f'{op}.{format}'] += 1 # Stat
                    vector_read_counters[vs1_rs1_imm] += 1 # Stat
            
                elif funct3 == 0b100: # OPIVX
                    vect1 = vector(vect=[icb(self.x_reg_file[vs1_rs1_imm], width=elen)] * (vlen // elen), elen=elen, vlen=vlen)

                    format = 'v.x' if op == 'vmv' else 'vxm' if op == 'vmerge' else 'vx'
                    self.__debug_log(f"{op}.{format} v{vd}, {f'v{vs2}, ' if op != 'vmv' else ''}x{vs1_rs1_imm}{', v0.t' if not vm else ''}")

                    vector_inst_counters[f'{op}.{format}'] += 1 # Stat
                    register_read_counters[vs1_rs1_imm] += 1 # Stat

                elif funct3 == 0b011: # OPIVI
                    vect1 = vector(vect=[icb(vs1_rs1_imm, width=5)] * (vlen // elen), elen=elen, vlen=vlen)

                    format = 'v.i' if op == 'vmv' else 'vim' if op == 'vmerge' else 'vi'
                    self.__debug_log(f"{op}.{format} v{vd}, {f'v{vs2}, ' if op != 'vmv' else ''}{hex(vs1_rs1_imm)}{', v0.t' if not vm else ''}")

                    vector_inst_counters[f'{op}.{format}'] += 1 # Stat

                else:
                    raise ValueError(f'Unsupported funct3: 0b{funct3:3b}.')
                
                masks = self.__get_masks(vm)

                result = self.__vop(funct6, vect2, vect1, masks)
                
                if op != 'vmv': self.__debug_log(f"Source: {f'v{vs2}':7} = {' '.join([elm.to_hex() for elm in vect2.elms])}", indent=2)
                self.__debug_log(f"Source: {f'v{vs1_rs1_imm}' if format in ['vv', 'vvm', 'v.v'] else f'x{vs1_rs1_imm}' if format in ['vx', 'vxm', 'v.x'] else 'imm5':7} = {' '.join([f'{elm.to_hex():>{elen // 4 + 2}}' for elm in vect1.elms])}", indent=2)
                self.__debug_log(f"Masks : {' ':7} = {' '.join([icb(mask, elen).to_hex() for mask in masks])}", indent=2)
                self.__debug_log(f"Result: {f'v{vd}':7} = {' '.join([icb(icb.get_bits(result, elen * i, elen), elen).to_hex() for i in range(vlen // elen)])}", indent=2)

                changes['pc'] = self.pc + 4
                if self.v_reg_file[vd] != result:
                    changes['v_reg_file'] = {vd: result}

            elif opcode == 0b0000111: # v_load
                opcode, vd, width_code, rs1, lumop_rs2_vs2, vm, mop, mew, nf = simulator.__decode_inst_v_load(inst)

                masks = self.__get_masks(vm)
                
                if width_code == 0b000: # 8-bit
                    width = 8
                elif width_code == 0b101: # 16-bit
                    width = 16
                elif width_code == 0b110: # 32-bit
                    width = 32
                else:
                    raise ValueError(f'Unsupported width_code: 0b{width_code:3b}.')

                base_addr = self.x_reg_file[rs1]

                vector_write_counters[vd] += 1 # Stat
                register_read_counters[rs1] += 1 # stat

                if mop == 0b00: # unit-stride
                    read_vect = self.__vload_unit_stride(vd, width, base_addr, masks)

                    self.__debug_log(f'vle{width}.v v{vd}, (x{rs1}){', v0.t' if not vm else ''}')
                    self.__debug_log(f'Source: base    = {icb(base_addr, xlen).to_hex()}', indent=2)
                    self.__debug_log(f"Masks :         = {' '.join([icb(mask, elen).to_hex() for mask in masks])}", indent=2)
                    self.__debug_log(f"Result: {f'v{vd}':7} = {' '.join([icb(icb.get_bits(read_vect, elen * i, elen), elen).to_hex() for i in range(vlen // elen)])}", indent=2)

                    vector_inst_counters[f'vle{width}.v'] += 1 # Stat
                
                elif mop == 0b01: # indexed-unordered
                    index_vect = vector(self.v_reg_file[lumop_rs2_vs2], elen=elen, vlen=vlen)
                    read_vect = self.__vload_indexed_unordered(vd, width, base_addr, index_vect, masks)

                    self.__debug_log(f'vluxei{width}.v v{vd}, (x{rs1}), v{lumop_rs2_vs2}{', v0.t' if not vm else ''}')
                    self.__debug_log(f'Source: base    = {icb(base_addr, xlen).to_hex()}', indent=2)
                    self.__debug_log(f'Source: indexes = {' '.join([elm.to_hex() for elm in index_vect.elms])}', indent=2)
                    self.__debug_log(f"Masks :         = {' '.join([icb(mask, elen).to_hex() for mask in masks])}", indent=2)
                    self.__debug_log(f"Result: {f'v{vd}':7} = {' '.join([icb(icb.get_bits(read_vect, elen * i, elen), elen).to_hex() for i in range(vlen // elen)])}", indent=2)

                    vector_inst_counters[f'vluxei{width}.v'] += 1 # Stat
                    vector_read_counters[lumop_rs2_vs2] += 1 # Stat
                    
                elif mop == 0b10: # strided
                    stride = self.x_reg_file[lumop_rs2_vs2]
                    read_vect = self.__vload_strided(vd, width, base_addr, stride, masks)

                    self.__debug_log(f'vlse{width}.v v{vd}, (x{rs1}), x{lumop_rs2_vs2}{', v0.t' if not vm else ''}')
                    self.__debug_log(f'Source: base    = {icb(base_addr, xlen).to_hex()}', indent=2)
                    self.__debug_log(f'Source: stride  = {icb(stride, xlen).to_hex()}', indent=2)
                    self.__debug_log(f"Masks :         = {' '.join([icb(mask, elen).to_hex() for mask in masks])}", indent=2)
                    self.__debug_log(f"Result: {f'v{vd}':7} = {' '.join([icb(icb.get_bits(read_vect, elen * i, elen), elen).to_hex() for i in range(vlen // elen)])}", indent=2)

                    vector_inst_counters[f'vlse{width}.v'] += 1 # Stat
                    register_read_counters[lumop_rs2_vs2] += 1 # Stat
                    
                else:
                    raise ValueError(f'Unsupported mop: 0b{mop:2b}.')
                
                changes['pc'] = self.pc + 4
                if self.v_reg_file[vd] != read_vect:
                    changes['v_reg_file'] = {vd: read_vect}

            elif opcode == 0b0100111: # v_store
                opcode, vs3, width_code, rs1, sumop_rs2_vs2, vm, mop, mew, nf = simulator.__decode_inst_v_store(inst)
                
                masks = self.__get_masks(vm)
                
                if width_code == 0b000: # 8-bit
                    width = 8
                elif width_code == 0b101: # 16-bit
                    width = 16
                elif width_code == 0b110: # 32-bit
                    width = 32
                else:
                    raise ValueError(f'Unsupported width_code: 0b{width_code:3b}.')

                base_addr = self.x_reg_file[rs1]
                write_vect = vector(self.v_reg_file[vs3], elen=elen, vlen=vlen)

                vector_read_counters[vs3] += 1 # Stat
                register_read_counters[rs1] += 1 # stat

                if mop == 0b00: # unit-stride
                    dmem_changes = self.__vstore_unit_stride(write_vect, width, base_addr, masks)

                    self.__debug_log(f'vse{width}.v v{vs3}, (x{rs1}){', v0.t' if not vm else ''}')
                    self.__debug_log(f"Source: {f'v{vs3}':7} = {' '.join([elm.to_hex() for elm in write_vect.elms])}", indent=2)
                    self.__debug_log(f'Source: base    = {icb(base_addr, xlen).to_hex()}', indent=2)
                    self.__debug_log(f"Masks :         = {' '.join([icb(mask, elen).to_hex() for mask in masks])}", indent=2)
                    self.__debug_log(f"Result: dmem    = {', '.join([f'[{icb(addr, addr_width).to_hex()}]: {icb(byte, 8).to_hex()}' for addr, byte in dmem_changes.items()])}", indent=2)
                    
                    vector_inst_counters[f'vse{width}.v'] += 1 # Stat
                
                elif mop == 0b01: # indexed-unordered
                    index_vect = vector(self.v_reg_file[sumop_rs2_vs2], elen=elen, vlen=vlen)
                    dmem_changes = self.__vstore_indexed_unordered(write_vect, width, base_addr, index_vect, masks)

                    self.__debug_log(f'vsuxei{width}.v v{vs3}, (x{rs1}), v{sumop_rs2_vs2}{', v0.t' if not vm else ''}')
                    self.__debug_log(f"Source: {f'v{vs3}':7} = {' '.join([elm.to_hex() for elm in write_vect.elms])}", indent=2)
                    self.__debug_log(f'Source: base    = {icb(base_addr, xlen).to_hex()}', indent=2)
                    self.__debug_log(f'Source: indexes = {' '.join([elm.to_hex() for elm in index_vect.elms])}', indent=2)
                    self.__debug_log(f"Masks :         = {' '.join([icb(mask, elen).to_hex() for mask in masks])}", indent=2)
                    self.__debug_log(f"Result: dmem    = {', '.join([f'[{icb(addr, addr_width).to_hex()}]: {icb(byte, 8).to_hex()}' for addr, byte in dmem_changes.items()])}", indent=2)

                    vector_inst_counters[f'vsuxei{width}.v'] += 1 # Stat
                    vector_read_counters[sumop_rs2_vs2] += 1 # Stat
                
                elif mop == 0b10: # strided
                    stride = self.x_reg_file[sumop_rs2_vs2]
                    dmem_changes = self.__vstore_strided(write_vect, width, base_addr, stride, masks)

                    self.__debug_log(f'vsse{width}.v v{vs3}, (x{rs1}), x{sumop_rs2_vs2}{', v0.t' if not vm else ''}')
                    self.__debug_log(f"Source: {f'v{vs3}':7} = {' '.join([elm.to_hex() for elm in write_vect.elms])}", indent=2)
                    self.__debug_log(f'Source: base    = {icb(base_addr, xlen).to_hex()}', indent=2)
                    self.__debug_log(f'Source: stride  = {icb(stride, xlen).to_hex()}', indent=2)
                    self.__debug_log(f"Result: dmem    = {', '.join([f'[{icb(addr, addr_width).to_hex()}]: {icb(byte, 8).to_hex()}' for addr, byte in dmem_changes.items()])}", indent=2)

                    vector_inst_counters[f'vsse{width}.v'] += 1 # Stat
                    register_read_counters[sumop_rs2_vs2] += 1 # Stat

                else:
                    raise ValueError(f'Unsupported mop: 0b{mop:2b}.')

                changes['pc'] = self.pc + 4
                changes['dmem'] = {addr: byte for addr, byte in dmem_changes.items() if self.dmem.get(addr, 0) != byte}

            elif opcode in GROUP_OF_OPCODES:
                if GROUP_OF_OPCODES[opcode] == 'u_type':
                    rd = icb.get_bits(inst, start=7, width=5)
                    imm20 = icb.get_bits(inst, start=12, width=20)

                    if opcode == 0b0110111: #lui
                        result = imm20 << 12
                        changes['pc'] = self.pc + 4
                        if self.x_reg_file[rd] != result:
                            changes['x_reg_file'] = {rd: result}

                        self.__debug_log(f'lui x{rd}, {hex(imm20)}')
                        self.__debug_log(f"Result: {f"x{rd}":7} = {icb(result, xlen).to_hex()}", indent=2)
                        
                        scalar_inst_counters['lui'] += 1 # Stat
                        register_write_counters[rd] += 1 # Stat

                    elif opcode == 0b0010111: # auipc
                        raise ValueError(f'Unsupported opcode: 0b{opcode:7b} (Not implemented yet).')

                elif GROUP_OF_OPCODES[opcode] == 'i_type':
                    rd = icb.get_bits(inst, start=7, width=5)
                    funct3 = icb.get_bits(inst, start=12, width=3)
                    rs1 = icb.get_bits(inst, start=15, width=5)
                    imm12 = icb.get_bits(inst, start=20, width=12)

                    register_write_counters[rd] += 1 # Stat
                    register_read_counters[rs1] += 1 # Stat

                    if funct3 == 0b000: # addi
                        scalar_inst_counters['addi'] += 1 # Stat

                        opnd2 = icb(self.x_reg_file[rs1], xlen)
                        opnd1 = icb(imm12, 12)

                        result = (opnd2 + opnd1).repr

                        changes['pc'] = self.pc + 4
                        if self.x_reg_file[rd] != result:
                            changes['x_reg_file'] = {rd: result}

                        self.__debug_log(f'addi x{rd}, x{rs1}, {hex(imm12)}')
                        self.__debug_log(f"Source: {f"x{rs1}":7} = {opnd2.to_hex()}", indent=2)
                        self.__debug_log(f"Source: {"imm12":7} = {opnd1.__sext__(xlen).to_hex()}", indent=2)
                        self.__debug_log(f"Result: {f"x{rd}":7} = {icb(result, xlen).to_hex()}", indent=2)
                    else:
                        raise ValueError(f'Unsupported funct3: 0b{funct3:3b} (Not implemented yet).')

                else:
                    raise ValueError(f'Unsupported opcode: 0b{opcode:7b}.')

            else:
                raise ValueError(f'Unsupported opcode: 0b{opcode:7b}.')

            changlog.append(changes)

            self.__apply_changes(changes)

        return changlog, {
            'vector_insts': vector_inst_counters,
            'scalar_insts': scalar_inst_counters,
            'vector_reads': vector_read_counters,
            'vector_writes': vector_write_counters,
            'register_reads': register_read_counters,
            'register_writes': register_write_counters,
        }
    

    def __vop(self, funct6: int, vect2: vector, vect1: vector, masks: list[int]):
        if funct6 == 0b000000: # vadd
            result_vect = vect2.__vadd__(vect1, masks)
        elif funct6 == 0b000010: # vsub
            result_vect = vect2.__vsub__(vect1, masks)
        elif funct6 == 0b000011: # vrsub
            result_vect = vect2.__vrsub__(vect1, masks)
        elif funct6 == 0b001001: # vand
            result_vect = vect2.__vand__(vect1, masks)
        elif funct6 == 0b001010: # vor
            result_vect = vect2.__vor__(vect1, masks)
        elif funct6 == 0b001011: # vxor
            result_vect = vect2.__vxor__(vect1, masks)
        elif funct6 == 0b100101: # vsll
            result_vect = vect2.__vsll__(vect1, masks)
        elif funct6 == 0b101000: # vsrl
            result_vect = vect2.__vsrl__(vect1, masks)
        elif funct6 == 0b101001: # vsra
            result_vect = vect2.__vsra__(vect1, masks)
        elif funct6 == 0b011000: # vmseq
            result_vect = vect2.__vmseq__(vect1, masks)
        elif funct6 == 0b011001: # vmsne
            result_vect = vect2.__vmsne__(vect1, masks)
        elif funct6 == 0b011010: # vmsltu
            result_vect = vect2.__vmsltu__(vect1, masks)
        elif funct6 == 0b011011: # vmslt
            result_vect = vect2.__vmslt__(vect1, masks)
        elif funct6 == 0b011100: # vmsleu
            result_vect = vect2.__vmsleu__(vect1, masks)
        elif funct6 == 0b011101: # vmsle
            result_vect = vect2.__vmsle__(vect1, masks)
        elif funct6 == 0b011110: # vmsgtu
            result_vect = vect2.__vmsgtu__(vect1, masks)
        elif funct6 == 0b011111: # vmsgt
            result_vect = vect2.__vmsgt__(vect1, masks)
        elif funct6 == 0b000100: # vminu
            result_vect = vect2.__vminu__(vect1, masks)
        elif funct6 == 0b000101: # vmin
            result_vect = vect2.__vmin__(vect1, masks)
        elif funct6 == 0b000110: # vmaxu
            result_vect = vect2.__vmaxu__(vect1, masks)
        elif funct6 == 0b000111: # vmax
            result_vect = vect2.__vmax__(vect1, masks)
        elif funct6 == 0b010111: # vmerge
            result_vect = vect2.__vmerge__(vect1, masks)
        elif funct6 == 0b010111: # vmv
            result_vect = [elm.__sext__(self.configs['elen']) for elm in vect1.elms]
        else:
            raise ValueError(f'Unsupported funct6: 0b{funct6:6b}.')
        
        return result_vect.to_register()

    
    def __vload_unit_stride(self, vd: int, width: int, base_addr: int, masks: list[int]) -> int:
        dmem_size = 1 << self.configs['addr_width']
        vlen = self.configs['vlen']
        elen = self.configs['elen']
        num_of_elms = vlen // elen

        read_vect = self.v_reg_file[vd]

        for i in range(num_of_elms):
            addr = (base_addr + i * (width // 8)) % dmem_size # Ignore higher address bits
            # if addr >= dmem_size: # TODO: Uncomment after constrain dmem access range
            #     raise ValueError(f"The address: {addr} is out of DMEM (DMEM size is {dmem_size})")

            if masks[i] == 1:
                elm_i = 0
                for j in range(width // 8):
                    elm_i |= self.dmem.get(addr + j, 0) << (j * 8)
            
                clear_mask = ~((1 << elen) - 1 << (i * elen))
                read_vect &= clear_mask # Clear old element before override
                read_vect |= icb(elm_i, width).__sext__(elen).repr << (i * elen)

        return read_vect
    

    def __vload_indexed_unordered(self, vd: int, width: int, base_addr: int, index_vect: vector, masks: list[int]) -> int:
        dmem_size = 1 << self.configs['addr_width']
        vlen = self.configs['vlen']
        elen = self.configs['elen']
        num_of_elms = vlen // elen

        read_vect = self.v_reg_file[vd]

        for i in range(num_of_elms):
            addr = (base_addr + index_vect.get_element(i).repr) % dmem_size # Ignore higher address bits
            # if addr >= dmem_size: # TODO: Uncomment after constrain dmem access range
            #     raise ValueError(f"The address: {addr} is out of DMEM (DMEM size is {dmem_size})")

            if masks[i] == 1:
                elm_i = 0
                for j in range(width // 8):
                    elm_i |= self.dmem.get(addr + j, 0) << (j * 8)
            
                clear_mask = ~((1 << elen) - 1 << (i * elen))
                read_vect &= clear_mask # Clear old element before override
                read_vect |= icb(elm_i, width).__sext__(elen).repr << (i * elen)

        return read_vect
    

    def __vload_strided(self, vd: int, width: int, base_addr: int, stride: int, masks: list[int]) -> int:
        dmem_size = 1 << self.configs['addr_width']
        vlen = self.configs['vlen']
        elen = self.configs['elen']
        num_of_elms = vlen // elen

        read_vect = self.v_reg_file[vd]

        for i in range(num_of_elms):
            addr = (base_addr + i * stride) % dmem_size # Ignore higher address bits
            # if addr >= dmem_size: # TODO: Uncomment after constrain dmem access range
            #     raise ValueError(f"The address: {addr} is out of DMEM (DMEM size is {dmem_size})")

            if masks[i] == 1:
                elm_i = 0
                for j in range(width // 8):
                    elm_i |= self.dmem.get(addr + j, 0) << (j * 8)
            
                clear_mask = ~((1 << elen) - 1 << (i * elen))
                read_vect &= clear_mask # Clear old element before override
                read_vect |= icb(elm_i, width).__sext__(elen).repr << (i * elen)

        return read_vect
    

    def __vstore_unit_stride(self, write_vect: vector, width: int, base_addr: int, masks: list[int]) -> dict:
        dmem_size = 1 << self.configs['addr_width']
        vlen = self.configs['vlen']
        elen = self.configs['elen']
        num_of_elms = vlen // elen

        dmem_changes = {}
        for i in range(num_of_elms):
            addr = (base_addr + i * (width // 8)) % dmem_size # Ignore higher address bits
            # if addr >= dmem_size: # TODO: Uncomment after constrain dmem access range
            #     raise ValueError(f"The address: {addr} is out of DMEM (DMEM size is {dmem_size})")

            if masks[i]:
                write_elm = write_vect.get_element(i).repr
                for j in range(width // 8):
                    byte = icb.get_bits(write_elm, start=8 * j, width=8)
                    dmem_changes[addr + j] = byte

        return dmem_changes
    

    def __vstore_indexed_unordered(self, write_vect: vector, width: int, base_addr: int, index_vect: vector, masks: list[int]) -> dict:
        dmem_size = 1 << self.configs['addr_width']
        vlen = self.configs['vlen']
        elen = self.configs['elen']
        num_of_elms = vlen // elen

        dmem_changes = {}
        for i in range(num_of_elms):
            addr = (base_addr + index_vect.get_element(i).repr) % dmem_size # Ignore higher address bits
            # if addr >= dmem_size: # TODO: Uncomment after constrain dmem access range
            #     raise ValueError(f"The address: {addr} is out of DMEM (DMEM size is {dmem_size})")

            if masks[i] == 1:
                write_elm = write_vect.get_element(i).repr
                for j in range(width // 8):
                    byte = icb.get_bits(write_elm, start=8 * j, width=8)
                    dmem_changes[addr + j] = byte

        return dmem_changes
    

    def __vstore_strided(self, write_vect: vector, width: int, base_addr: int, stride: int, masks: list[int]) -> dict:
        dmem_size = 1 << self.configs['addr_width']
        vlen = self.configs['vlen']
        elen = self.configs['elen']
        num_of_elms = vlen // elen

        dmem_changes = {}
        for i in range(num_of_elms):
            addr = (base_addr + i * stride) % dmem_size # Ignore higher address bits
            # if addr >= dmem_size: # TODO: Uncomment after constrain dmem access range
            #     raise ValueError(f"The address: {addr} is out of DMEM (DMEM size is {dmem_size})")

            if masks[i] == 1:
                write_elm = write_vect.get_element(i).repr
                for j in range(width // 8):
                    byte = icb.get_bits(write_elm, start=8 * j, width=8)
                    dmem_changes[addr + j] = byte

        return dmem_changes


    def __get_masks(self, vm: int) -> list[int]:
        vlen = self.configs['vlen']
        elen = self.configs['elen']

        if vm:
            return [1] * (vlen // elen)
        
        return [
            icb.get_bits(self.v_reg_file[0], start=(i * elen), width=1)
            for i in range(vlen // elen)
        ]
    
    
    def __debug_log(self, msg: str, indent: int = 0) -> None:
        if self.debug_mode:
            if self.log:
                with open(self.log, 'a') as file:
                    print(' ' * indent + msg, file=file)
            else:
                print(' ' * indent + msg)


    @staticmethod
    def __decode_inst_v_arith(inst: int) -> tuple:
        opcode = icb.get_bits(inst, start=0, width=7)
        vd = icb.get_bits(inst, start=7, width=5)
        funct3 = icb.get_bits(inst, start=12, width=3)
        vs1_rs1_imm = icb.get_bits(inst, start=15, width=5)
        vs2 = icb.get_bits(inst, start=20, width=5)
        vm = icb.get_bits(inst, start=25, width=1)
        funct6 = icb.get_bits(inst, start=26, width=6)

        return opcode, vd, funct3, vs1_rs1_imm, vs2, vm, funct6


    @staticmethod
    def __decode_inst_v_load(inst: int) -> tuple:
        opcode = icb.get_bits(inst, start=0,width=7)
        vd = icb.get_bits(inst, start=7,width=5)
        width_code = icb.get_bits(inst, start=12,width=3)
        rs1 = icb.get_bits(inst, start=15,width=5)
        lumop_rs2_vs2 = icb.get_bits(inst, start=20,width=5)
        vm = icb.get_bits(inst, start=25,width=1)
        mop = icb.get_bits(inst, start=26,width=2)
        mew = icb.get_bits(inst, start=28,width=1)
        nf = icb.get_bits(inst, start=29,width=3)

        return opcode, vd, width_code, rs1, lumop_rs2_vs2, vm, mop, mew, nf


    @staticmethod
    def __decode_inst_v_store(inst: int) -> tuple:
        opcode = icb.get_bits(inst, start=0, width=7)
        vs3 = icb.get_bits(inst, start=7, width=5)
        width_code = icb.get_bits(inst, start=12, width=3)
        rs1 = icb.get_bits(inst, start=15, width=5)
        sumop_rs2_vs2 = icb.get_bits(inst, start=20, width=5)
        vm = icb.get_bits(inst, start=25, width=1)
        mop = icb.get_bits(inst, start=26, width=2)
        mew = icb.get_bits(inst, start=28, width=1)
        nf = icb.get_bits(inst, start=29, width=3)

        return opcode, vs3, width_code, rs1, sumop_rs2_vs2, vm, mop, mew, nf
    
    