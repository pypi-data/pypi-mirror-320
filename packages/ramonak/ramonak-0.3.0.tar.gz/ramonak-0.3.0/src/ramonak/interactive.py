from ramonak.stemmer import SnowballStemmer

stemmer = SnowballStemmer()


while True:
    word = input("Word to stem: ")

    if word == "exit":
        break

    print(stemmer.stem_word(word))
