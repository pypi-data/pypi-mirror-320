# pvtlib

`pvtlib` is a Python library that provides various tools in the categories of thermodynamics, fluid mechanics, and metering. The library includes functions for calculating flow rates, energy balances, and other related calculations.

## Installation

You can install the library using `pip`:

```sh
pip install pvtlib
```

## Usage

Here is an example of how to use the library:

```py
from pvtlib import metering

# Example usage of the calculate_flow_venturi function
result = metering.calculate_flow_venturi(D=0.1, d=0.05, dP=200, rho1=1000)
print(result)
```

## Features

- **Thermodynamics**: Thermodynamic functions
- **Fluid Mechanics**: Fluid mechanic functions
- **Metering**: Metering functions

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please read the [contributing guidelines](CONTRIBUTING.md) for more details.

## Contact

For any questions or suggestions, feel free to open an issue or contact the author at chaagen2013@gmail.com.