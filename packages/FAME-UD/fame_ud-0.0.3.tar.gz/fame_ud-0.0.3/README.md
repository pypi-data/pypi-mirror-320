![Documentation Status](https://readthedocs.org/projects/fame-ud/badge/?version=latest)
[![PyPI version](https://img.shields.io/badge/TestPyPI-0.0.3-blue)](https://test.pypi.org/project/FAME-UD/)

## Development Instructions: [here](docs/developerReadme/development.md) &  Documentation: [here](https://fame-ud.readthedocs.io/en/latest/)

## Overview
FAME is a simulation tool designed to model the laser powder bed fusion (LPBF) additive manufacturing process using the Finite Volume Method (FVM). This tool helps in understanding the thermal and mechanical behavior of materials during the LPBF process.

## Features
- **Thermal Simulation**: Models the heat distribution and cooling rates.
- **Mechanical Simulation**: Analyzes stress and deformation.
- **Material Properties**: Supports various materials with customizable properties.
- **User-Friendly Interface**: Easy to set up and run simulations.

## Installation
To install FAME you need to have anaconda installed then clone the repository and install the required dependencies:
```bash
git clone https://github.com/neoceph/FAME.git
cd FAME
conda env create -f environment.yaml
```

## Usage
To run a simulation, use the following command:
```bash
python fame.py --config your_config_file.json
```
Replace `your_config_file.json` with your specific configuration file.

## Configuration
The configuration file should include parameters such as:
- Laser power
- Scan speed
- Layer thickness
- Material properties

Example configuration:
```json
{
    "laser_power": 200,
    "scan_speed": 1000,
    "layer_thickness": 0.03,
    "material": "Ti-6Al-4V"
}
```

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request.

## License
This project is licensed under the MIT License.

## Contact
For any questions or issues, please contact aamin1@udayton.edu.
