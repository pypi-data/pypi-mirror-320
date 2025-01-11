ELEN = 32
VLEN = 128

V_ADDSUB = ['vadd', 'vsub', 'vrsub']
V_BITWISE = ['vand', 'vor', 'vxor']
V_SHIFT = ['vsll', 'vsrl', 'vsra']
V_COMPARE = ['vmseq', 'vmsne', 'vmsltu', 'vmslt', 'vmsleu', 'vmsle', 'vmsgtu', 'vmsgt']
V_MINMAX = ['vminu', 'vmin', 'vmaxu', 'vmax']
V_MERGEMV = ['vmerge', 'vmv']

V_ARITH = V_ADDSUB + V_BITWISE + V_SHIFT + V_COMPARE + V_MINMAX + V_MERGEMV
V_LOAD = ['vle', 'vlse', 'vluxei']
V_STORE = ['vse', 'vsse', 'vsuxei']

V_ALL = V_ARITH + V_LOAD + V_STORE


TYPE_WIDTHS = {# unit: bit
    '.byte': 8,
    '.half': 16,
    '.word': 32
}

DATA_TYPES = list(TYPE_WIDTHS.keys())

WIDTH_CODES = {
    8: 0b000,
    16: 0b101,
    32: 0b110
}


MOPS = {
    'vle': 0b00,
    'vluxei': 0b01,
    'vlse': 0b10,
    'vloxei': 0b11,

    'vse': 0b00,
    'vsuxei': 0b01,
    'vsse': 0b10,
    'vsoxei': 0b11,
}

VECTOR_INSTS = {
    'vadd': {'formats': ['vv', 'vx', 'vi'], 'group': 'v_arith/v_addsub', 'syntax': 'vadd.<format> <vd>, <vs2>, <vs1|rs1|imm>[, v0.t]', 'funct6': 0b000000},
    'vsub': {'formats': ['vv', 'vx'], 'group': 'v_arith/v_addsub', 'syntax': 'vsub.<format> <vd>, <vs2>, <vs1|rs1>[, v0.t]', 'funct6': 0b000010},
    'vrsub': {'formats': ['vx', 'vi'], 'group': 'v_arith/v_addsub', 'syntax': 'vrsub.<format> <vd>, <vs2>, <rs1|imm>[, v0.t]', 'funct6': 0b000011},
    'vand': {'formats': ['vv', 'vx', 'vi'], 'group': 'v_arith/v_bitwise', 'syntax': 'vand.<format> <vd>, <vs2>, <vs1|rs1|imm>[, v0.t]', 'funct6': 0b001001},
    'vor': {'formats': ['vv', 'vx', 'vi'], 'group': 'v_arith/v_bitwise', 'syntax': 'vor.<format> <vd>, <vs2>, <vs1|rs1|imm>[, v0.t]', 'funct6': 0b001010},
    'vxor': {'formats': ['vv', 'vx', 'vi'], 'group': 'v_arith/v_bitwise', 'syntax': 'vxor.<format> <vd>, <vs2>, <vs1|rs1|imm>[, v0.t]', 'funct6': 0b001011},
    'vsll': {'formats': ['vv', 'vx', 'vi'], 'group': 'v_arith/v_shift', 'syntax': 'vsll.<format> <vd>, <vs2>, <vs1|rs1|imm>[, v0.t]', 'funct6': 0b100101},
    'vsrl': {'formats': ['vv', 'vx', 'vi'], 'group': 'v_arith/v_shift', 'syntax': 'vsrl.<format> <vd>, <vs2>, <vs1|rs1|imm>[, v0.t]', 'funct6': 0b101000},
    'vsra': {'formats': ['vv', 'vx', 'vi'], 'group': 'v_arith/v_shift', 'syntax': 'vsra.<format> <vd>, <vs2>, <vs1|rs1|imm>[, v0.t]', 'funct6': 0b101001},
    'vmseq': {'formats': ['vv', 'vx', 'vi'], 'group': 'v_arith/v_compare', 'syntax': 'vmseq.<format> <vd>, <vs2>, <vs1|rs1|imm>[, v0.t]', 'funct6': 0b011000},
    'vmsne': {'formats': ['vv', 'vx', 'vi'], 'group': 'v_arith/v_compare', 'syntax': 'vmsne.<format> <vd>, <vs2>, <vs1|rs1|imm>[, v0.t]', 'funct6': 0b011001},
    'vmsltu': {'formats': ['vv', 'vx'], 'group': 'v_arith/v_compare', 'syntax': 'vmsltu.<format> <vd>, <vs2>, <vs1|rs1>[, v0.t]', 'funct6': 0b011010},
    'vmslt': {'formats': ['vv', 'vx'], 'group': 'v_arith/v_compare', 'syntax': 'vmslt.<format> <vd>, <vs2>, <vs1|rs1>[, v0.t]', 'funct6': 0b011011},
    'vmsleu': {'formats': ['vv', 'vx', 'vi'], 'group': 'v_arith/v_compare', 'syntax': 'vmsleu.<format> <vd>, <vs2>, <vs1|rs1|imm>[, v0.t]', 'funct6': 0b011100},
    'vmsle': {'formats': ['vv', 'vx', 'vi'], 'group': 'v_arith/v_compare', 'syntax': 'vmsle.<format> <vd>, <vs2>, <vs1|rs1|imm>[, v0.t]', 'funct6': 0b011101},
    'vmsgtu': {'formats': ['vx', 'vi'], 'group': 'v_arith/v_compare', 'syntax': 'vmsgtu.<format> <vd>, <vs2>, <rs1|imm>[, v0.t]', 'funct6': 0b011110},
    'vmsgt': {'formats': ['vx', 'vi'], 'group': 'v_arith/v_compare', 'syntax': 'vmsgt.<format> <vd>, <vs2>, <rs1|imm>[, v0.t]', 'funct6': 0b011111},
    'vminu': {'formats': ['vv', 'vx'], 'group': 'v_arith/v_minmax', 'syntax': 'vminu.<format> <vd>, <vs2>, <vs1|rs1>[, v0.t]', 'funct6': 0b000100},
    'vmin': {'formats': ['vv', 'vx'], 'group': 'v_arith/v_minmax', 'syntax': 'vmin.<format> <vd>, <vs2>, <vs1|rs1>[, v0.t]', 'funct6': 0b000101},
    'vmaxu': {'formats': ['vv', 'vx'], 'group': 'v_arith/v_minmax', 'syntax': 'vmaxu.<format> <vd>, <vs2>, <vs1|rs1>[, v0.t]', 'funct6': 0b000110},
    'vmax': {'formats': ['vv', 'vx'], 'group': 'v_arith/v_minmax', 'syntax': 'vmax.<format> <vd>, <vs2>, <vs1|rs1>[, v0.t]', 'funct6': 0b000111},
    'vmerge': {'formats': ['vvm', 'vxm', 'vim'], 'group': 'v_arith/v_mergemv', 'syntax': 'vmerge.<format> <vd>, <vs2>, <vs1|rs1|imm>, v0.t', 'funct6': 0b010111},
    'vmv': {'formats': ['v.v', 'v.x', 'v.i'], 'group': 'v_arith/v_mergemv', 'syntax': 'vmv.<format> <vd>, <vs1|rs1|imm>', 'funct6': 0b010111},
    'vle': {'widths': [8, 16, 32], 'group': 'v_load', 'syntax': 'vle<width>.v <vd>, (<rs1>)[, v0.t]'},
    'vlse': {'widths': [8, 16, 32], 'group': 'v_load', 'syntax': 'vlse<width>.v <vd>, (<rs1>), <rs2>[, v0.t]'},
    'vluxei': {'widths': [8, 16, 32], 'group': 'v_load', 'syntax': 'vluxei<width>.v <vd>, (<rs1>), <vs2>[, v0.t]'},
    'vse': {'widths': [8, 16, 32], 'group': 'v_store', 'syntax': 'vse<width>.v <vs3>, (<rs1>)[, v0.t]'},
    'vsse': {'widths': [8, 16, 32], 'group': 'v_store', 'syntax': 'vsse<width>.v <vs3>, (<rs1>), <rs2>[, v0.t]'},
    'vsuxei': {'widths': [8, 16, 32], 'group': 'v_store', 'syntax': 'vsuxei<width>.v <vs3>, (<rs1>), <vs2>[, v0.t]'},
}

SCALAR_INSTS = { # RV32I
    'lui': {'opcode': 0b0110111, 'group': 'u_type', 'syntax': 'lui <rd>, <imm20>'},
    'addi': {'opcode': 0b0010011, 'group': 'i_type', 'syntax': 'addi <rd>, <rs1>, <imm12>', 'funct3': 0b000}
}


SUPPORTED_INSTS = VECTOR_INSTS | SCALAR_INSTS # Merge


# Mapping
GROUP_OF_OPCODES = {
    0b0110111: 'u_type',
    0b0010011: 'i_type'
}

FUNCT6_TO_INST_MAP = {v['funct6']: k for k, v in VECTOR_INSTS.items() if 'funct6' in v}