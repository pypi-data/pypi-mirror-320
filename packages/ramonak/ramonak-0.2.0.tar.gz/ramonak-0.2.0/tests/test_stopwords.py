import pytest

from ramonak.stemmer.base import Stemmer
from ramonak.stopwords import STOP_WORDS, clean_stop_words

fix_lang_phenomenons = Stemmer.fix_lang_phenomenons


specific_words = ["мы", "аднак", "безумоўна"]


@pytest.mark.parametrize("word", specific_words)
def test_check_words(word):
    assert word in STOP_WORDS


def test_clean_stop_words_in_list():
    assert clean_stop_words(["не", "пайшоў", "а", "паехаў"]) == ["пайшоў", "паехаў"]


def test_clean_stop_words_in_str():
    assert clean_stop_words("не пайшоў, а паехаў") == "пайшоў, паехаў"
