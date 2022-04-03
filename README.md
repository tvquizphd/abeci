# abeci 

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

Use `tee` to write output of `python -u pangrams.py` to a logfile, like this:

```
python -u pangrams.py | tee 2022-04-01T1700.log
```

## Gotchas

- If needed, find where `google_ngram_downloader` is installed, and change the URL prefix to use https.
