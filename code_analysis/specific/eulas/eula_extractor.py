"""
Get information from EULAS

output to similarly named files in analysis directory
"""
import spacy
from enum import Enum
from os.path import join, isfile, exists, abspath
from os.path import split, isdir, splitext, expanduser
from os import listdir
from random import shuffle
import pyparsing as pp

nlp = spacy.load("en_core_web_sm")

import analysis_case as AC
import utils

# Setup root_logger:
import logging as root_logger
LOGLEVEL = root_logger.DEBUG
LOG_FILE_NAME = "log.{}".format(splitext(split(__file__)[1])[0])
root_logger.basicConfig(filename=LOG_FILE_NAME, level=LOGLEVEL, filemode='w')

console = root_logger.StreamHandler()
console.setLevel(root_logger.INFO)
root_logger.getLogger('').addHandler(console)
logging = root_logger.getLogger(__name__)
##############################
LEFT_QUOTE = "‘"
RIGHT_QUOTE = "’"
LEFT_DBL_QUOTE = "“"
RIGHT_DBL_QUOTE = "”"
DBL_QUOTE = '"'


# Enums:

def build_parser():
    return None

def extract_from_file(filename, ctx):
    logging.info("Extracting from: {}".format(filename))
    data = { '__unique_words' : set(),
             '__total_count' : 0,
             '__sen_counts'  : {},
             '__nouns'       : set(),
             '__pronouns'    : {},
             '__speech'      : [],
             '__colours'     : set(),
             '__honorifics'  : set(),
             '__clothes'     : [],
             '__environments' : [],
             '__actions'     : set(),
             '__genders'     : [],
             '__death'       : [],
             '__entities'    : set(),
             '__verb_pairs'  : set()
    }
    lines = []
    with open(filename,'rb') as f:
        lines = [x for x in f.read().decode('utf-8','ignore').split('\n')]

    state = { 'bracket_count' : 0,
              'current' : None,
              'line' : 0,
              'potential_speech' : None,
              'sentence_start' : 0,
              'sentence_length' : 0
              }
    while bool(lines):
        state['line'] += 1
        current = lines.pop(0)

        state['sentence_start'] = 0
        state['sentence_length'] = 0
        state['potential_speech'] = None


        parsed = nlp(current)

        # Get entities:
        for ent in parsed.ents:
            data['__entities'].add((ent.text, ent.label_))


        # TODO split into sections of commitments
        # TODO extract permissions and prohibitions
        # TODO extract responsibilities

        for word in parsed:

            # Count lemmas
            word_lemma = word.lemma_.lower()
            if word_lemma not in data:
                data['__unique_words'].add(word_lemma)
                data[word_lemma] = 0
            data[word_lemma] += 1

            # Get Noun Verb pairs
            if word.tag_ == "NNP":
                data['__nouns'].add(word.text)
                if word.dep_ == "nsubj" and word.head.pos_ == "VERB":
                    heads = [word.head.text] + [x.text for x in word.head.children if x.dep_ == 'conj' and x.pos_ == "VERB"]
                    data['__verb_pairs'].add((word.text, ",".join(heads)))

            # Get Pronouns
            if word.pos_ == "PRON":
                if word.text not in data['__pronouns']:
                    data['__pronouns'][word.text] = 0
                data['__pronouns'][word.text] += 1
                if word.dep_ == "nsubj" and word.head.pos_ == "VERB":
                    heads = [word.head.text] + [x.text for x in word.head.children if x.dep_ == 'conj' and x.pos_ == "VERB"]
                    data['__verb_pairs'].add((word.text, ",".join(heads)))

            # Get Verbs
            if word.pos_ == "VERB":
                data['__actions'].add(word.lemma_)

            # Count sentence lengths
            if word.is_punct and word.text in [".","?","!"]:
                if state['sentence_length'] not in data['__sen_counts']:
                    data['__sen_counts'][state['sentence_length']] = 0
                data['__sen_counts'][state['sentence_length']] += 1
                state['sentence_length'] = 0
            else:
                state['sentence_length'] += 1



    return data


if __name__ == "__main__":
    input_ext = ".txt"
    output_lists = []
    output_ext = ".eula_analysis"

    AC.AnalysisCase(__file__,
                    input_ext,
                    extract_from_file,
                    output_lists,
                    output_ext)()
