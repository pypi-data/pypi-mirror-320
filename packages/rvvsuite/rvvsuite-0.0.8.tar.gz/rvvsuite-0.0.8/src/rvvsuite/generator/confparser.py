import json
from ..common.helpers import ask_user



CONFIG_SCHEMAS = {
    'num_of_tests': {
        'type': int,
        'required': True,
        'min': 1,
    },
    'test_prefix': {
        'type': str,
        'default': 'test',
    },
    'num_of_insts': {
        'type': int,
        'required': True,
        'min': 10,
    },
    'v_arith': {
        'type': [int, float],
        'default': 14,
    },
    'v_load': {
        'type': [int, float],
        'default': 3,
    },
    'v_store': {
        'type': [int, float],
        'default': 3,
    },
    'v_reg_reuse_rate': {
        'type': float,
        'default': 0.3,
        'min': 0.0,
        'max': 1.0,
        'typical_min': 0.1,
        'typical_max': 0.4,
    },
    'x_reg_reuse_rate': {
        'type': float,
        'default': 0.1,
        'min': 0.0,
        'max': 1.0,
        'typical_min': 0.05,
        'typical_max': 0.3,
    },
    "data_type_weights": {
        'type': list,
        'length': 3,
        'item_type': [int, float],
        'default': [1, 1, 1] # [.byte, .half, .word]
    },
    "data_variant_weights": {
        'type': list,
        'length': 4,
        'item_type': [int, float],
        'default': [1, 3, 3, 3] # [zero, neg, pos, big_num]
    },
    'vector_masking': {
        'type': bool,
        'default': False
    },
    "vector_masking_change_rate": { # this schema must be defined after 'vector_masking'
        'type': float,
        'default': 0.2,
        'min': 0.0,
        'max': 1.0,
        'typical_min': 0.05,
        'typical_max': 0.3,
    },
    'dmem_size': { # TODO: check align, multiples of 4
        'type': int,
        'required': True,
        'min': 4 * (2 ** 10), # 4096 bytes = 1024 words  
    },
    'dmem_access_range_start': { # TODO: check align, multiples of 4
        'type': int,
        'default': 0,
    },
    'dmem_access_range_end': { # TODO: check align, multiples of 4
        'type': int,
        'default': '$dmem_size',
    },
    'rtg': {
        'mutate_rate': {
            'type': float,
            'default': 0.1,
            'min': 0.0,
            'max': 1.0,
            'typical_min': 0.05,
            'typical_max': 0.2,
        },
        'population_size': {
            'type': int,
            'default': 10,
            'min': 5,
            'typical_min': 5,
            'typical_max': 20,    
        }
    },
}

def _validate_configs(configs, schemas):
    output_configs = {}

    for key, schema in schemas.items():
        if key not in configs:
            if key =='rtg': # sub-schemas
                output_configs['rtg'] = _validate_configs({}, schema)
                continue

            is_required = schema.get('required', False)
            if is_required:
                print(f'[Config Reading][Error] \'{key}\' is required.')
                exit(-1)
            else:
                default_value = schema['default']
                if type(default_value) == str and default_value[0] == '$':
                    output_configs[key] = output_configs[default_value[1:]]
                    print(f'[Config Reading][Info] \'{key}\' is not defined, take default: \'{output_configs[default_value[1:]]}\'.')
                else:
                    output_configs[key] = default_value
                    print(f'[Config Reading][Info] \'{key}\' is not defined, take default: \'{default_value}\'.')
                continue
        
        config = configs[key]

        # sub-schemas
        if key == 'rtg':
            if type(config) != dict:
                print(f'[Config Reading][Error] \'{key}\' is must be a sub-config.')
                exit(-1)

            output_configs['rtg'] = _validate_configs(config, schema)
            configs.pop(key)
            continue
        
        # check dependent configs
        if key == 'vector_masking_change_rate' and output_configs['vector_masking']:
            print(f'[Config Reading][Info] \'{key}\' is useless in case \'vector_masking\' is True (unmasked).')
            configs.pop(key)
            continue

        # check type
        expected_type = schema['type']
        current_type = type(config)
        if (type(expected_type) == list): # check multi type
            if current_type not in expected_type:
                print(f"[Config Reading][Error] '{key}' must be {' or '.join([t.__name__ for t in expected_type])}, but it is {current_type.__name__}.")
                exit(-1)
        elif expected_type == list: # check list
            expected_length = schema['length']
            current_length = len(config)
            if current_length != expected_length: # check length
                print(f"[Config Reading][Error] '{key}' must be list of {expected_length} items, but it contains {current_length}.")
                exit(-1)
            expected_item_type = schema['item_type']
            if type(expected_item_type) == list:
                if any(type(item) not in expected_item_type for item in config): # check multi type of items
                    print(f"[Config Reading][Error] '{key}' must be list of {'s or '.join([t.__name__ for t in expected_item_type])}s.")
                    exit(-1)
            else:
                if any(type(item) != expected_item_type for item in config): # check single type of items
                    print(f"[Config Reading][Error] '{key}' must be list of {expected_item_type}s.")
                    exit(-1)
        else:
            if current_type != expected_type: # check single type
                print(f'[Config Reading][Error] \'{key}\' must be {expected_type.__name__}, but it is {current_type.__name__}.')
                exit(-1)

        # check range
        min = schema.get('min', None)
        max = schema.get('max', None)
        if min is not None and config < min:
            print(f'[Config Reading][Error] \'{key}\' must be greater than \'{min}\'.')
            exit(-1)

        if max is not None and config > max:
            print(f'[Config Reading][Error] \'{key}\' must be less than \'{max}\'.')
            exit(-1)

        # check typical range
        typical_min = schema.get('typical_min', None)
        typical_max = schema.get('typical_max', None)
        if typical_min is not None and config < typical_min:
            print(f'[Config Reading][Warning] \'{key}\' should be greater than \'{typical_min}\'.')
            if not ask_user('Do you want continue?'):
                exit(1)

        if typical_max is not None and config > typical_max:
            print(f'[Config Reading][Warning] \'{key}\' should be less than \'{typical_max}\'.')
            if not ask_user('Do you want continue?'):
                exit(1)

        # add to output configs and remove from input configs
        output_configs[key] = config
        configs.pop(key)

    # check invalid for unsupported configs
    for key, config in configs.items():
        print(f'[Config Reading][Warning] \'{key}\' is invalid or unsuppported and will be ignored.')
        if not ask_user('Do you want continue?'):
            exit(1)

    return output_configs


def parse_config_file(config_file):
    f = open(config_file, 'r')
    configs = json.load(f)
    f.close()

    good_configs = _validate_configs(configs, CONFIG_SCHEMAS)

    return good_configs