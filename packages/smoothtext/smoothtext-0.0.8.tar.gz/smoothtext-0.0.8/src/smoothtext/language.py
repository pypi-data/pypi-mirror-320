#  SmoothText - https://smoothtext.tugrulgungor.me/
#
#  Copyright (c) 2025 - present. All rights reserved.
#  Tuğrul Güngör - https://tugrulgungor.me
#
#  Distributed under the MIT License.
#  https://opensource.org/license/mit/

from __future__ import annotations
from enum import Enum


class Language(Enum):
    """
    Languages supported by SmoothText.

    Attributes:
        English: English language.
        Turkish: Turkish language.
    """

    English = 'English'
    Turkish = 'Turkish'

    def __str__(self) -> str:
        return self.value

    def alpha2(self) -> str:
        """
        Returns string representation of language.
        :return: String representation of language.
        """

        if self == Language.English:
            return 'en'

        if self == Language.Turkish:
            return 'tr'

    def alpha3(self) -> str:
        """
        Returns string representation of language.
        :return: String representation of language.
        """

        if self == Language.English:
            return 'eng'

        if self == Language.Turkish:
            return 'tur'

    @staticmethod
    def values() -> list[Language]:
        """
        Returns list of supported languages.
        :return: List of supported languages.
        """

        return [Language.English, Language.Turkish]

    @staticmethod
    def parse(language: Language | str) -> Language:
        """
        Parses language string into supported languages.
        :param language: Language string to parse.
        :return: Language parsed into supported languages.
        :exception ValueError: If language is not supported.
        """

        if isinstance(language, Language):
            return language

        language = language.lower()

        if Language.English.alpha2() == language or Language.English.alpha3() == language or Language.English.value.lower() == language:
            return Language.English

        if Language.Turkish.alpha2() == language or Language.Turkish.alpha3() == language or Language.Turkish.value.lower() == language:
            return Language.Turkish

        raise ValueError('Unknown language.')
