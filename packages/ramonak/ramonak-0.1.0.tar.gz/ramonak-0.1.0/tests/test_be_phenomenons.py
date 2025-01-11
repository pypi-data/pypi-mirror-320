from ramonak.stemmer import SimpleStemmer

fix_lang_phenomenons = SimpleStemmer.fix_lang_phenomenons


def test_dz_ts_and_jvowel():
    assert fix_lang_phenomenons("савецізіраваны") == fix_lang_phenomenons(
        "саветызіраваны"
    )


def test_dz_ts_jvowel_and_v():
    assert fix_lang_phenomenons("дзве") == fix_lang_phenomenons("двэ")
