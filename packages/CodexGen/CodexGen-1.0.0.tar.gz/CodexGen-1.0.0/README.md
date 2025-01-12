<p align="center">
  <img src="icon.png" alt="CodexGen Icon" width="300" height="300" style="object-fit: cover;">
</p>

# CodexGen

CodexGen is a Python library that allows you to convert digital data into DNA sequences and vice versa. It provides functionality to encode any data into a DNA sequence, which can then be decoded back to its original form. The library supports various types of data, including strings, booleans, dictionaries, and files.

## Features
- Convert digital data (e.g., strings, dictionaries, files) into DNA sequences.
- Decode DNA sequences back to their original data format.
- Save and load files in DNA sequence format.
- Etc.

## Installation

To install CodexGen, you can use pip:

```bash
pip install CodexGen
```

Alternatively, you can clone the repository and install it locally:

```bash
git clone https://github.com/Arifmaulanaazis/CodexGen.git
cd CodexGen
python setup.py install
```

## Usage

### Convert data to DNA sequence

You can convert any data to a DNA sequence using the `CodexGen` class:

```python
from codexgen import CodexGen

# Initialize CodexGen instance
codexgen = CodexGen()

# Data to be converted
data = {"name": "Alice", "age": 30}

# Convert data to DNA sequence
dna_sequence = codexgen.to_dna(data)

print("DNA Sequence:", dna_sequence)
```

### Decode a DNA sequence back to the original data

You can decode a DNA sequence back to the original data:

```python
# Decode the DNA sequence
decoded_data = codexgen.to_binary(dna_sequence)

print("Decoded Data:", decoded_data)
```

### Working with files

You can load and save files as DNA sequences using the `load_file`:

```python
from codexgen import CodexGen

# Initialize CodexGen instance
codexgen = CodexGen()

# Convert file content to DNA sequence
file_content = codexgen.load_file("example.txt")
dna_sequence = codexgen.to_dna(file_content)

# Save DNA sequence to file
codexgen.save_file(dna_sequence, 'output.txt')
```

## Running Tests

To run the tests for CodexGen, you can use `TestCodexGen`:

```python
from codexgen import TestCodexCore, TestCodexUtils, TestCodexTransformer

# Run tests for CodexCore
test_core = TestCodexCore()
test_core.run_tests()

# Run tests for CodexUtils
test_utils = TestCodexUtils()
test_utils.run_tests()

# Run tests for CodexTransformer
test_transformer = TestCodexTransformer()
test_transformer.run_tests()

print("All tests completed.")
```

## License

This library is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for more details.
