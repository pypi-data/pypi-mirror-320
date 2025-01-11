import gc
from collections import Counter
from os.path import commonprefix
from pathlib import Path
from typing import List, Tuple

from lxml import etree

from ramonak.packages.actions import package_path as rm_pkg_path
from ramonak.packages.actions import require

require("@bnkorpus/grammar_db/20230920")


def find_flexions(words) -> List[str]:
    common_prefix = commonprefix(words)
    flexions = []

    if common_prefix == "":
        return flexions

    for word in words:
        if word == common_prefix:
            continue

        if len(common_prefix) - len(word) == 1:
            continue

        flexions.append(word[len(common_prefix) :])

    return flexions


def extract_stem_data(ncorp_xml_path) -> Tuple[List[str], List[str]]:
    f = etree.parse(ncorp_xml_path)
    root = f.getroot()

    print("File has been loaded in lxml")

    flexions_in_file = []
    unchangeable_words = []

    for variant in root.findall("Paradigm/Variant"):
        processed_variant_lemma = variant.get("lemma").replace("+", "")
        variant_forms = variant.findall("Form")

        processed_forms = []

        if "-" in processed_variant_lemma:
            continue

        if (
            len(variant_forms) == 1
            and variant_forms[0].text.replace("+", "") == processed_variant_lemma
        ):
            unchangeable_words.append(processed_variant_lemma)
            continue

        for form in variant.findall("Form"):
            processed_forms.append(form.text.replace("+", ""))

        flexions = find_flexions((processed_variant_lemma, *processed_forms))
        flexions_in_file.extend(flexions)

    return flexions_in_file, unchangeable_words


def xml_stem_data_stats(xml_dir_path: str) -> Tuple[Tuple[str, int]]:
    all_flexions = []
    unchangeable_words = []

    for xml_file in Path(xml_dir_path).glob("*.xml"):
        print("Processing", xml_file)
        file_stem_data = extract_stem_data(xml_file)

        all_flexions.extend(file_stem_data[0])
        unchangeable_words.extend(file_stem_data[1])
        gc.collect()

    print(
        "All flexions: {}, all unchangeable words: {}. Counting total stats...".format(
            len(all_flexions), len(unchangeable_words)
        )
    )

    flexions_and_count = Counter(all_flexions).items()
    unchangeable_words = tuple(set(unchangeable_words))

    print(
        "Unique flexions: {}, unique unchangeable words: {}. Sorting...".format(
            len(flexions_and_count), len(unchangeable_words)
        )
    )

    flexions_and_count = sorted(flexions_and_count, key=lambda x: x[1], reverse=True)

    return flexions_and_count


def get_stem_data():
    flexions_and_count = xml_stem_data_stats(
        rm_pkg_path("@bnkorpus/grammar_db/20230920")
    )

    max_count = flexions_and_count[0][1]

    flexions_and_count = map(
        lambda x: (x[0], round(x[1] / max_count, 1)), flexions_and_count
    )
    flexions_and_count = tuple(filter(lambda x: x[1] > 0, flexions_and_count))

    print("Valuable flexions: {}".format(len(flexions_and_count)))

    return tuple(x[0] for x in flexions_and_count)
