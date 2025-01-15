# ELFEN - Efficient Linguistic Feature Extraction for Natural Language Datasets

This python package provides efficient linguistic feature extraction for text datasets (i.e. datasets with N text instances, in a tabular structure). 

For a full overview of the features available, check the [overview table](features.md), for further details and tutorials check the
[Documentation (TODO)]()


## Installation
Install this package using pip
```bash
python -m pip install elfen
```
Install this package using conda (NOT SUPPORTED YET)
```bash
conda install -c conda-forge elfen
```

Install this package from source 
```bash
python -m pip install git+https://github.com/mmmaurer/elfen.git
```

If you want to use the spacy backbone, download the respective model, e.g. "en_core_web_sm":
```bash
python -m spacy download en_core_web_sm
```

To use transformer models with the spacy backbone, you will additionally need to install ``spacy_transformers``:
```bash
python -m pip insall spacy_transformers
python -m spacy download en_core_web_trf  # for the English transformer model
```

To use wordnet features, download open multilingual wordnet using:
```bash
python -m wn download omw:1.4
```

## Usage of third-party resources usable in this package
Please refer to the original author's licenses and conditions for usage, and cite them if you use the resources through this package in your analyses.

## Acknowledgements

While all feature extraction functions in this package are written from scratch, the choice of features in the readability and lexical richness feature areas (partially) follows the [`readability`](https://github.com/andreasvc/readability) and [`lexicalrichness`](https://github.com/LSYS/LexicalRichness) python packages.

## Citation
If you use this package in your work, for now, please cite
```bibtex
@misc{maurer-2024-elfen,
  author = {Maurer, Maximilian},
  title = {ELFEN - Efficient Linguistic Feature Extraction for Natural Language Datasets},
  year = {2024},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/mmmaurer/elfen}},
}
```