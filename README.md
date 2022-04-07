# abeci 

Create [perfect pangrams][pp], sentences with exactly one of each letter in the English alphabet.

[pp]: https://en.wikipedia.org/wiki/Pangram#Perfect_pangrams

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

## Generate Pangrams

For help, run `python src/pangrams.py -h`

```
python src/pangrams.py
```

## Build


Update setuptools in conda environemnt

```
python3 -m pip install --user --upgrade setuptools wheel 
```

```
Install conda-build
conda config --add channels conda-forge
```

```
conda install conda-build
```


```
conda build .
```

## Test

```
bash run_test.sh
```

## Publish

- [Publish to pip](https://levelup.gitconnected.com/turn-your-python-code-into-a-pip-package-in-minutes-433ae669657f)
- [Publish to conda](https://levelup.gitconnected.com/publishing-your-python-package-on-conda-and-conda-forge-309a405740cf)

## Gotchas

- If needed, find where `google_ngram_downloader` is installed, and change the URL prefix to use https.
