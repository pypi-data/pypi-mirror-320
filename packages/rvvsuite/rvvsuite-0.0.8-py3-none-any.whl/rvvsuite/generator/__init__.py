from .confparser import parse_config_file
from .vrtg import generate_operator_sequence, add_operands, insert_vm_change_placeholders, replace_vm_change_placeholders, display
from .init_data_generator import trace_uninitialzed_operands, init_data


def generate(configs):
    operator_seq = generate_operator_sequence(configs)
    main_text_seq = add_operands(operator_seq, configs)
    main_text_seq = insert_vm_change_placeholders(main_text_seq, configs)
    vregs2init, xreg2init, vms2init = trace_uninitialzed_operands(main_text_seq)
    data_section, init_text_seq = init_data(vregs2init, xreg2init, vms2init, configs)
    main_text_seq = replace_vm_change_placeholders(main_text_seq)
    
    return data_section, init_text_seq, main_text_seq

