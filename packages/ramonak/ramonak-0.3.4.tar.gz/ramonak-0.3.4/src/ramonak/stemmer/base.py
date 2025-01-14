class Stemmer:
    def stem_word(self, word):
        raise NotImplementedError()

    def stem_words(self, words: list[str]) -> list[str]:
        result = []

        for word in words:
            result.append(self.stem_word(word))

        return result
