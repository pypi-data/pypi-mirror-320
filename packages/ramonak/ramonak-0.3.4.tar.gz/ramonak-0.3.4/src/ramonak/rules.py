import re


def unify_dz_ts_to_d_t(word: str) -> str:
    """Dzekannie, tsekannie, soft + jvowel = hard + jvowel"""

    vowel_pairs = {
        "е": "э",
        "ё": "о",
        "ю": "у",
        "я": "а",
        "і": "ы",
    }

    for jvowel, vowel in vowel_pairs.items():
        word = re.sub("дз" + jvowel, "д" + vowel, word)
        word = re.sub("ц" + jvowel, "т" + vowel, word)

        word = re.sub("дзв" + jvowel, "дв" + vowel, word)
        word = re.sub("цв" + jvowel, "тв" + vowel, word)

    return word


def fix_trailing_u_short(word: str) -> str:
    return re.sub(r"^ў", "у", word)


def fix_lang_phenomenons(word: str) -> str:
    # region dzekannie, tsekannie, soft + jvowel = hard + jvowel
    word = unify_dz_ts_to_d_t(word)
    # endregion

    # region Remove ў at the beginning
    word = fix_trailing_u_short(word)
    # endregion

    return word
