#  SmoothText - https://smoothtext.tugrulgungor.me/
#
#  Copyright (c) 2025 - present. All rights reserved.
#  Tuğrul Güngör - https://tugrulgungor.me
#
#  Distributed under the MIT License.
#  https://opensource.org/license/mit/

# # # # # # # # #
# Dependencies  #
# # # # # # # # #
from enum import Enum
import importlib
import logging
import math
import os

import unidecode


# # # # # # #
# Language  #
# # # # # # #
class Language(Enum):
    """
    Languages supported by SmoothText.
    """

    English = 'English'
    Turkish = 'Turkish'

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def values() -> list:
        return [Language.English, Language.Turkish]


def _get_lang_(lang: any) -> Language:
    if isinstance(lang, Language):
        return lang

    if not isinstance(lang, str):
        raise TypeError(f'Language must be str: {lang}')

    lang = lang.lower()

    if lang == 'en' or lang == 'eng' or lang == Language.English.value.lower():
        return Language.English

    elif lang == 'tr' or lang == 'tur' or lang == Language.Turkish.value.lower():
        return Language.Turkish

    raise ValueError(f'Invalid language: {lang}')


# # # # # # # # # # # #
# Readability Formula #
# # # # # # # # # # # #
class ReadabilityFormula(Enum):
    """
    Readability formulas supported by SmoothText.
    """

    Atesman = 'Atesman'
    Bezirci_Yilmaz = 'Bezirci-Yilmaz'
    Flesch_Reading_Ease = 'Flesch Reading Ease'
    Flesch_Kincaid_Grade = 'Flesch-Kincaid Grade'


# Turkish
# # # # # #
_CONSONANTS_TUR_ = 'bcçdfgğhjklmnprsştvyzxqwBCÇDFGĞHJKLMNPRSŞTVYZXQW'
_VOWELS_TUR_ = 'aeıioöuüAEIİOÖUÜ'


def _is_vowel_tur_(c: str) -> bool:
    return c in _VOWELS_TUR_


def _is_consonant_tur_(c: str) -> bool:
    return c in _CONSONANTS_TUR_


def _count_consonants_and_vowels_tur_(token: str) -> tuple[int, int, int]:
    num_consonants: int = 0
    num_vowels: int = 0
    num_others: int = 0

    for c in token:
        if _is_consonant_tur_(c):
            num_consonants += 1
        elif _is_vowel_tur_(c):
            num_vowels += 1
        else:
            num_others += 1

    return num_consonants, num_vowels, num_others


def _count_words_and_syllables_tur_(tokens: list[str]) -> tuple[int, int, dict[int, int]]:
    num_words: int = 0
    num_syllables: int = 0
    syllable_frequencies: dict[int, int] = {}

    for token in tokens:
        num_consonants, num_vowels, num_others = _count_consonants_and_vowels_tur_(token)
        if 0 == num_consonants and 0 == num_vowels:
            continue

        num_token_syllables = max(num_vowels, 1)
        if num_token_syllables not in syllable_frequencies:
            syllable_frequencies[num_token_syllables] = 1
        else:
            syllable_frequencies[num_token_syllables] += 1

        num_syllables += num_token_syllables
        num_words += 1

    return num_words, num_syllables, syllable_frequencies


def _compute_readability_tur_atesman_(sentences: list[list[str]]) -> float:
    total_words: int = 0
    total_syllables: int = 0
    total_sentences: int = 0

    for sentence in sentences:
        num_words, num_syllables, _ = _count_words_and_syllables_tur_(sentence)

        if 0 == num_words:
            continue

        total_words += num_words
        total_syllables += num_syllables
        total_sentences += 1

    x1: float = float(total_syllables) / float(total_words)
    x2: float = float(total_words) / float(total_sentences)

    return 198.825 - (40.175 * x1) - (2.610 * x2)


def _compute_readability_tur_bezirci_yilmaz_(sentences: list[list[str]]) -> float:
    sentence_word_counts: list[int] = []
    sentence_syllable_frequencies: list[dict[int, int]] = []
    num_sentences: int = 0

    for sentence in sentences:
        num_words, num_syllables, syllable_frequency = _count_words_and_syllables_tur_(sentence)

        if 0 == num_words:
            continue

        frequencies: dict[int, int] = {
            3: 0,
            4: 0,
            5: 0,
            6: 0
        }

        for k, v in syllable_frequency.items():
            if 6 <= k:
                frequencies[6] += v
            elif 3 <= k:
                frequencies[k] += v

        sentence_syllable_frequencies.append(frequencies)
        sentence_word_counts.append(num_words)

        num_sentences += 1

    h3: float = 0.0
    h4: float = 0.0
    h5: float = 0.0
    h6: float = 0.0

    for syllable_frequency in sentence_syllable_frequencies:
        h3 += float(syllable_frequency[3])
        h4 += float(syllable_frequency[4])
        h5 += float(syllable_frequency[5])
        h6 += float(syllable_frequency[6])

    h3 = h3 / float(num_sentences)
    h4 = h4 / float(num_sentences)
    h5 = h5 / float(num_sentences)
    h6 = h6 / float(num_sentences)

    score: float = 0.0

    score += h3 * 0.84
    score += h4 * 1.5
    score += h5 * 3.5
    score += h6 * 26.25

    awc = float(sum(sentence_word_counts)) / float(num_sentences)
    return math.sqrt(awc * score)


def _syllabify_tur_(tokens: list[str]) -> list[str] | list[list[str]]:
    syllables: list[list[str]] = []

    for token in tokens:
        if 0 == len(token):
            continue

        token_syllables: list[str] = []

        tok = unidecode(token)

        previous: int = len(tok)
        index: int = len(tok) - 1
        while index >= 0:
            c = tok[index]

            if _is_vowel_tur_(c):
                if 0 == index:
                    token_syllables.append(token[0:previous])
                    previous = 0
                    break

                c2 = tok[index - 1]
                if _is_consonant_tur_(c2):
                    index -= 1

                token_syllables.append(token[index:previous])
                previous = index

            index -= 1

        if 0 != previous:
            token_syllables.append(token[0:previous])

        if 0 != len(token_syllables):
            token_syllables.reverse()
            syllables.append(token_syllables)

    if 1 == len(syllables):
        return syllables[0]

    return syllables


# English
# # # # # #
_CONSONANTS_ENG_ = 'bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ'
_VOWELS_ENG_ = 'aeiouAEIOU'
_DIGITS_ENG_ = '0123456789'


def _is_valid_word_eng_(word: str) -> bool:
    if 0 == len(word):
        return False

    for c in word:
        if c in _CONSONANTS_ENG_ or c in _VOWELS_ENG_ or c in _DIGITS_ENG_:
            return True

    return False


def _syllabify_eng_(tokens: list[str], tokenizer: any) -> list[str] | list[list[str]]:
    syllables: list[list[str]] = []

    for token in tokens:
        token_syllables: list[str] = tokenizer(unidecode(token))
        syllables.append(token_syllables)

    if 1 == len(syllables):
        return syllables[0]

    return syllables


def _count_words_and_syllables_r_eng_(tokens: list[str]) -> tuple[int, int]:
    return 0, 0


def _count_words_and_syllables_eng_(tokens: list[str], tokenizer: any) -> tuple[int, int]:
    total_words, total_syllables = 0, 0

    for token in tokens:
        if not _is_valid_word_eng_(token):
            continue

        syllables: list[str] = tokenizer(unidecode(token))
        for syllable in syllables:
            if _is_valid_word_eng_(syllable):
                total_syllables += 1

        total_words += 1

    return total_words, total_syllables


def _compute_avg_sentence_length_and_syllables_per_word_eng_(sentences: list[list[str]], tokenizer: any) -> tuple[
    int, int]:
    num_sentences: int = 0
    total_words: int = 0
    total_syllables: int = 0

    for sentence in sentences:
        num_words, num_syllables = _count_words_and_syllables_eng_(sentence, tokenizer)
        if 0 == num_words:
            continue

        total_words += num_words
        total_syllables += num_syllables

        num_sentences += 1

    avg_sentence_length: float = float(total_words) / float(num_sentences)
    avg_syllables_per_word = float(total_syllables) / float(total_words)
    return avg_sentence_length, avg_syllables_per_word


def _compute_readability_eng_flesch_reading_ease_(sentences: list[list[str]], tokenizer: any) -> float:
    avg_sentence_length, avg_syllables_per_word = _compute_avg_sentence_length_and_syllables_per_word_eng_(sentences,
                                                                                                           tokenizer)
    return 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)


def _compute_readability_eng_flesch_kincaid_grade_(sentences: list[list[str]], tokenizer: any) -> float:
    avg_sentence_length, avg_syllables_per_word = _compute_avg_sentence_length_and_syllables_per_word_eng_(sentences,
                                                                                                           tokenizer)
    return (0.39 * avg_sentence_length) + (11.8 * avg_syllables_per_word) - 15.59


# # # # # # # #
# SmoothText  #
# # # # # # # #
class SmoothText(object):
    @staticmethod
    def __import_nltk__() -> None:
        pass

    _languages_: list[Language] = []
    _backend_: any = None

    @staticmethod
    def test_support(language: Language | str, formula: ReadabilityFormula) -> bool:
        """
        Tells if the `formula` supports the `language`.
        :param language: Language to test.
        :param formula: Formula to test.
        :return: `True` if the `formula` supports the `language`, `False` otherwise.
        """

        if Language.English == language:
            return ReadabilityFormula.Flesch_Reading_Ease == formula or ReadabilityFormula.Flesch_Kincaid_Grade == formula

        if Language.Turkish == language:
            return ReadabilityFormula.Atesman == formula or ReadabilityFormula.Bezirci_Yilmaz == formula

        return False

    @staticmethod
    def setup(languages: None | list[str] | str | list[Language] | Language = None, backend: None | str = None,
              **kwargs) -> None:
        """
        Global setup function for the SmoothText class.
        :param languages: Language or languages to enable. This can be a single language code/name or a list of language
        codes/names (e.g., `['English', 'Turkish']`). Only the resources for the specified languages will be imported.
        If `None` or empty, all the languages are imported.
        :param backend: Backend to use. Must be one of the following: `NLTK`. If `None`, the value is imported from the
        environment variable `SMOOTHTEXT_BACKEND`.
        :param kwargs: Additional keyword arguments to pass to the backend's data downloader function.
        :return: `None`. This function does not return anything but might raise exceptions.
        """

        # Languages
        if languages is None:
            languages = Language.values()
        elif isinstance(languages, str):
            if ',' in languages:
                languages = languages.split(',')
            else:
                languages = [languages]
        elif isinstance(languages, Language):
            languages = [languages]

        for i in range(len(languages)):
            languages[i] = _get_lang_(languages[i])

        SmoothText._languages_ = languages

        # Backend
        if backend is None:
            backend = os.environ.get('SMOOTHTEXT_BACKEND')

        if isinstance(backend, str) and backend.lower() == 'NLTK'.lower():
            try:
                nltk = importlib.import_module('nltk')
                if not nltk.download('punkt_tab', **kwargs):
                    raise ImportError('Could not download NLTK data.')

                globals()['nltk'] = nltk

                SmoothText._backend_ = nltk
            except ModuleNotFoundError:
                raise ModuleNotFoundError('NLTK is not installed.')
        else:
            raise Exception(f'Backend \'{backend}\' is not supported.')

    def __init__(self, language: Language | str | None = None) -> None:
        """
        Default constructor for the SmoothText class.
        :param language: Default language to use.
        """

        if language is None:
            language = SmoothText._languages_[0]
        elif isinstance(language, str):
            language = _get_lang_(language)
        else:
            language = language

        if language not in SmoothText._languages_:
            raise ValueError(f'Invalid language: {language}. Make sure the language was included in the setup.')

        self._set_language_(language)

    def _set_language_(self, language: Language) -> None:
        self.language = language
        self.language_ = self.language.value.lower()

        if Language.English == language:
            self._syllable_tokenizer_ = nltk.tokenize.SyllableTokenizer(self.language_[0:2])
        else:
            self._syllable_tokenizer_ = None

    def set_language(self, language: Language | str) -> None:
        """
        Sets the language of the SmoothText class.
        :param language: Language to use.
        :return: `None`. This function does not return anything but might raise exceptions.
        :except: `ValueError` when the language code is invalid or not supported.
        """

        if isinstance(language, str):
            language = _get_lang_(language)

        if language not in SmoothText._languages_:
            raise ValueError(f'Invalid language: {language}. Make sure the language was included in the setup.')

        self._set_language_(language)

    def sentencize(self, text: str) -> list[str]:
        """
        Breaks down the `text` into sentences.
        :param text: Text to break down into sentences.
        :return: List of sentences.
        """

        return self._backend_.sent_tokenize(text, self.language_)

    def tokenize(self, text: str) -> list[str]:
        """
        Breaks down the `text` into tokens.
        :param text: Text to break down into tokens.
        :return: The list of tokens.
        """

        return self._backend_.word_tokenize(text, self.language_)

    def sentencize_and_tokenize(self, text: str) -> list[list[str]]:
        """
        Breaks down the `text` into sentences and tokens.
        :param text: Text to break down into sentences and tokens.
        :return: List of sentences and tokens.
        """

        result: list[list[str]] = []

        sentences: list[str] = self.sentencize(text)
        for sentence in sentences:
            result.append(self.tokenize(sentence))

        return result

    def syllabify(self, token: str) -> list[str] | list[list[str]]:
        """
        Breaks down the `token` into syllables.
        :param token: Token to syllabify.
        :return: List of syllables.
        :remark: If token is in fact a list of tokens, each is syllabified separately.
        """

        if Language.English == self.language:
            return _syllabify_eng_(self.tokenize(token), self._syllable_tokenizer_.tokenize)
        elif Language.Turkish == self.language:
            return _syllabify_tur_(self.tokenize(token))

        return [token]

    @staticmethod
    def _compute_readability_tur_(sentences: list[list[str]], formula: ReadabilityFormula) -> float:
        for s in range(len(sentences)):
            for t in range(len(sentences[s])):
                sentences[s][t] = unidecode(sentences[s][t])

        if ReadabilityFormula.Atesman == formula:
            return _compute_readability_tur_atesman_(sentences)

        if ReadabilityFormula.Bezirci_Yilmaz == formula:
            return _compute_readability_tur_bezirci_yilmaz_(sentences)

        return 0.0

    @staticmethod
    def _compute_readability_eng_(sentences: list[list[str]], formula: ReadabilityFormula, tokenizer: any) -> float:
        if ReadabilityFormula.Flesch_Reading_Ease == formula:
            return _compute_readability_eng_flesch_reading_ease_(sentences, tokenizer)

        if ReadabilityFormula.Flesch_Kincaid_Grade == formula:
            return _compute_readability_eng_flesch_kincaid_grade_(sentences, tokenizer)

        return 0.0

    def compute_readability(self, text: str, formula: ReadabilityFormula) -> float:
        """
        Computes the readability score of the `text` using `formula`.
        :param text: Text to compute the readability score of.
        :param formula: `ReadabilityFormula` to use.
        :return: Readability score.
        """

        if not SmoothText.test_support(self.language, formula):
            logging.warning(f'Readability formula \'{formula.value}\' does not work with \'{self.language}\'.')
            return 0.0

        sentences: list[list[str]] = self.sentencize_and_tokenize(text)

        if Language.Turkish == self.language:
            return SmoothText._compute_readability_tur_(sentences, formula)

        if Language.English == self.language:
            return SmoothText._compute_readability_eng_(sentences, formula, self._syllable_tokenizer_.tokenize)

        return 0.0
