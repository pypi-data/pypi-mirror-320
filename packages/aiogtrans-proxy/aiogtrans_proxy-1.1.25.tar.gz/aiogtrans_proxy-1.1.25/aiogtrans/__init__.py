"""
Free Google Translate API for Python. Translates totally free of charge.

Forked by _Leg3ndary after original project was abandoned.

Licensed Under MIT
------------------

Copyright (c) 2022 Ben Z

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
"""

__all__ = (
    "Translator",
    "LANGCODES",
    "LANGUAGES",
    "Translated",
    "Detected",
)

from aiogtrans.client import Translator
from aiogtrans.constants import LANGCODES, LANGUAGES
from aiogtrans.models import Detected, Translated
