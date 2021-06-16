import os
import unicodedata
import pandas as pd

from diaman.configuration.data import DataConfig
from diaman.domain import preprocessing


data_config = DataConfig('fr')
filepath = os.path.join(os.environ['BIN'], 'test', 'resources', 'reports_sample.csv')


def test_refine_corpus():
    """[domain][preprocessing] Check the refine corpus process."""
    df_test = pd.read_csv(filepath)
    df_test = df_test[13:15]

    df_test = preprocessing.refine_corpus(df_test,
                                          corpus_col='COMMENT',
                                          stopwords=data_config.stopwords,
                                          remove_numbers=True,
                                          remove_small_words=True)

    expected_output = ['rearme relance convoyeur surveillance',
                       'effectuer remise etat bridage']
    assert df_test.tolist() == expected_output


def test_remove_comment_header():
    """[domain][preprocessing] Check if remove the head of the corpus."""
    df_test = pd.read_csv(filepath)
    df_test = df_test[13:15]

    corpus = df_test['COMMENT']
    corpus = corpus.apply(lambda x: x.lower())
    corpus = corpus.apply(lambda x: unicodedata.normalize('NFKD', x)
                          .encode('ascii', 'ignore'))
    corpus = corpus.str.decode('utf-8')
    corpus = corpus.apply(lambda x: preprocessing.remove_comment_header(x))

    expected_output = ['*  * rearme defaut et relance convoyeur , surveillance ok',
                       '*  * effectuer la remise en etat du bridage pmr 8110']
    assert corpus.tolist() == expected_output


def test_correct_words():
    """[domain][preprocessing] Check if correct the wrong words."""
    df_test = pd.read_csv(filepath)
    df_test = df_test.iloc[296:298]

    corpus = preprocessing.refine_corpus(df_test,
                                         corpus_col='COMMENT',
                                         stopwords=data_config.stopwords,
                                         remove_numbers=True,
                                         remove_small_words=True)

    corpus = preprocessing.correct_words(corpus, data_config.word_dict)

    expected_output = ['perte connexion barre shunt relance suppression shunt relance',
                       'deux postes soudes portatif remetre etat vetilateur changer cable alimentation deuxieme recherche remise etat']
    assert corpus.tolist() == expected_output
