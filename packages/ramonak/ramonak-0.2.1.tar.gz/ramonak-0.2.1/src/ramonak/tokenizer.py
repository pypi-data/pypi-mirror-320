import itertools
import re
import string

word_punct = string.punctuation + "…"
sent_punct = ".?!…"

re_word_tokenize = re.compile(r"[{}]+".format(re.escape(word_punct)))
re_word_tokenize_keep = re.compile(r"([{}]+)".format(re.escape(word_punct)))

re_sent_tokenize_keep = re.compile(
    r"([^{sent_punct}]+[{sent_punct}]+)".format(sent_punct=re.escape(sent_punct))
)


def word_tokenize(text: str, remove_punct=False) -> list[str]:
    regex = re_word_tokenize_keep

    if remove_punct:
        regex = re_word_tokenize

    result = []

    for sent_parts in regex.split(text):
        result.append(sent_parts.split())

    return list(itertools.chain(*result))


def sent_tokenize(text: str) -> list[str]:
    result = []

    for sentence in re_sent_tokenize_keep.split(text):
        sentence = sentence.strip()

        if not sentence:
            continue

        result.append(sentence)

    return result
