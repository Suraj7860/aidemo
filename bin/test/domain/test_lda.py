import os
import pandas as pd
from sklearn.decomposition import LatentDirichletAllocation

from diaman.configuration.data import DataConfig
from diaman.domain.vectorizer import CorpusVect
from diaman.domain import lda


data_config = DataConfig('fr')
filepath = os.path.join(os.environ['BIN'], 'test', 'resources', 'reports_sample.csv')


def test_vectorize_corpus():
    """[domain][lda] Check vectorizer process."""
    corpus_vect = CorpusVect('fr', 'STA', corpus_col='COMMENT')
    df_test = pd.read_csv(filepath)
    df_test = df_test[:70]

    corpus_vect.preprocess_corpus(df=df_test,
                                  stopwords=data_config.stopwords,
                                  word_dict=data_config.word_dict,
                                  remove_numbers=False,
                                  remove_small_words=False)

    _, dt_matrix, feature_names = lda.vectorize_corpus(corpus_vect.df_preprocessed,
                                                       data_config.processing_params)
    freq = dt_matrix.toarray().sum(axis=0)

    expected_features = ['appel', 'arret', 'auto', 'bridage', 'cable']
    expected_freq = [5, 7, 11, 11, 13]

    assert feature_names[:5] == expected_features
    assert list(freq)[:5] == expected_freq


def test_get_top_words_topics():
    """[domain][lda] Check process to get the top words in the topics."""
    corpus_vect = CorpusVect('fr', 'STA', corpus_col='COMMENT')
    df_test = pd.read_csv(filepath)
    df_test = df_test[:70]
    corpus_vect.preprocess_corpus(df=df_test,
                                  stopwords=data_config.stopwords,
                                  word_dict=data_config.word_dict,
                                  remove_numbers=False,
                                  remove_small_words=False)

    _, dt_matrix, feature_names = lda.vectorize_corpus(corpus_vect.df_preprocessed,
                                                       data_config.processing_params)

    max_iter = data_config.processing_params.max_iter
    evaluate_every = data_config.processing_params.evaluate_every
    perp_tol = data_config.processing_params.perp_tol
    n_components = data_config.processing_params.n_components
    learning_method = data_config.processing_params.learning_method
    random_state = data_config.processing_params.random_state

    lda_model = LatentDirichletAllocation(max_iter=max_iter,
                                          evaluate_every=evaluate_every,
                                          perp_tol=perp_tol,
                                          n_components=n_components,
                                          learning_method=learning_method,
                                          random_state=random_state)
    lda_model.fit(dt_matrix)
    top_words_topics = lda.get_top_words_topics(lda_model, feature_names, 4)

    expected_output = [['chute', 'essai', 'changer', 'commander'],
                       ['cable', 'tension', 'auto', 'remplacer'],
                       ['essai', 'flan', 'robot', 'piece'],
                       ['bridage', 'position', 'remis', 'fermer'],
                       ['convoyeur', 'relance', 'piece', 'haut']]

    assert top_words_topics == expected_output
