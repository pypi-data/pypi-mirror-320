# SmoothText

SmoothText is a Python library that aims to provide an easy-to-use interface to calculate readability statistics of
texts in multiple languages and multiple formulas.

This library aims to ensure accuracy through a unified interface. Thus, further formula or feature implementations shall
be available for all languages without breaking the existing use style.

## External Dependencies

|                     Library                      |  Version  |   License    | Notes                                                                  |
|:------------------------------------------------:|:---------:|:------------:|------------------------------------------------------------------------|
| [Unidecode](https://pypi.org/project/Unidecode/) | `>=1.3.8` | `GNU GPL-2`  | Required.                                                              |
|          [NLTK](https://www.nltk.org/)           | `>=3.9.1` | `Apache 2.0` | Optional, but temporarily Required until other backends are supported. |

## Supported Languages and Formulas

| Formula/Language                                                                                                                                                                                                                                                    | English | Turkish |
|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-------:|:-------:|
| Flesch Reading Ease                                                                                                                                                                                                                                                 |    ✔    |    ❌    |
| Flesch-Kincaid Grade                                                                                                                                                                                                                                                |    ✔    |    ❌    |
| [Ateşman](https://scholar.google.com/scholar?as_sdt=0%2C5&q=T%C3%BCrk%C3%A7ede+Okunabilirli%C4%9Fin+%C3%96l%C3%A7%C3%BClmesi+Ate%C5%9Fman&btnG=)                                                                                                                    |    ❌    |    ✔    |
| [Bezirci-Yılmaz](https://scholar.google.com/scholar?as_sdt=0%2C5&q=Metinlerin+okunabilirli%C4%9Finin+%C3%B6l%C3%A7%C3%BClmesi+%C3%BCzerine+bir+yazilim+k%C3%BCt%C3%BCphanesi+ve+T%C3%BCrk%C3%A7e+i%C3%A7in+yeni+bir+okunabilirlik+%C3%B6l%C3%A7%C3%BCt%C3%BC&btnG=) |    ❌    |    ✔    |

**Ateşman** is the Turkish adaptation of **Flesch Reading Ease**, and **Bezirci-Yılmaz** is the Turkish adaptation of
**Flesch-Kincaid Grade**.

### `SmoothText.class` API

|         Function          | Description                                                                      |
|:-------------------------:|:---------------------------------------------------------------------------------|
|          `setup`          | Configures the class and its dependencies.                                       |
|      `set_language`       | Changes instance language.                                                       |
|   `compute_readability`   | Computes the readability score of the provided text using the specified formula. |
|       `sentencize`        | Breaks down the `text` into sentences.                                           |
|        `tokenize`         | Breaks down the `text` into tokens.                                              |
| `sentencize_and_tokenize` | Breaks down the `text` into sentences and tokens.                                |
|        `syllabify`        | Breaks down the `token` into syllables.                                          |

## Usage

### Initializing the Library

The library must be initialized before creating any instances.

```python
from src.smoothtext import SmoothText

SmoothText.setup(languages='en,tr', backend='nltk')
```

Now, we are ready to create an instance.

```python
from src.smoothtext import SmoothText

st = SmoothText()
```

### Switching Languages

If multiple languages are listed when the library was set, the instances can switch between those languages.

```python
from src.smoothtext import Language, SmoothText

st = SmoothText(Language.Turkish)
st.set_language(Language.English)
```

### Computing the Readability Statistics

```python
from src.smoothtext import Language, ReadabilityFormula, SmoothText

# https://en.wikipedia.org/wiki/Forrest_Gump
text = "Forrest Gump is a 1994 American comedy-drama film directed by Robert Zemeckis."

st = SmoothText(Language.English)

s1 = st.compute_readability(text=text, formula=ReadabilityFormula.Flesch_Reading_Ease)
s2 = st.compute_readability(text=text, formula=ReadabilityFormula.Flesch_Kincaid_Grade)
print(s1, s2)

# Output is: 25.455000000000013 12.690000000000001
```
