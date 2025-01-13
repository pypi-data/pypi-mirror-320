import re


class Stemmer:
    def stem_word(self, word):
        raise NotImplementedError()

    @staticmethod
    def fix_lang_phenomenons(word: str) -> str:
        # region dzekannie, tsekannie, soft + jvowel = hard + jvowel
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
        # endregion

        # region Remove ў at the beginning
        word = re.sub(r"^ў", "у", word)
        # endregion

        return word

    def stem_words(self, words: list[str]) -> list[str]:
        result = []

        for word in words:
            result.append(self.stem_word(word))

        return result
