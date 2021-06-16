import os
import json

from diaman.utils import doccano_interaction


class WordDict():
    """Personalized word dictionary to correct misspelled words and manage
    abbreviations.

    Attributes
    ----------
    word_dict : dict
        dictionary {correct word: list of incorrect words}.

    """
    def __init__(self, language='fr', word_dict_filename='word_dict.json'):
        """Instantiate a WordDict instance.

        Parameters
        ----------
        language : string
            user language.
        word_dict_filename : string
            filename of the word dictionary.

        """
        # Check word dict filepath
        current_dirpath = os.path.dirname(os.path.realpath(__file__))
        language_dirpath = os.path.join(current_dirpath, '..', 'configuration', 'resources', language)
        self._word_dict_filepath = os.path.join(language_dirpath, word_dict_filename)
        if not os.path.exists(self._word_dict_filepath):
            raise FileExistsError(f"No '{word_dict_filename}' file in {language_dirpath}")

        # Load dict
        self._load()

    def _load(self):
        """Load word dictionary.

        """
        with open(self._word_dict_filepath) as reader:
            self.word_dict = json.load(reader)

    def enrich(self, doccano_output_filename):
        """Update the word dictionary by adding new words.

        Parameters
        ----------
        doccano_output_filename : string
            filename of the doccano output after labelling

        """
        # Load word dict from doccano file
        doccano_dirpath = os.path.join(os.environ['REPO'], 'data', 'doccano')
        doccano_output_filepath = os.path.join(doccano_dirpath, doccano_output_filename)
        if not os.path.exists(doccano_output_filepath):
            raise FileExistsError(f"No '{doccano_output_filename}' file in {doccano_dirpath}")
        doccano_dict = doccano_interaction.doccano_file_to_word_dict(doccano_output_filepath)

        # Update word_dict by adding the words of doccano_dict not already present
        merge_word_dicts(self.word_dict, doccano_dict)

        # Remove incorrect words if they also are correct words
        for correct_word in self.word_dict.keys():
            self.word_dict[correct_word] = [word for word in self.word_dict[correct_word]
                                            if word not in self.word_dict.keys()]

        # Save word_dict
        self._save()

    def _save(self):
        """Save word dictionary.

        """
        with open(self._word_dict_filepath, 'w') as writer:
            json.dump(self.word_dict, writer, indent=4)


def merge_word_dicts(ref_dict, new_dict):
    """Update ref_dict by adding the words of new_dict not already present.

    Parameters
    ----------
    ref_dict : dict
        initial dictionary.
    new_dict : dict
        dictionary containing the words to add.

    """
    # Enrich the incorrect words of the ref_dict
    already_existing_words = []
    for word in new_dict:
        for correct_word, incorrect_words in ref_dict.items():
            if (word == correct_word) | (word in incorrect_words):
                already_existing_words.append(word)
                ref_dict[correct_word] = list(set(ref_dict[correct_word]
                                                  + new_dict[word]))
                break

    # Restrict the new_dict to words that don't already exist in the ref_dict
    new_dict = {correct_word: incorrect_words
                for correct_word, incorrect_words in new_dict.items()
                if correct_word not in already_existing_words}

    ref_dict.update(new_dict)
