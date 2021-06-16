import os
import logging
import argparse
import re
import pandas as pd
import Levenshtein as lev

from diaman.configuration.app import AppConfig
from diaman.interface.kernel import DiamanKernel
from diaman.utils import doccano_interaction


def run(code_shop, min_word_count, language='fr'):
    """Run the pipeline to prepare groups of close words to be labeled in doccano.

    Parameters
    ----------
    code_shop : string
        shop chosen for the labelling.
    min_word_count : int
        minimum number of occurrences of a word in order to be kept
    language : string
        language of words.

    """
    # Configurations
    AppConfig()
    doccano_dirpath = os.path.join(os.environ['REPO'], 'data', 'doccano')

    logging.info('===========================================================')
    logging.info(f'Starting pipeline to prepare the doccano labelling for the {code_shop} shop')

    logging.info('Retrieving the corpus words & finding the most used words')
    diaman_kernel = DiamanKernel(language, code_shop)
    df_shop = diaman_kernel.description_vect.df_preprocessed

    # Count words in the corpus
    df_wc = df_shop['corpus'] \
        .apply(lambda x: ' '.join(re.findall('\w+(?:[\?\-\"_]\w+)*', x, re.M+re.DOTALL))) \
        .str.split(' ', expand=True) \
        .stack() \
        .value_counts() \
        .reset_index() \
        .rename(columns={'index': 'word', 0: 'count'})

    # Keep words with no digit & at least 3 letters
    df_wc = df_wc.loc[(df_wc['word']
                       .apply(lambda x: (len(re.findall('\d', x)) == 0) & (len(x) >= 3)))]

    # Keep the most used words
    most_used_words = df_wc.loc[df_wc['count'] > min_word_count, 'word'].tolist()
    logging.info((f'{len(most_used_words)} words with at least {min_word_count} '
                  f'occurrences in the {code_shop} shop reports'))

    # Acronyms
    acronyms = [word for word in most_used_words if len(word) == 3]

    acronyms_filepath = os.path.join(doccano_dirpath, f'acronyms_{code_shop}.csv')
    logging.info(f'Saving the acronyms in {acronyms_filepath}')
    pd.DataFrame(data=acronyms, columns=['acronym']).to_csv(acronyms_filepath, index=False)

    # Words to group
    words_to_group = [word for word in most_used_words if len(word) > 3]
    word_groups = generate_word_groups(words_to_group)
    word_groups = [group for group in word_groups if len(group) > 1]  # groups with at least 2 words
    logging.info(f'Found {len(word_groups)} groups of words to label')
    df_groups = pd.DataFrame(data=[' '.join(group) for group in word_groups],
                             columns=['similar_words']).reset_index()

    doccano_input_filepath = os.path.join(doccano_dirpath, f'doccano_input_{code_shop}.json')
    logging.info(f'Saving doccano input file in {doccano_input_filepath}')
    doccano_interaction.pandas_to_doccano_file(df_groups, 'similar_words', 'index',
                                               doccano_input_filepath, 'all',
                                               {"INCORRECT": '\\b\\w+\\b'})

    logging.info('*** Pipeline finished ***')


def generate_word_groups(list_of_words, max_distance=2):
    """Generate groups of words.

    Parameters
    ----------
    list_of_words : list of strings
        list of the words to group
    max_distance : int
        maximum number of operations to change a word in another

    """
    word_groups = list()
    for word in list_of_words:
        for g in word_groups:
            if all(lev.distance(word, w) <= max_distance for w in g):
                g.append(word)
                break
        else:
            word_groups.append([word])
    return word_groups


if __name__ == '__main__':
    # Parse the cli arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('code_shop', help='shop chosen for the labelling')
    parser.add_argument('--min-word-count',
                        help='minimum number of occurrences of a word in order to be kept',
                        default=10)
    args = parser.parse_args()

    # Run pipeline
    try:
        run(args.code_shop, int(args.min_word_count))
    except Exception as e:
        logging.error(e)
