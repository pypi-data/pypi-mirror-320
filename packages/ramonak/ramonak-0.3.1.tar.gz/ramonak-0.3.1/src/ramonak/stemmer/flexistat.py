from ramonak.packages.actions import require

from .base import Stemmer


class FlexionStatStemmer(Stemmer):
    def __init__(self):
        flexistat_dir = require("@alerus/flexistat_data")

        self.unchangeable_words = []
        self.flexions = []

        for word in open(
            flexistat_dir / "unchangeable_words.txt",
            "r",
            encoding="utf8",
        ).readlines():
            word = word.strip()

            if word:
                self.unchangeable_words.append(word)

        for flexion in open(
            flexistat_dir / "flexions.txt",
            "r",
            encoding="utf8",
        ).readlines():
            flexion = flexion.strip()

            if flexion:
                self.flexions.append(flexion)

    def stem_word(self, word: str) -> str:
        if word in self.unchangeable_words:
            return word

        word = FlexionStatStemmer.fix_lang_phenomenons(word)

        for flexion in self.flexions:
            if word.endswith(flexion):
                return word[: -len(flexion)]

        return word
