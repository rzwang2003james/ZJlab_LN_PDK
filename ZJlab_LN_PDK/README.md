## 🔬 ZJlab_LN_PDK

ZJlab Lithium-Niobate Photonics Design Kit (PDK) for layout design, simulation, and tapeout.  
This PDK provides parameterized device cells (PCells), technology definitions, and utilities for integration with layout tools such as **PHIDL**.

---

## 📁 Repository Structure

```
ZJlab_LN_PDK/
├── zjlab_ln/          # Main PDK Python package
│   ├── __init__.py
│   ├── active/         # Parameterized device cells
│   ├── passive/          # Technology and process definitions
│   └── layers/        # Layer mapping and utilities
├── environment.yml    # Conda environment specification
├── pyproject.toml     # Python package metadata
├── test.py            # Test PDK Installation
└── README.md          # This file
```

---



## ⚙️ Installation

### 1. Create the Conda environment
```bash
conda env create -f environment.yml
```
### 2. Activate the Conda environment
In your working directory: 
```bash
conda activate ZJlab_LN_PDK
```
### 3. Testing Installation of PDK
In the directory where the conda environment is activated, copy test.py to the directory
```bash
python test.py
```
Check the generated gds file



## 🧱 Requirements

- **Python** ≥ 3.8 (tested up to 3.11)
- **Conda** for environment management  
- Dependencies:
  - [PHIDL](https://github.com/amccaugh/phidl)
  - [NumPy](https://numpy.org/)
  - [SciPy](https://scipy.org/)
  - [KLayout](https://www.klayout.de/)
  - [Gdstk](https://pypi.org/project/gdstk/)

---