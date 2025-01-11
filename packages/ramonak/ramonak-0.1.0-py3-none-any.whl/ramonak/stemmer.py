import re

from ramonak.packages.actions import package_path, require


class SimpleStemmer:
    def __init__(self):
        require("@alerus/stemdata")

        self.unchangeable_words = []
        self.flexions = []

        for word in open(
            package_path("@alerus/stemdata") / "unchangeable_words.txt",
            "r",
            encoding="utf8",
        ).readlines():
            word = word.strip()

            if word:
                self.unchangeable_words.append(word)

        for flexion in open(
            package_path("@alerus/stemdata") / "flexions.txt", "r", encoding="utf8"
        ).readlines():
            flexion = flexion.strip()

            if flexion:
                self.flexions.append(flexion)

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

        return word

    def stem_word(self, word: str) -> str:
        if word in self.unchangeable_words:
            return word

        word = SimpleStemmer.fix_lang_phenomenons(word)

        for flexion in self.flexions:
            if word.endswith(flexion):
                return word[: -len(flexion)]

        return word
