from random import choices, randint
from ..common.supported_features import DATA_TYPES, TYPE_WIDTHS
from ..common.helpers import random_imm, split_imm

def trace_uninitialzed_operands(text_seq):
    vregs2init = set()
    xregs2init = set()
    vms2init = []

    for inst in reversed(text_seq):
        if inst['operator'] == 'placeholder.chgvm':
            vms2init.insert(0, inst['vm_label'])
            continue

        if 'vs3' in inst:
            vregs2init.add(inst['vs3'])
        if 'vs2' in inst:
            vregs2init.add(inst['vs2'])
        if 'vs1' in inst:
            vregs2init.add(inst['vs1'])
        if 'vd' in inst and inst['vd'] in vregs2init:
            vregs2init.remove(inst['vd'])

        if 'rs2' in inst:
            xregs2init.add(inst['rs2'])
        if 'rs1' in inst:
            xregs2init.add(inst['rs1'])
        if 'rd' in inst and inst['rd'] in vregs2init:
            xregs2init.remove(inst['rd'])

    return vregs2init, xregs2init, vms2init


# Currently, init values ignore dmem_access_range
def init_data(vregs2init, xregs2init, vms2init, configs):
    data_section = {}
    text_section = []

    addr = 0
    
    for vreg in vregs2init:
        data_type = choices(DATA_TYPES, configs['data_type_weights'])[0]
        data_items = []
        for _ in range(4):
            item, __ = random_imm(TYPE_WIDTHS[data_type], configs['data_variant_weights'])
            data_items.append(item)

        data_def = {
            'addr': addr,
            'type': data_type,
            'items': data_items,
        }
        data_section[f'_v{vreg}_'] = data_def

        imm20 = f"%hi(_v{vreg}_)"
        imm12 = f"%lo(_v{vreg}_)"

        text_section.extend([
            {'operator': 'lui', 'rd': 1, 'imm20': imm20},
            {'operator': 'addi', 'rd': 1, 'rs1': 1, 'imm12': imm12},
            {'operator': 'vle', 'width' : TYPE_WIDTHS[data_type], 'vd': vreg, 'rs1': 1, 'vm': True}
        ])

        addr += TYPE_WIDTHS[data_type] * len(data_items)

    for xreg in xregs2init:
        if xreg == 0:
            continue
        
        data_type = choices(DATA_TYPES, configs['data_type_weights'])[0]
        value, is_big = random_imm(TYPE_WIDTHS[data_type], configs['data_variant_weights'])
        if is_big:
            hi20b, lo12b = split_imm(value)

            text_section.extend([
                {'operator': 'lui', 'rd': xreg, 'imm20': hi20b},
                {'operator': 'addi', 'rd': xreg, 'rs1': xreg, 'imm12': lo12b},
            ])
        else:
            text_section.append(
                {'operator': 'addi', 'rd': xreg, 'rs1': 0, 'imm12': value}
            )

    for vm_label in vms2init:
        data_def = {
            'addr': addr,
            'type': '.byte',
            'items': [randint(0, 1 << 8) for _ in range(4)]
        }
        data_section[vm_label] = data_def
        addr += TYPE_WIDTHS[data_type] * len(data_items)

    return data_section, text_section