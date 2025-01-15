#!/usr/bin/env python3

"""
Example use:
------------

**WARNING:** Due to the licensing issues the raw data for LIWC categories
cannot be distributed with NVM package (unfortunately, you have to get
the data yourself).

>>> import srsly
>>> from nvm.aux_spacy.data.BrysbaertEtAl2014a import concr_dict
>>> print(srsly.yaml_dumps(concr_dict))
>>> print(srsly.yaml_dumps(list(concr_dict.keys())))

"""

import srsly
from importlib import resources


try:
    with resources.path("pyconcr.data.BrysbaertEtAl2014a", "concr_values.json") as if0:
        concr_dict = srsly.read_json(if0)
except FileNotFoundError as e:
    print(str(e))
    print(
        " ".join(
            [
                "Due to licensing issues, we cannot distribute LIWC raw data with the NVM package.",
                "Unfortunately, you need to get the raw data for LIWC categories at your own.",
            ]
        )
    )
    concr_dict = None
