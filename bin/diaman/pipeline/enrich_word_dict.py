import logging
import argparse

from diaman.configuration.app import AppConfig
from diaman.utils.word_dict import WordDict


def run(doccano_output_filename, word_dict_filename='word_dict.json'):
    """Run the pipeline to enrich the word dictionary after doccano labelling.

    Parameters
    ----------
    word_dict_filename : string
        filename of the word dictionary.
    doccano_output_filename : string
        filename of the doccano output after labelling.

    """
    # Configurations
    AppConfig()

    logging.info('===========================================================')

    # Load word dictionary
    logging.info(f'Loading word dictionary from {word_dict_filename}')
    word_dict = WordDict(word_dict_filename=word_dict_filename)
    len_bef = len(word_dict.word_dict)

    # Enrich word dictionary
    logging.info(f'Enriching the word dictionary with the words in {doccano_output_filename}')
    word_dict.enrich(doccano_output_filename)
    len_aft = len(word_dict.word_dict)

    logging.info(f'{len_aft - len_bef} new words added in the dictionary')


if __name__ == '__main__':
    # Parse the cli arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('doccano_output_filename',
                        help='filename of the doccano output after labelling')
    parser.add_argument('--word-dict-filename', help='filename of the word dictionary',
                        default='word_dict.json')
    args = parser.parse_args()

    # Run pipeline
    try:
        run(args.doccano_output_filename, args.word_dict_filename)
    except Exception as e:
        logging.error(e)
