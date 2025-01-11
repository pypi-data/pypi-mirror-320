import re

from ..common.supported_features import DATA_TYPES, TYPE_WIDTHS, SUPPORTED_INSTS, VECTOR_INSTS, SCALAR_INSTS
from ..common.helpers import code_number, print_error_and_exit


def sectionify(asm: str):
    text_section = {}
    data_section = {}
    current_section = 'text' # Default is .text section
    
    lines = asm.splitlines()
    for i in range(len(lines)):
        line = lines[i].strip()
        
        if line == '':
            continue

        section_match = re.match(r'^\.(?P<section>text|data)\b', line)
        if section_match:
            current_section = section_match.group('section') # Update current section
        else: # If in a section, add the line to it
            if current_section == 'text':
                text_section[i+1] = line
            elif current_section == 'data':
                data_section[i+1] = line
    
    return text_section, data_section


def parse_data(data_section):
    current_addr = 0
    data = {}
    for line_number, statement in data_section.items():
        # TODO: like .text section, label can be missing; label and data definition can be on multi lines
        statement_match = re.match(r'(?P<label>\w+):\s*(?P<type>\.\w+)\s*(?P<data>[^#]*)(?:\s*#(?P<comment>.*))?', statement)
        
        # Check overall syntax
        if not statement_match:
            print_error_and_exit(line_number, statement, [
                'Right syntax: <label>: <type> <data_item_1>[, <data_item_2>, ...,<data_item_n>][# <comment>]'
                '<label> must start with a letter or _ not a number'
            ])
        
        # Check supported types
        type = statement_match.group('type')
        if type not in DATA_TYPES:
            print_error_and_exit(line_number, statement, [
                f"Unsupported type: '{type}'"
            ])

        # Check data sequence syntax
        data_seq = statement_match.group('data')
        data_match = re.match(r'(?:\s*(?:0b[01]+|0x[0-9a-fA-F]+|\-?\d+)\s*,\s*)*(?:0b[01]+|0x[0-9a-fA-F]+|\-?\d+)\s*', data_seq)

        if not data_match:
            print_error_and_exit(line_number, statement, [
                f"Some thing wrong here: '{type}'"
            ]) # TODO: Modify error message
        
        items = []
        for item in data_seq.split(','):
            item = item.strip()

            number = code_number(item, TYPE_WIDTHS[type])
            if number == -1:
                print_error_and_exit(line_number, statement, [
                    f"Invalid number format '{item}'"
                ])

            # TODO: check overflow

            items.append(number)

        data[statement_match.group('label')] = {
            'addr': current_addr,
            'width': TYPE_WIDTHS[type],
            'items': items
        }

        current_addr += len(items) * TYPE_WIDTHS[type] // 8

    return data


def syntax_2_regex(syntax: str, dynamic_params):
    syntax = syntax.replace('.', r'\.')
    if 'formats' in dynamic_params:
        syntax = syntax.replace('<format>', f"(?P<format>{'|'.join(format.replace('.', '\\.') for format in dynamic_params['formats'])})")
    if 'widths' in dynamic_params:
        syntax = syntax.replace('<width>', f"(?P<width>{'|'.join([str(width) for width in dynamic_params['widths']])})")
    syntax = syntax.replace(' <vd>', r'\s+v(?P<vd>\d+)')
    syntax = syntax.replace(' <rd>', r'\s+x(?P<rd>\d+)')
    syntax = syntax.replace(' <vs3>', r'\s+v(?P<vs3>\d+)')
    syntax = syntax.replace('<vs2>', r'v(?P<vs2>\d+)')
    syntax = syntax.replace('<rs2>', r'x(?P<rs2>\d+)')
    syntax = syntax.replace('<rs1>', r'x(?P<rs1>\d+)')
    syntax = syntax.replace(r'(x(?P<rs1>\d+))', r'(?:\(x(?P<rs1>\d+)\))')
    syntax = syntax.replace('<imm20>', r'(?P<imm20>0b[01]+|0x[0-9a-fA-F]+|\-?\d+)')
    syntax = syntax.replace('<imm12>', r'(?P<imm12>0b[01]+|0x[0-9a-fA-F]+|\-?\d+)')
    syntax = syntax.replace('<vs1|rs1|imm>', r'(?:v(?P<vs1>\d+)|x(?P<rs1>\d+)|(?P<imm>0b[01]+|0x[0-9a-fA-F]+|\-?\d+))')
    syntax = syntax.replace('<vs1|rs1>', r'(?:v(?P<vs1>\d+)|x(?P<rs1>\d+))')
    syntax = syntax.replace('<rs1|imm>', r'(?:x(?P<rs1>\d+)|(?P<imm>0b[01]+|0x[0-9a-fA-F]+|-?\d+))')
    syntax = syntax.replace(r', v0\.t', r'(?:\s*,\s*(?P<vm>v0\.t))')
    syntax = syntax.replace(r'[(?:\s*,\s*(?P<vm>v0\.t))]', r'(?:\s*,\s*(?P<vm>v0\.t))?')
    syntax = syntax.replace(',', r'\s*,')
    syntax = syntax.replace(' ', r'\s*')
    syntax += r'(?:\s*#(?P<comment>.*))?'

    return syntax


def replace_relocation_functions(inst, data):
    hi_reloc_funct_match = re.match(r'.*%hi\((?P<symbol>\w+)\)', inst)
    if hi_reloc_funct_match:
        symbol = hi_reloc_funct_match.group('symbol')
        inst = re.sub(r'%hi\((?P<symbol>\w+)\)', str(data[symbol]['addr'] >> 12), inst)
    
    lo_reloc_funct_match = re.match(r'.*%lo\((?P<symbol>\w+)\)', inst)
    if lo_reloc_funct_match:
        symbol = lo_reloc_funct_match.group('symbol')
        inst = re.sub(r'%lo\((?P<symbol>\w+)\)', str(data[symbol]['addr'] % (2 ** 12)), inst)

    return inst  


def parse_text(text_section, data):
    inst_seq = {}
    labels = {}
    pc_map_line = {}
    pc = 0
    
    for line_number, statement in text_section.items():
        # Check overall syntax: [<label>:][<inst>]
        syntax_match = re.match(r'(?:(?P<label>\w+)\s*:\s*)?(?:(?P<inst>.*))?', statement)
        if not syntax_match:
            print_error_and_exit(line_number, statement, [
                'Right syntax: [<label>: ][<inst>]'
            ])

        label = syntax_match.group('label')
        inst = syntax_match.group('inst')

        if label:
            if label in data:
                print_error_and_exit(line_number, statement, [
                    f"Duplicated label: '{label}'"
                ])
            
            labels[label] = pc

        if inst:
            inst_seq[pc] = inst
            pc_map_line[pc] = line_number
            pc += 4

    text = []
    for addr, inst in inst_seq.items():
        # Check supported operator
        op_match = re.match(r'^[a-z]+', inst)
        op = op_match.group(0)
        if op in VECTOR_INSTS:
            inst_params = VECTOR_INSTS[op]
            inst_pattern = syntax_2_regex(inst_params['syntax'], inst_params)

            # Check syntax
            inst_match = re.match(inst_pattern, inst)
            if not inst_match:
                print_error_and_exit(pc_map_line[addr], text_section[pc_map_line[addr]], [
                    f"The instruction must follow this pattern: {inst_params['syntax']}[# <comment>]"
                ])

            # Check valid params
            cuptured_params = inst_match.groupdict()
            inst_params = {'op': op}
            if 'format' in cuptured_params and not cuptured_params['format'] == None:
                inst_params['format'] = cuptured_params['format']
            
            if 'width' in cuptured_params and not cuptured_params['width'] == None:
                inst_params['width'] = int(cuptured_params['width'])

            if op != 'vmv':
                inst_params['vm'] = (cuptured_params['vm'] == None)
            
            if 'vd' in cuptured_params and not cuptured_params['vd'] == None:
                vd = int(cuptured_params['vd'])
                if vd < 0 or vd > 31:
                    print_error_and_exit(pc_map_line[addr], text_section[pc_map_line[addr]], [
                        f'Invalid vd: v{vd}'
                    ])
                inst_params['vd'] = vd
                
            if 'vs3' in cuptured_params and not cuptured_params['vs3'] == None:
                vs3 = int(cuptured_params['vs3'])
                if vs3 < 0 or vs3 > 31:
                    print_error_and_exit(pc_map_line[addr], text_section[pc_map_line[addr]], [
                        f'Invalid vs3: v{vs3}'
                    ])
                inst_params['vs3'] = vs3

            if 'vs2' in cuptured_params and not cuptured_params['vs2'] == None:
                vs2 = int(cuptured_params['vs2'])
                if vs2 < 0 or vs2 > 31:
                    print_error_and_exit(pc_map_line[addr], text_section[pc_map_line[addr]], [
                        f'Invalid vs2: v{vs2}'
                    ])
                inst_params['vs2'] = vs2

            if 'vs1' in cuptured_params and not cuptured_params['vs1'] == None:
                vs1 = int(cuptured_params['vs1'])
                if vs1 < 0 or vs1 > 31:
                    print_error_and_exit(pc_map_line[addr], text_section[pc_map_line[addr]], [
                        f'Invalid vs1: v{vs1}'
                    ])
                inst_params['vs1'] = vs1
                
            if 'rs2' in cuptured_params and not cuptured_params['rs2'] == None:
                rs2 = int(cuptured_params['rs2'])
                if rs2 < 0 or rs2 > 31:
                    print_error_and_exit(pc_map_line[addr], text_section[pc_map_line[addr]], [
                        f'Invalid rs2: x{rs2}'
                    ])
                inst_params['rs2'] = rs2
                
            if 'rs1' in cuptured_params and not cuptured_params['rs1'] == None:
                rs1 = int(cuptured_params['rs1'])
                if rs1 < 0 or rs1 > 31:
                    print_error_and_exit(pc_map_line[addr], text_section[pc_map_line[addr]], [
                        f'Invalid rs1: x{rs1}'
                    ])
                inst_params['rs1'] = rs1

            if 'imm' in cuptured_params and not cuptured_params['imm'] == None:
                imm = code_number(cuptured_params['imm'], 5)
                if imm == -1 or imm > 31:
                    print_error_and_exit(pc_map_line[addr], text_section[pc_map_line[addr]], [
                        'Invalid imm'
                    ])
                inst_params['imm'] = imm

        elif op in SCALAR_INSTS:
            # Replace Relocation Functions by Addresses
            inst = replace_relocation_functions(inst, data)
            
            inst_params = SCALAR_INSTS[op]
            inst_pattern = syntax_2_regex(inst_params['syntax'], inst_params)

            # Check syntax
            inst_match = re.match(inst_pattern, inst)
            if not inst_match:
                print_error_and_exit(pc_map_line[addr], text_section[pc_map_line[addr]], [
                    f"The instruction must follow this pattern: {inst_params['syntax']}[# <comment>]"
                ])

            # Check valid params
            cuptured_params = inst_match.groupdict()
            inst_params = {'op': op}
            
            if 'rd' in cuptured_params and not cuptured_params['rd'] == None:
                rd = int(cuptured_params['rd'])
                if rd < 0 or rd > 31:
                    print_error_and_exit(pc_map_line[addr], text_section[pc_map_line[addr]], [
                        f'Invalid rd: x{rd}'
                    ])
                inst_params['rd'] = rd

            if 'rs2' in cuptured_params and not cuptured_params['rs2'] == None:
                rs2 = int(cuptured_params['rs2'])
                if rs2 < 0 or rs2 > 31:
                    print_error_and_exit(pc_map_line[addr], text_section[pc_map_line[addr]], [
                        f'Invalid rs2: x{rs2}'
                    ])
                inst_params['rs2'] = rs2

            if 'rs1' in cuptured_params and not cuptured_params['rs1'] == None:
                rs1 = int(cuptured_params['rs1'])
                if rs1 < 0 or rs1 > 31:
                    print_error_and_exit(pc_map_line[addr], text_section[pc_map_line[addr]], [
                        f'Invalid rs1: x{rs1}'
                    ])
                inst_params['rs1'] = rs1

            if 'imm20' in cuptured_params and not cuptured_params['imm20'] == None:
                imm20 = code_number(cuptured_params['imm20'], 20)
                if imm20 == -1 or imm20 > 2 ** 20 - 1:
                    print_error_and_exit(pc_map_line[addr], text_section[pc_map_line[addr]], [
                        'Invalid imm20'
                    ])
                inst_params['imm20'] = imm20

            if 'imm12' in cuptured_params and not cuptured_params['imm12'] == None:
                imm12 = code_number(cuptured_params['imm12'], 12)
                if imm12 == -1 or imm12 > 2 ** 12 - 1:
                    print_error_and_exit(pc_map_line[addr], text_section[pc_map_line[addr]], [
                        'Invalid imm12'
                    ])
                inst_params['imm12'] = imm12

            if 'imm5' in cuptured_params and not cuptured_params['imm5'] == None:
                imm5 = code_number(cuptured_params['imm5'], 5)
                if imm5 == -1 or imm5 > 2 ** 5 - 1:
                    print_error_and_exit(pc_map_line[addr], text_section[pc_map_line[addr]], [
                        'Invalid imm5'
                    ])
                inst_params['imm5'] = imm5

        else:
            print_error_and_exit(pc_map_line[addr], text_section[pc_map_line[addr]], [
                f"Unsupported operator: '{op}'"
            ])

        text.append(inst_params)
    
    return text

        