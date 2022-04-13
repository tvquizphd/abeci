# abeci 

Create [perfect pangrams][pp], sentences with exactly one of each letter in the English alphabet.

[pp]: https://en.wikipedia.org/wiki/Pangram#Perfect_pangrams

## Generate Pangrams

After installing locally or with pip/conda, you can run:

```
abeci-pangrams
```

This script makes a text file with this name, in `results` by default:

```
./results/std4_max1_has_2x_3x/pangrams_1024_0x1_128x2_512x3_1024x4.txt
```

It also generates additional files in an `effects` directory.

If the `effects/source.p` file is missing,
  - The script uses Google's English Corpus of all books published in 2008.
  - The script will wiret an `effects/source.p` to speed up future calls to the script.

it also writes a log file such as `2022-04-07T0200.log`.
The file is named after the current date and UTC time.

Run the help command for options: `abeci-pangrams -h`


## API Usage

- No programatic api is documented at this time:
- Look to `src/modules/savePangrams.py` for inspiration


# Local Installation

## Dependencies

Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or Anaconda.

```
conda env create -f environment.yaml
```
or 
```
conda env update -f environment.yaml
```

Then, activate the installed environment:

```
conda activate abeci
```

## Install Locally w/ pip

After activating the conda environment, install locally with pip

```
VIRTUAL_ENV=$CONDA_PREFIX pip install --src $VIRTUAL_ENV/src -e .
```

## Install Locally w/ conda

Update setuptools in conda environemnt

```
python3 -m pip install --user --upgrade setuptools wheel 
```

Install conda-build

```
conda config --add channels conda-forge
```

```
conda install conda-build
```

```
conda build .
```

## Test

After installing locally, run:

```
bash run_test.sh
```

## Publish

Publishing happens on release. The following two links were inspirations:

- [Publish to pip](https://levelup.gitconnected.com/turn-your-python-code-into-a-pip-package-in-minutes-433ae669657f)
- [Publish to conda](https://levelup.gitconnected.com/publishing-your-python-package-on-conda-and-conda-forge-309a405740cf)

## Gotchas

- If needed, find where `google_ngram_downloader` is installed, and change the URL prefix to use https.
