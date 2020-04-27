# getBooks

An script to download the list of free ebooks released by Springer during the quarantine period.

## Get The Source

```bash
git clone https://github.com/diegofps/getBooks.git
```

## Install Dependencies

```bash
pip3 install lxml bs4
```

## Usage

```bash
# Download using 8 parallel connections
./getBooks.py

# Download using a different number of parallel connections
./getBooks.py 2
```
