#!/usr/bin/env python3

from typing import (
    Dict,
    List,
    # Union,
    Optional,
    # Callable,
)

import numpy as np
import logging
import warnings

import spacy
from spacy.language import Language

from spacy.tokens import Doc, Span, Token
from spacy.tokens.underscore import Underscore

from spacy.symbols import ORTH

from spacy.matcher import PhraseMatcher
from spacy.util import filter_spans

# from spacy.tokens.underscore import Underscore

from pyconcr.data.BrysbaertEtAl2014a import concr_dict as concr_dict_orig


@Language.factory(
    "get_doc_concreteness",
    default_config={
        "dict0": concr_dict_orig,
        "cases": True,
        "log0": logging.getLogger("dummy"),
    },
)
def get_doc_concreteness_component(
    nlp: Language,
    name: str,
    dict0: Dict,
    cases: bool,
    log0: logging.Logger,
):
    """Get concreteness.

    Example use:
    ------------
    >>> import spacy
    >>> import srsly
    >>> from nvm.aux_spacy import get_doc_summary_dict_component
    >>> from nvm.aux_spacy import get_doc_concreteness_component
    >>> nlp = spacy.load("en_core_web_sm")
    >>> nlp.tokenizer.add_special_case("cannot", [{spacy.symbols.ORTH: "cannot"}])  # IMPORTANT
    >>> nlp.add_pipe("get_doc_concreteness", "CONCR")
    >>> # This should be the last one
    >>> nlp.add_pipe("get_doc_summary_dict", "SUMMARY")
    >>> doc = nlp("I want to make a sentence and I want it to contain exactly four verbs and three nouns.")
    >>> print(srsly.yaml_dumps(doc._.SUMMARY))
    >>> print(doc._.concr_info)

    """
    return ConcrComponent(
        nlp,
        # WARNING: This use of name is not for pipeline element
        # but for variable/column name.
        name,
        dict0,
        cases,
        log0=log0,
    )


class ConcrComponent:
    def __init__(
        self,
        nlp: Language,
        name: str,
        dict0: Dict,
        cases: bool,
        log0: logging.Logger = logging.getLogger("dummy"),
    ):
        # SEE: https://spacy.io/usage/processing-pipelines#example-stateful-components

        self.log0 = log0

        # CONCRETENESS
        if cases:
            self.concr_dict = dict()
            self.concr_dict.update({key0.lower(): val0 for key0, val0 in dict0.items()})
            self.concr_dict.update({key0.upper(): val0 for key0, val0 in dict0.items()})
            self.concr_dict.update(
                {key0.capitalize(): val0 for key0, val0 in dict0.items()}
            )
        else:
            self.concr_dict = dict()
            self.concr_dict.update({key0.lower(): val0 for key0, val0 in dict0.items()})

        # ONETWOGRAMS
        self.concr_list = list(self.concr_dict.keys())

        # PATTERNS
        self.patterns = list(nlp.tokenizer.pipe(self.concr_list))
        # self.patterns = [nlp.make_doc(term) for term in self.concr_list]  # DEPRECATED
        # self.patterns = list(nlp.pipe(self.concr_list))  # DEPRECATED

        ### OPEN: Consider if this can be better that the above `cases'
        ### SEE: https://github.com/explosion/spaCy/issues/1579
        ### as an alternative is to use INPUT_TEXT.lower().

        ### Create the matcher and match on Token.lower if case-insensitive
        ### matcher_attr = "TEXT" if dict0 else "LOWER"
        ### self.matcher = PhraseMatcher(nlp.vocab, attr=matcher_attr)
        ### self.matcher.add("ACRONYMS", [nlp.make_doc(term) for term in DICTIONARY])

        # Update nlp with a special case of token `cannot'
        # (it is used in some dictionaries as one token)
        nlp.tokenizer.add_special_case("cannot", [{ORTH: "cannot"}])

        self.matcher = PhraseMatcher(nlp.vocab)
        self.matcher.add("CONCR_MATCHER", self.patterns)

        # Register custom extensions on the Span and Doc
        # TODO: FIXME: Add the component name/ID (same as with factories)
        ext0 = "concr_value"
        self.log0.debug(f"Adding Span extension {ext0!r}")
        if Span.has_extension(ext0):
            self.log0.warning(f"Span extension {ext0!r} was replaced.")
            Span.remove_extension(ext0)

        Span.set_extension(ext0, getter=self.concr_value)

        ext0 = "concr_spans"
        self.log0.debug(f"Adding Doc extension {ext0!r}")
        if Doc.has_extension(ext0):
            self.log0.warning(f"Doc extension {ext0!r} was replaced.")
            Doc.remove_extension(ext0)

        Doc.set_extension(ext0, default=[])

        ext0 = "concr_info"
        self.log0.debug(f"Adding Doc extension {ext0!r}")
        if Doc.has_extension(ext0):
            self.log0.warning(f"Doc extension {ext0!r} was replaced.")
            Doc.remove_extension(ext0)

        Doc.set_extension(ext0, getter=self.concr_info)

        ext0 = "concr_count"
        self.log0.debug(f"Adding Doc extension {ext0!r}")
        if Doc.has_extension(ext0):
            self.log0.warning(f"Doc extension {ext0!r} was replaced.")
            Doc.remove_extension(ext0)

        Doc.set_extension(ext0, getter=self.concr_count)

        ext0 = "concr_sum"
        self.log0.debug(f"Adding Doc extension {ext0!r}")
        if Doc.has_extension(ext0):
            self.log0.warning(f"Doc extension {ext0!r} was replaced.")
            Doc.remove_extension(ext0)

        Doc.set_extension(ext0, getter=self.concr_sum)

        ext0 = "concr_mean"
        self.log0.debug(f"Adding Doc extension {ext0!r}")
        if Doc.has_extension(ext0):
            self.log0.warning(f"Doc extension {ext0!r} was replaced.")
            Doc.remove_extension(ext0)

        Doc.set_extension(ext0, getter=self.concr_mean)

    def __call__(self, doc: Doc) -> Doc:
        matches = self.matcher(doc)
        spans = [
            Span(doc, start, end, label="CONCR") for match_id, start, end in matches
        ]
        spans = filter_spans(spans)
        # spans = [span.text for span in spans]  # This is no good as we later need Span extension
        # doc._.concr_spans = spans
        # TRY THIS
        doc._.concr_spans = [[sp.text, sp._.concr_value] for sp in spans]
        """
        # Add the matched spans when doc is processed
        for _, start, end in self.matcher(doc):
            span = doc[start:end]
            acronym = DICTIONARY.get(span.text if self.dict0 else span.text.lower())
            doc._.acronyms.append((span, acronym))
        """
        return doc

    def concr_value(self, span):
        if span.text in self.concr_dict:
            concr_val = self.concr_dict.get(span.text)
        else:
            concr_val = np.nan
            self.log0.warning(
                f"problem with getting concreteness value for the extracted span {span.text!r}."
            )

        return concr_val

    def concr_info(self, doc):
        """Get the concreteness spans info."""
        # span_concr_info = [{sp.text: sp._.concr_value} for sp in doc._.concr_spans]
        # return span_concr_info
        return doc._.concr_spans

    def concr_count(self, doc):
        """Get the number of concreteness spans in DOC."""
        return len(doc._.concr_spans)

    def concr_sum(self, doc):
        """Get the sum of concreteness span values in DOC."""
        # span_concr_vals = [sp._.concr_value for sp in doc._.concr_spans]
        span_concr_vals = [item[1] for item in doc._.concr_spans]
        if len(span_concr_vals) == 0:
            span_concr_sum = np.nan
        else:
            span_concr_sum = float(np.nansum(span_concr_vals))

        return span_concr_sum

    def concr_mean(self, doc):
        """Get the mean of concreteness span values in DOC."""
        # span_concr_vals = [sp._.concr_value for sp in doc._.concr_spans]
        span_concr_vals = [item[1] for item in doc._.concr_spans]
        if len(span_concr_vals) == 0:
            span_concr_mean = np.nan
        else:
            span_concr_mean = float(np.nanmean(span_concr_vals))

        return span_concr_mean
