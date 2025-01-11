from ..common.supported_features import SUPPORTED_INSTS, MOPS, WIDTH_CODES


def translate_data(data):
    dmem = ''
    for label, data_def in data.items():
        for item in data_def['items']:
            for _ in range(data_def['width'] // 8):
                dmem += bin(int(item % (2 ** 8)))[2:].zfill(8) + '\n'
                item //= (2 ** 8)

    return dmem


def icb_of_v_arith(format, funct6, vd, vs2, vs1, rs1, imm, vm):
    if format in ['vv', 'vvm', 'v.v']:
        funct3 = 0b000
        bit_19_15 = vs1
    elif format in ['vx', 'vxm', 'v.x']:
        funct3 = 0b100
        bit_19_15 = rs1
    elif format in ['vi', 'vim', 'v.i']:
        funct3 = 0b011
        bit_19_15 = imm

    icb = 0b1010111 # opcode
    icb |= (vd << 7)
    icb |= (funct3 << 12)
    icb |= (bit_19_15 << 15)
    icb |= (vs2 << 20)
    icb |= (int(vm) << 25)
    icb |= (funct6 << 26)

    return icb


def icb_of_v_store(mop, width, vs3, rs1, rs2, vs2, vm, sumop=0b00000, nf=0b000, mew=0b0):
    if mop == 0b00:
        bit_24_20 = sumop
    elif mop == 0b01:
        bit_24_20 = vs2
    elif mop == 0b10:
        bit_24_20 = rs2

    icb = 0b0100111 # opcode
    icb |= (vs3 << 7)
    icb |= (width << 12)
    icb |= (rs1 << 15)
    icb |= (bit_24_20 << 20)
    icb |= (int(vm) << 25)
    icb |= (mop << 26)
    icb |= (mew << 28)
    icb |= (nf << 29)

    return icb


def icb_of_v_load(mop, width, vd, rs1, rs2, vs2, vm, lumop=0b00000, nf=0b00, mew=0b0):
    if mop == 0b00:
        bit_24_20 = lumop
    elif mop == 0b01:
        bit_24_20 = vs2
    elif mop == 0b10:
        bit_24_20 = rs2

    icb = 0b0000111 # opcode
    icb |= (vd << 7)
    icb |= (width << 12)
    icb |= (rs1 << 15)
    icb |= (bit_24_20 << 20)
    icb |= (int(vm) << 25)
    icb |= (mop << 26)
    icb |= (mew << 28)
    icb |= (nf << 29)

    return icb


def icb_of_u_type(opcode, rd, imm20):
    icb = opcode
    icb |= (rd << 7)
    icb |= (imm20 << 12)

    return icb


def icb_of_i_type(opcode, funct3, rd, rs1, imm12):
    icb = opcode
    icb |= (rd << 7)
    icb |= (funct3 << 12)
    icb |= (rs1 << 15)
    icb |= (imm12 << 20)

    return icb


def translate_text(text):
    imem = ''
    for inst in text:
        inst_params = SUPPORTED_INSTS[inst['op']]
        group = inst_params['group']
        if group.startswith('v_arith'):
            funct6 = inst_params['funct6']
            vs2 = inst['vs2'] if 'vs2' in inst else 0
            vs1 = inst['vs1'] if 'vs1' in inst else None
            rs1 = inst['rs1'] if 'rs1' in inst else None
            imm = inst['imm'] if 'imm' in inst else None
            vm = inst['vm'] if 'vm' in inst else True
            icb = icb_of_v_arith(inst['format'], funct6, inst['vd'], vs2, vs1, rs1, imm, vm)
            
        elif group.startswith('v_store'):
            mop = MOPS[inst['op']]
            rs2 = inst['rs2'] if 'rs2' in inst else None
            vs2 = inst['vs2'] if 'vs2' in inst else None
            icb = icb_of_v_store(mop, WIDTH_CODES[inst['width']], inst['vs3'], inst['rs1'], rs2, vs2, inst['vm'])

        elif group.startswith('v_load'):
            mop = MOPS[inst['op']]
            rs2 = inst['rs2'] if 'rs2' in inst else None
            vs2 = inst['vs2'] if 'vs2' in inst else None
            icb = icb_of_v_load(mop, WIDTH_CODES[inst['width']], inst['vd'], inst['rs1'], rs2, vs2, inst['vm'])
        
        # Below cases for scalar instructions
        elif group.startswith('u_type'):
            icb = icb_of_u_type(inst_params['opcode'], inst['rd'], inst['imm20'])

        elif group.startswith('i_type'):
            icb = icb_of_i_type(inst_params['opcode'], inst_params['funct3'], inst['rd'], inst['rs1'], inst['imm12'])
        
        imem += bin(icb)[2:].zfill(32) + '\n'

    return imem