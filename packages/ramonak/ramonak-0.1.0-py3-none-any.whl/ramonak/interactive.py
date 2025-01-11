from ramonak.stemmer import SimpleStemmer

stemmer = SimpleStemmer()

while True:
    word = input("Word to stem: ")
    print(stemmer.stem_word(word))
