from ramonak.packages.actions import info
from ramonak.stemmer import FlexionStatStemmer

stemmer = FlexionStatStemmer()

info("@alerus/flexistat_data==20250111_125624")


while True:
    word = input("Word to stem: ")

    if word == "exit":
        break

    print(stemmer.stem_word(word))
