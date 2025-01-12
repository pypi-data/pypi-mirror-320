import re
from typing import Iterable, Union

from ramonak.packages.actions import package_path, require

require("@alerus/stopwords")

STOP_WORDS = (
    (package_path("@alerus/stopwords") / "belarusian.txt")
    .read_text(encoding="utf8")
    .split("\n")
)


def clean_stop_words(data: Union[str, Iterable[str]]) -> Union[str, Iterable[str]]:
    if type(data) is str:
        for word in STOP_WORDS:
            data = re.sub(r"\b{}\b".format(word), "", data)

        data = re.sub(r" {2,}", " ", data)
        data = data.strip()
    else:
        word_list = []

        for data_word in data:
            if type(data_word) is not str:
                raise Exception(
                    "Wrong type: {}. Data must be str or an iterable with str".format(
                        type(data_word).__name__
                    )
                )

            if data_word not in STOP_WORDS:
                word_list.append(data_word)

        data = word_list

    return data
