# PDBSpider
Crawling for chain information on Protein Data Bank website.

## Requirement
- beautifulsoup4==4.11.2
- bs4==0.0.1
- certifi @ file:///croot/certifi_1671487769961/work/certifi
- numpy==1.24.2
- pandas==1.5.3
- python-dateutil==2.8.2
- pytz==2022.7.1
- six==1.16.0
- soupsieve==2.4
- tqdm==4.65.0

## Installation
```bash
pip install -r requirement.txt
```

## Usage

It is very easy to run this project. The only mandatory input is `--input_path`, which is a file with each PDB id in one line. Here is an demo you can follow.

```bash
# python main.py [-h] [--input_path INPUT_PATH] [--output_path OUTPUT_PATH]
python main.py --input_path ./input_demo.txt
```

options:

  - `-h, --help`            show this help message and exit

  - `--input_path` INPUT_PATH: list for pdb id, one for each line.

  - `--output_path` OUTPUT_PATH: output file. If None, input file path suffixed with ".out" will be used.

