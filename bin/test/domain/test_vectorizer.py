import os
import pandas as pd

from diaman.configuration.data import DataConfig
from diaman.domain.vectorizer import CorpusVect
from diaman.domain import vectorizer


data_config = DataConfig('fr')
filepath = os.path.join(os.environ['BIN'], 'test', 'resources', 'reports_sample.csv')


def test_distance_to_description():
    """[domain][vectorizer] Check the distance between the input text and each description."""
    corpus_vect = CorpusVect('fr', 'STA', corpus_col='DESCR_ORDER')
    df_test = pd.read_csv(filepath)
    user_search = 'position'

    corpus_vect.preprocess_corpus(df=df_test,
                                  stopwords=data_config.stopwords,
                                  word_dict=data_config.word_dict,
                                  remove_numbers=False,
                                  remove_small_words=False)
    corpus_vect.create_vectorizer()
    corpus_vect.df_preprocessed = vectorizer.distance_to_description(corpus_vect,
                                                                     user_search)

    output = list(corpus_vect.df_preprocessed['similarity']
                             .sort_values(ascending=False)[:5])

    expected_output = [0.7438802475828189, 0.6475842063276834, 0.5636870610096454,
                       0.5636870610096454, 0.5425504279620771]
    assert output == expected_output


def test_distance_to_comment():
    """[domain][vectorizer] Check the distance between the input text and each comment."""
    corpus_vect = CorpusVect('fr', 'STA', corpus_col='COMMENT')
    df_test = pd.read_csv(filepath)
    user_search = 'coussin'

    # df_test['COMMENT'] = df_test['COMMENT'].astype(str)
    corpus_vect.preprocess_corpus(df=df_test,
                                  stopwords=data_config.stopwords,
                                  word_dict=data_config.word_dict,
                                  remove_numbers=False,
                                  remove_small_words=False)
    corpus_vect.create_vectorizer()
    corpus_vect.df_preprocessed = vectorizer.distance_to_comment(corpus_vect,
                                                                 user_search)

    output = list(corpus_vect.df_preprocessed['similarity']
                             .sort_values(ascending=False)[:5])

    expected_output = [1.0, 1.0, 0.9821428571428572, 0.9821428571428572,
                       0.9821428571428572]
    assert output == expected_output
