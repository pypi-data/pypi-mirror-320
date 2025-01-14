from ramonak.stemmer.flexistat import FlexionStatStemmer


def test_flexistat_stemmer():
    stemmer = FlexionStatStemmer()

    assert stemmer.stem_words(["лесам", "лесу", "лесамі"]) == (["лес"] * 3)


def test_flexistat_stemmer_u():
    stemmer = FlexionStatStemmer()

    assert stemmer.stem_word("ўдот") == "удот"
