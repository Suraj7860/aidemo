import os
import logging
import pandas as pd
import json
import yaml
from collections import namedtuple


ProcessingParameters = namedtuple('ProcessingParameters', [
    'strip_accents', 'lowercase', 'max_df', 'min_df', 'ngram_range', 'max_iter',
    'evaluate_every', 'perp_tol', 'n_components', 'learning_method', 'random_state'])


class DataConfig:
    def __init__(self, language=None):
        # config filepaths
        dir_path = os.path.dirname(os.path.realpath(__file__))
        base_path = os.path.join(dir_path, 'resources')

        # General files
        self._perimeter_filepath = os.path.join(base_path, 'perimeter.json')
        self._processing_filepath = os.path.join(base_path, 'processing_conf.yml')
        self._prepare_perimeter_configuration()
        self._prepare_processing_params_configuration()

        # Language specific files
        if language is not None:
            language_path = os.path.join(base_path, language)
            self._stopwords_filepath = os.path.join(language_path, 'stopwords.txt')
            self._word_dict_filepath = os.path.join(language_path, 'word_dict.json')
            self._prepare_stopwords_configuration()
            self._prepare_word_dict_configuration()

    def _prepare_perimeter_configuration(self):
        """Load the industrialisation perimeter."""
        logging.info("  - Loading 'perimeter' attributes")
        with open(self._perimeter_filepath) as json_file:
            perimeter = json.load(json_file)
        self._indus_perimeter = perimeter['indus_perimeter']
        self.gmt_columns = perimeter['gmt_columns']
        self.diaman_search_cols = perimeter['diaman_search_cols']

        self.indus_languages = [code_language for code_language in self._indus_perimeter
                                if len(self._indus_perimeter[code_language]['shops']) > 0]
        self.psa_sites = [site for sites in [self.get_sites(language)
                                             for language in self._indus_perimeter]
                          for site in sites]

    def _prepare_processing_params_configuration(self):
        """Load the 'processing_params' attribute.
        These parameters control the LDA algorithm & have a scientific impact.
        """
        logging.info("  - Loading the Processing Parameters")
        with open(self._processing_filepath) as f:
            config = yaml.load(f.read(), Loader=yaml.FullLoader)
            if 'vect_parameters' not in config:
                raise(KeyError("vect_parameters configuration not found."))
            if 'lda_parameters' not in config:
                raise(KeyError("lda_parametersconfiguration not found."))
            self.processing_params = \
                ProcessingParameters(strip_accents=config['vect_parameters']['strip_accents'],
                                     lowercase=config['vect_parameters']['lowercase'],
                                     max_df=config['vect_parameters']['max_df'],
                                     min_df=config['vect_parameters']['min_df'],
                                     ngram_range=(config['vect_parameters']['ngram_range']['min'],
                                                  config['vect_parameters']['ngram_range']['max']),
                                     max_iter=config['lda_parameters']['max_iter'],
                                     evaluate_every=config['lda_parameters']['evaluate_every'],
                                     perp_tol=config['lda_parameters']['perp_tol'],
                                     n_components=config['lda_parameters']['n_components'],
                                     learning_method=config['lda_parameters']['learning_method'],
                                     random_state=config['lda_parameters']['random_state'])

    def _prepare_stopwords_configuration(self):
        """Load the personalized list of stopwords."""
        logging.info("  - Loading 'stopwords' attribute")
        with open(self._stopwords_filepath, 'r') as f:
            self.stopwords = f.read().splitlines()

    def _prepare_word_dict_configuration(self):
        """Load the personalized correction dictionnary."""
        logging.info("  - Loading 'word_dict' attribute")
        with open(self._word_dict_filepath) as json_file:
            self.word_dict = json.load(json_file)

    def get_shops(self, language):
        """Get shops of a specific language.

        Parameters
        ----------
        language : string
            user's language

        """
        return self._indus_perimeter[language]['shops']

    def get_sites(self, language):
        """Get sites of a specific language.

        Parameters
        ----------
        language : string
            user's language

        """
        return [site for site, _ in self._indus_perimeter[language]['sites'].items()]

    def get_language(self, code_site):
        """Get language of a specific code_site.

        Parameters
        ----------
        code_site : string
            code_site corresponding to the user's site

        """
        return [language for language in self._indus_perimeter
                if code_site in list(self._indus_perimeter[language]['sites'].keys())][0]
