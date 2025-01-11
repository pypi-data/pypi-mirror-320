# RISC-V Vector Development Suite

A set of tools for developing RISC-V Vector IP includes Random Test Generator (RTG), Assembler, and Simulator.

> **This project is not yet complete**.
>
> However, since my teammate needs it for testing the RTL design, I have decided to publish it anyway.
> This package is tested on product environment. LMAO.

## Supported features

## Configurations

## APIs

## Changelog

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
