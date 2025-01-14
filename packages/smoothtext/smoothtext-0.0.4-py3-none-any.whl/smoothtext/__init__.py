#  SmoothText - https://smoothtext.tugrulgungor.me/
#
#  Copyright (c) 2025 - present. All rights reserved.
#  Tuğrul Güngör - https://tugrulgungor.me
#
#  Distributed under the MIT License.
#  https://opensource.org/license/mit/

from .smoothtext import SmoothText, ReadabilityFormula, Language

__version__ = (0, 0, 4)

for attribute in dir(SmoothText):
    if callable(getattr(SmoothText, attribute)):
        if not attribute.startswith("_"):
            globals()[attribute] = getattr(SmoothText, attribute)
