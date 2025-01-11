from random import randint, choice
from ..common.helpers import repeated_random
from ..common.supported_features import V_LOAD, V_STORE, VECTOR_INSTS, SCALAR_INSTS, TYPE_WIDTHS
from .ga import run_evolution


def generate_operator_sequence(configs):
    '''
    Receive the configs and run evoluation from genetic algorithm
    to generate operator sequence.
    '''
    operator_seq, _ = run_evolution(configs)
    return operator_seq


def add_operands(operator_sequence, configs):
    '''
    Receive a operator sequence and add operands
    to get the completed instruction sequence.
    '''
    
    used_vd_regs = set()
    used_x_regs = set()

    completed_inst_sequence = []

    for operator in operator_sequence:
        inst = {
            'operator': operator,
            'vm': True if configs['vector_masking'] else choice([True, False])
            # vm = 1 --> asm_vm = nothing --> unmasked
            # vm = 0 --> asm_vm = v0.t    --> vector result, only where v0[i][0] = 1
        }

        group = VECTOR_INSTS[operator]['group']
        if group.startswith('v_arith'):
            # Randomize instruction format
            format = choice(VECTOR_INSTS[operator]['formats'])
            inst['format'] = format
            
            # Randomize vs2 register
            inst['vs2'] = repeated_random(0, 31, used_vd_regs, configs['v_reg_reuse_rate'])

            if format in ['vv', 'v.v', 'vvm']:
                inst['vs1'] = repeated_random(0, 31, used_vd_regs, configs['v_reg_reuse_rate'])
            elif format in ['vx', 'v.x', 'vxm']:
                inst['rs1'] = repeated_random(0, 31, used_x_regs, configs['x_reg_reuse_rate'])
                used_x_regs.add(inst['rs1'])
            elif format in ['vi', 'v.i', 'vim']:
                inst['imm'] = randint(0b00000, 0b11111)

            inst['vd'] = randint(0, 31)
            used_vd_regs.add(inst['vd'])
        
        else: # V_LOAD or V_STORE
            inst['width'] = choice(VECTOR_INSTS[operator]['widths'])
            inst['rs1'] = repeated_random(1, 31, used_x_regs, configs['x_reg_reuse_rate'])
            used_x_regs.add(inst['rs1'])
          
            if operator == 'vlse' or operator == 'vsse':
                inst['rs2'] = randint(0, 31)
                used_x_regs.add(inst['rs2'])
            elif operator == 'vluxei' or operator == 'vsuxei':
                inst['vs2'] = repeated_random(0, 31, used_vd_regs, configs['v_reg_reuse_rate'])

            if operator in V_LOAD:
                inst['vd'] = randint(0, 31)
                used_vd_regs.add(inst['vd'])
            elif operator in V_STORE:
                inst['vs3'] = repeated_random(0, 31, used_vd_regs, configs['v_reg_reuse_rate'])

        completed_inst_sequence.append(inst)

    return completed_inst_sequence


def insert_vm_change_placeholders(inst_sequence: list, configs):
    num_of_insts = configs['num_of_insts']
    num_of_vms = 0 if (configs['vector_masking']) else \
                 int(num_of_insts * configs['vector_masking_change_rate'])

    if num_of_vms == 0:
        return inst_sequence
    
    strip = num_of_insts // num_of_vms

    inst_sequence.insert(0, {
        'operator': 'placeholder.chgvm',
        'vm_label': f'__vm0__'
    })
    start_pos = 1
    for i in range(1, num_of_vms + 1):
        insert_pos = randint(start_pos, start_pos + strip - 1)

        inst_sequence.insert(insert_pos + 1, {
            'operator': 'placeholder.chgvm',
            'vm_label': f'__vm{i}__'
        })

        start_pos = strip * i + 1 + 1

    return inst_sequence


def replace_vm_change_placeholders(inst_sequence: list):
    updated_sequence = []

    for inst in inst_sequence:
        if inst['operator'] == 'placeholder.chgvm':
            vm_label = inst['vm_label']

            imm20 = f"%hi({vm_label})"
            imm12 = f"%lo({vm_label})"

            updated_sequence.extend([
                {'operator': 'lui', 'rd': 1, 'imm20': imm20},
                {'operator': 'addi', 'rd': 1, 'rs1': 1, 'imm12': imm12},
                {'operator': 'vle', 'width': 8, 'vd': 0, 'rs1': 1, 'vm': True}
            ])
        else:
            updated_sequence.append(inst)
    
    return updated_sequence


def display_inst(inst):
    operator = inst['operator']
    if operator in VECTOR_INSTS:
        group = VECTOR_INSTS[operator]['group']
        if group.startswith('v_load') or group.startswith('v_store'):
            assembly = f"{operator}{inst['width']}.v "

            if operator in V_LOAD:
                assembly += f"v{inst['vd']}, (x{inst['rs1']})"
            elif operator in V_STORE:
                assembly += f"v{inst['vs3']}, (x{inst['rs1']})"
            
            if operator in ['vlse', 'vsse']:
                assembly += f", x{inst['rs2']}"
            elif operator in ['vluxei', 'vsuxei']:
                assembly += f", v{inst['vs2']}"

            if not (inst['vm']):
                assembly += ', v0.t'

            return assembly
    
        else:
            if operator == 'vmerge':
                if inst['format'] == 'vvm':
                    return f"vmerge.vvm v{inst['vd']}, v{inst['vs2']}, v{inst['vs1']}, v0.t"
                elif inst['format'] == 'vxm':
                    return f"vmerge.vxm v{inst['vd']}, v{inst['vs2']}, x{inst['rs1']}, v0.t"
                elif inst['format'] == 'vim':
                    return f"vmerge.vim v{inst['vd']}, v{inst['vs2']}, 0x{inst['imm']:x}, v0.t"

            elif operator == 'vmv':
                if inst['format'] == 'v.v':
                    return f"vmv.v.v v{inst['vd']}, v{inst['vs1']}"
                elif inst['format'] == 'v.x':
                    return f"vmv.v.x v{inst['vd']}, x{inst['rs1']}"
                elif inst['format'] == 'v.i':
                    return f"vmv.v.i v{inst['vd']}, 0x{inst['imm']:x}"
            
            else:
                assembly = f"{operator}.{inst['format']} v{inst['vd']}, v{inst['vs2']}, "
                if inst['format'] == 'vv':
                    assembly += f"v{inst['vs1']}"
                elif inst['format'] == 'vx':
                    assembly += f"x{inst['rs1']}"
                elif inst['format'] == 'vi':
                    assembly += f"0x{inst['imm']:x}"

                if not (inst['vm']):
                    assembly += ', v0.t'

                return assembly
        
    elif operator in SCALAR_INSTS:
        group = SCALAR_INSTS[operator]['group']
        if group.startswith('i_type'):
            imm12 = inst['imm12']
            return f"{operator} x{inst['rd']}, x{inst['rs1']}, {imm12 if type(imm12) == str else hex(imm12)}"
        elif group.startswith('u_type'):
            imm20 = inst['imm20']
            return f"{operator} x{inst['rd']}, {imm20 if type(imm20) == str else hex(imm20)}"
        
    else:
        raise ValueError(f"Unsupported operator: '{operator}'")


def display_data_def(label, data_def):
    return f"{label}: {data_def['type']} {', '.join([hex(item) for item in data_def['items']])}"
    

def display(
    data_section,
    init_text_seq,
    main_text_seq,
):
    TAB = 4 * ' '

    asm_data_section = ''
    for label, data_def in data_section.items():
        asm_data_section += display_data_def(label, data_def) + '\n'

    asm_init_text = ''
    asm_init_sequence = [display_inst(inst) for inst in init_text_seq]
    for inst in asm_init_sequence:
        asm_init_text +=f'{TAB}{inst}\n'


    asm_main_text = ''
    asm_main_sequence = [display_inst(inst) for inst in main_text_seq]
    for inst in asm_main_sequence:
        asm_main_text += f'{TAB}{inst}\n'

    return '.data\n' + \
        asm_data_section + \
        '\n' + \
        '.text\n' + \
        'init:\n' + \
        asm_init_text + \
        'main:\n' + \
        asm_main_text

