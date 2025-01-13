from ramonak.stemmer.base import Stemmer

fix_lang_phenomenons = Stemmer.fix_lang_phenomenons


def test_dz_ts_and_jvowel():
    assert fix_lang_phenomenons("савецізіраваны") == "саветызіраваны"


def test_dz_ts_jvowel_and_v():
    assert fix_lang_phenomenons("дзве") == fix_lang_phenomenons("двэ")
