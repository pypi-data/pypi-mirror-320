# Py-Graph-Imputation-MLO

## Overview

`py-graph-imputation-MLO` is a Python package for graph-based imputation of missing data in genetic datasets. It leverages the `py-graph-imputation` library and provides additional functionality for filtering and processing imputed results.

## Installation

To install the package, use the following command:

```bash
pip install py-graph-imputation-MLO
```

## Dependencies

The package requires the following dependencies:

- `py-graph-imputation`
- `cython == 0.29.32`
- `numpy >= 1.20.2`
- `pandas`
- `tqdm`

These dependencies will be installed automatically when you install the package.

## Usage

### Running the Imputation

To run the imputation process, use the `RunGrim.py` script. You can configure the process using a JSON configuration file. Here is an example of how to run the script:

```bash
python src/py-graph-imputation-MLO/RunGrim.py
```

### Configuration

The configuration file should be in JSON format and include the following fields:

- `freq_file`: Path to the frequency file.
- `imputation_in_file`: Path to the input file for imputation.
- `imputation_out_path`: Path to the output directory for imputation results.
- `imputation_out_hap_freq_filename`: Filename for the haplotype frequency output.
- `imputation_out_umug_freq_filename`: Filename for the UMUG frequency output.
- `imputation_out_umug_pops_filename`: Filename for the UMUG populations output.
- `imputation_out_hap_pops_filename`: Filename for the haplotype populations output.
- `imputation_out_miss_filename`: Filename for the missing data output.
- `output_MUUG`: Boolean flag to enable/disable MUUG output.
- `output_haplotypes`: Boolean flag to enable/disable haplotype output.
- `number_of_results`: Number of results to output.
- `number_of_pop_results`: Number of population results to output.

### Example Configuration

Here is an example of a minimal configuration file:

```json
{
  "freq_file": "path/to/frequency/file",
  "imputation_in_file": "path/to/input/file",
  "imputation_out_path": "path/to/output/directory",
  "imputation_out_hap_freq_filename": "hap_freq.csv",
  "imputation_out_umug_freq_filename": "umug_freq.csv",
  "imputation_out_umug_pops_filename": "umug_pops.csv",
  "imputation_out_hap_pops_filename": "hap_pops.csv",
  "imputation_out_miss_filename": "miss.csv",
  "output_MUUG": true,
  "output_haplotypes": true,
  "number_of_results": 10,
  "number_of_pop_results": 5
}
```

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Contact

For any questions or inquiries, please contact Regev Yehezkel Imra at regevel2006@gmail.com.