# Ramonak

[![PyPI - Version](https://img.shields.io/pypi/v/ramonak.svg)](https://pypi.org/project/ramonak)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ramonak.svg)](https://pypi.org/project/ramonak)

Універсальная бібліятэка па працы з тэкстам на беларускай мове для Python.

## Як усталяваць?

Напішыце ў вашым тэрмінале:

```sh
pip install ramonak
```

Або ў Google Colab:

```sh
!pip install ramonak
```

## Як карыстацца?

```python
!pip install ramonak -U

import ramonak
from ramonak.tokenizer import word_tokenize
from ramonak.stemmer import FlexionStatStemmer
from ramonak.stopwords import clean_stop_words


text = "Яны iшлi ўдвух выкатанаю нячутна-пругкiмi веласiпедамi сцежкаю ля шэрых нямогла нахiленых да вулiцы платоў".lower()
tokens = word_tokenize(text, remove_punct=True)
tokens = clean_stop_words(tokens)

stemmer = FlexionStatStemmer()
print(
      stemmer.stem_words(tokens)
    )
```

## Дарожная карта

 - [x] Такенізацыя па словам
 - [x] Такенізацыя сказаў
 - [x] Спісак стоп-слоў
 - [x] Просты стэмер, заснаваны на статыстыцы флексій
 - [x] Менеджар пакетаў з дадзенымі
 - [ ] Стэмер Портэра
 - [ ] Леммацізатар
 - [ ] Марфалагічны аналізатар
