# RISC-V Vector Development Suite

A set of tools for developing RISC-V Vector IP includes Random Test Generator (RTG), Assembler, and Simulator.

## Supported features

### List of instructions

#### Vector

- **v_arith/v_addsub**
    - `vadd.vv`, `vadd.vx`, `vadd.vi`  
    - `vsub.vv`, `vsub.vx`  
    - `vrsub.vx`, `vrsub.vi`  

- **v_arith/v_bitwise**
    - `vand.vv`, `vand.vx`, `vand.vi`  
    - `vor.vv`, `vor.vx`, `vor.vi`  
    - `vxor.vv`, `vxor.vx`, `vxor.vi`  

- **v_arith/v_shift**
    - `vsll.vv`, `vsll.vx`, `vsll.vi`  
    - `vsrl.vv`, `vsrl.vx`, `vsrl.vi`  
    - `vsra.vv`, `vsra.vx`, `vsra.vi`  

- **v_arith/v_compare**
    - `vmseq.vv`, `vmseq.vx`, `vmseq.vi`  
    - `vmsne.vv`, `vmsne.vx`, `vmsne.vi`  
    - `vmsltu.vv`, `vmsltu.vx`  
    - `vmslt.vv`, `vmslt.vx`  
    - `vmsleu.vv`, `vmsleu.vx`, `vmsleu.vi`  
    - `vmsle.vv`, `vmsle.vx`, `vmsle.vi`  
    - `vmsgtu.vx`, `vmsgtu.vi`  
    - `vmsgt.vx`, `vmsgt.vi`  

- **v_arith/v_minmax**
    - `vminu.vv`, `vminu.vx`  
    - `vmin.vv`, `vmin.vx`  
    - `vmaxu.vv`, `vmaxu.vx`  
    - `vmax.vv`, `vmax.vx`  

- **v_arith/v_mergemv**
    - `vmerge.vvm`, `vmerge.vxm`, `vmerge.vim`  
    - `vmv.v.v`, `vmv.v.x`, `vmv.v.i`  

- **v_load**
    - `vle8.v`, `vle16.v`, `vle32.v`  
    - `vlse8.v`, `vlse16.v`, `vlse32.v`  
    - `vluxei8.v`, `vluxei16.v`, `vluxei32.v`  

- **v_store**
    - `vse8.v`, `vse16.v`, `vse32.v`  
    - `vsse8.v`, `vsse16.v`, `vsse32.v`  
    - `vsuxei8.v`, `vsuxei16.v`, `vsuxei32.v`  

#### Scalar

- `lui`
- `addi`

### Immediate types

- `.byte`
- `.half`
- `.word`

### Relocation Functions

- `%hi()`
- `%lo()`

## Configurations

Configurations are the constraints that you want the generated tests (assembly code) to meet.

- `num_of_tests`: *Required*
    - Specifies the number of tests to be generated. The value *must be an integer* and *cannot be less than 1*.

- `test_prefix`: *Optional*
    - Defines a prefix for the test names. Default: `test`.

- `num_of_insts`: *Required*
    - Indicates the number of instructions to be used in the test (only main section is counted, expect change vector masking instructions). The value *must be an integer*, *must be at least 10* and must equal `v_arith` + `v_load` + `v_store`.

- `v_arith`: *Optional*
    - Specifies the vector arithmetic operation variant. The value `must be an integer`. Default: 14.

- `v_load`: *Optional*
    - Specifies the vector load operation variant. The value `must be an integer`. Default: 3.

- `v_store`: *Optional*
    - Specifies the vector store operation variant. The value `must be an integer`. Default: 3.

- `v_reg_reuse_rate`: *Optional*
    - Indicates the rate of vector register reuse. The value is a float between `0.0` and `1.0`. Recommend: `0.1` to `0.4`. Default: `0.3`.

- `x_reg_reuse_rate`: *Optional*
    - Indicates the rate of scalar register reuse. The value is a float between `0.0` and `1.0`. Recommend: `0.05` to `0.3`. Default: `0.1`.

- `data_type_weights`: *Optional*
    - Specifies the weights for different data types: `.byte`, `.half`, and `.word`. The value is a list of three numbers (integers or floats). Default: `[1, 1, 1]`.

- `data_variant_weights`: *Optional*
    - Defines the weights for different data variants: zero, negative, positive, and big numbers. The value is a list of four numbers (integers or floats). Default: `[1, 3, 3, 3]`.

- `vector_masking`: *Optional*
    - Indicates whether vector masking is enabled. `vector_masking` is `True`: unmasked, else can be unmasked or controlled by `v0.mask`. Default: `False`.

- `vector_masking_change_rate`: *Optional*
    - Specifies the rate of change for vector masking when `vector_masking` is `False`. The value is a float between `0.0` and `1.0`. Recommend: `0.05` to `0.3`. Default: `0.2`.

- `dmem_size`: *Required*
    - Specifies the size of the data memory in bytes. The value must be an integer and must be at least 4096 bytes (1024 words), which is a multiple of 4.

- `dmem_access_range_start`: *Optional*
    - Defines the starting address for the data memory access range. The value must be an integer. Default: `0`.

- `dmem_access_range_end`: *Optional*
    - Defines the ending address for the data memory access range. The value must be an integer. Default: `dmem_size`.

- `rtg.mutate_rate`: *Optional*
    - Specifies the mutation rate for the evolutionary algorithm. The value is a float between `0.0` and `1.0`. Recommend: `0.05` to `0.2`. Default: `0.1`.

- `rtg.population_size`: *Optional*
    - Defines the population size for the evolutionary algorithm. The value must be an integer. Recommend: `5` to `20`. Default: `10`.

Example of `configs.json` file:

```json
{
  "num_of_tests": 20,
  "num_of_insts": 20,
  "test_prefix": "test_",
  "v_arith": 14,
  "v_load": 3,
  "v_store": 3,
  "v_reg_reuse_rate": 0.3,
  "x_reg_reuse_rate": 0.1,
  "vector_masking": false,
  "vector_masking_change_rate": 0.2,
  "data_type_weights": [ 1, 1, 1 ],
  "data_variant_weights": [ 1, 3, 3, 3 ],
  "dmem_size": 4096,
  "dmem_access_range_start": 2048,
  "rtg": {
    "mutate_rate": 0.1,
    "population_size": 10
  }
}
```

## APIs

### Generator

`rvvsuite.generator`

#### `rvvsuite.generator.parse_config_file()`

#### `rvvsuite.generator.generate()`

#### `rvvsuite.generator.display()`

#### `rvvsuite.generator.generate_operator_sequence()`

#### `rvvsuite.generator.add_operands()`

#### `rvvsuite.generator.insert_vm_change_placeholders()`

#### `rvvsuite.generator.replace_vm_change_placeholders()`

#### `rvvsuite.generator.trace_uninitialzed_operands()`

#### `rvvsuite.generator.init_data()`

### Assembler

`rvvsuite.assembler`

#### `rvvsuite.assembler.sectionify()`

#### `rvvsuite.assembler.parse_data()`

#### `rvvsuite.assembler.parse_text()`

#### `rvvsuite.assembler.translate_data()`

#### `rvvsuite.assembler.translate_text()`

### Simulator

`rvvsuite.simulator`

#### Constructor: `rvvsuite.simulator()`

- **Parameters**
    - `imem` *(dict[int, int])*: The Instruction Memory (IMEM), represented as a dictionary.
        - Key: `pc_addr` (Program Counter address, integer).
        - Value: 32-bit `inst` (instruction, integer).
    
    - `dmem` *(dict[int, int])*: The Data Memory (DMEM), represented as a dictionary.
        - Key: `byte_addr` (Byte address, integer).
        - Value: 8-bit `data` (data value, integer).
    
    - `configs` *(dict)*: A dictionary containing the configuration of the RISC-V system.
    ```python
    DEFAULT_CONFIGS = {
        'pc_width': 10,     # IMEM_SIZE = 2 ** 10 = 1024 bytes = 265 32-bit instructions
        'addr_width': 12,   # DMEM_SIZE = 2 ** 12 = 4028 bytes
        'elen': 32,         # Width of an element in vector register (32 bits)
        'vlen': 128,        # Width of a vector register (128 bits - 4 elements)
        'xlen': 32          # Width of a scalar register (32 bits)
    }
    ```
    
    - `debug_mode` *(bool)*: A control flag for enabling debug mode.
        - Default: `False`.
        - When `True`, enables the generation of debugging messages for tracing execution.
    
    - `log` *(str)*: The file path where debugging messages will be stored.
        - If not provided, messages will be written to the terminal.

#### `rvvsuite.simulator.run()`

- **Parameters**
    - No

- **Returns**
    - `changelog` *(list[dict])*: A list of dictionaries capturing the state after each instruction execution, including changes to **PC**, **DMEM**, **VRegFile**, and **XRegFile**.

    - `stat` *(dict)*: Statistics for coverage calculation, including counts for instructions, registers, vector, immediate, ...


## Changelog

### Version 0.0.8 (by [Nguyen Binh Khiem](https://github.com/khiemnb153))

- **[Added]** `Simulator` Added a feature to generate statistics on the used instructions, registers, and vectors.

### Version 0.0.7 (by [Nguyen Binh Khiem](https://github.com/khiemnb153))

- **[Fixed]** `Simulator` Fixed `sra` operation.
- **[Fixed]** `Simulator` Fixed unsigned operations.
- **[Fixed]** `Simulator` Fixed vector initialization mismatch width.

### Version 0.0.6 (by [Nguyen Binh Khiem](https://github.com/khiemnb153))

- **[Added]** `Simulator` Enabled write debug log to file.
- **[Fixed]** `Simulator` Fixed `vmsgt` operation.
- **[Fixed]** `Simulator` Fixed `vsrub` operation.

### Version 0.0.5 (by [Nguyen Binh Khiem](https://github.com/khiemnb153))

- **[Fixed]** `Simulator` Fixed vector load operations.

### Version 0.0.4 (by [Nguyen Binh Khiem](https://github.com/khiemnb153))

- **[Changed]** `Simulator` Modified how PC is logged.
- **[Changed]** `Simulator` Added debug mode.
- **[Fixed]** `Simulator` Fixed vector store operations.

### Version 0.0.3 (by [Nguyen Binh Khiem](https://github.com/khiemnb153))

- **[Changed]** `Simulator` Ignored out-of-width address bits in vector load and store instructions in simulator.

### Version 0.0.2 (by [Nguyen Binh Khiem](https://github.com/khiemnb153))

- **[Fixed]** `Simulator` Fixed SRA opeator of ICB

### Version 0.0.1 (by [Nguyen Binh Khiem](https://github.com/khiemnb153))

- **[Added]** Initial version
