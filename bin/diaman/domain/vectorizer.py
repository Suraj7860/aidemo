import logging
import os
import datetime
import pickle
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from . import preprocessing


class CorpusVect():
    """Compute a vectorizer and operate on a corpus of text documents.

    Attributes
    ----------
    corpus_col : string
        name of the column containing the text information
    histo_path : string
        path to the saving location
    df_preprocessed : pd.DataFrame
        input dataframe with additional cols: 'corpus', 'similarity'
    vectorizer : CountVectorizer or TfidfVectorizer
        vectorizer fitted to a corpus of text documents
    dt_matrix : array of floats
        document-term matrix of the corpus text documents

    """
    def __init__(self, language, shop, corpus_col):
        """Initialize a CorpusVect instance.

        Parameters
        ----------
        language : string
            language of the reports
        shop : string
            shop of the plant ('emb', 'fer' ...)
        corpus_col : string
            name of the column containing the text information

        """
        self.histo_path = os.path.join(os.environ['REPO'], 'histo',
                                       language, shop)
        self.corpus_col = corpus_col

    def preprocess_corpus(self, df, stopwords, word_dict,
                          remove_numbers, remove_small_words):
        """Make pipeline to preprocess the 'corpus_col' column.

        Parameters
        ----------
        df : pd.DataFrame
            input dataframe with the corpus_col to preprocess
        stopwords : list of strings
            list containing the stopwords
        word_dict : dict
            personalized correction dictionnary
        remove_numbers : bool
            True if numbers are removed
        remove_small_words : bool
            True if small words are removed

        """
        # Create df_preprocessed attribute
        self.df_preprocessed = df.copy()

        # Preprocess the corpus_col column
        self.df_preprocessed['corpus'] = preprocessing.preprocess_corpus(df,
                                                                         self.corpus_col,
                                                                         stopwords,
                                                                         word_dict,
                                                                         remove_numbers,
                                                                         remove_small_words)

        # Preprocess the 'comment' column for the lda training
        if self.corpus_col == 'COMMENT':
            self.df_preprocessed['corpus_lda'] = preprocessing.preprocess_corpus(
                df, self.corpus_col, stopwords, word_dict,
                remove_numbers=True, remove_small_words=True)

    def create_vectorizer(self):
        """Create and fit a vectorizer to the corpus_col column."""
        corpus = self.df_preprocessed['corpus'].values.tolist()

        # Create vectorizer
        if self.corpus_col == 'DESCR_ORDER':
            self.vectorizer = TfidfVectorizer().fit(corpus)
        elif self.corpus_col == 'COMMENT':
            self.vectorizer = CountVectorizer().fit(corpus)
        else:
            logging.error(("The corpus column should be either 'description'"
                           "or 'comment'"))

        # Create document-term matrix
        self.dt_matrix = self.vectorizer.transform(corpus)

    def compute_distance(self, input_data):
        """Compute the distance between the input text and each document
        of the corpus.

        Parameters
        ----------
        input_data : string
            user search

        """
        if self.corpus_col == 'DESCR_ORDER':
            self.df_preprocessed = distance_to_description(self, input_data)
        elif self.corpus_col == 'COMMENT':
            self.df_preprocessed = distance_to_comment(self, input_data)
        else:
            logging.error(("The corpus column should be either 'description'"
                           "or 'comment'"))

    def save(self):
        """Save CorpusVect."""
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        vect_path = os.path.join(self.histo_path,
                                 'vect_{}'.format(self.corpus_col),
                                 'vect_{}_{}.pkl'.format(self.corpus_col, now))
        dir_path = os.path.dirname(vect_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        logging.info('Saving to: {}'.format(vect_path))
        with open(vect_path, 'wb') as f:
            pickle.dump([self.df_preprocessed, self.vectorizer,
                         self.dt_matrix],
                        f, protocol=pickle.HIGHEST_PROTOCOL)

    def load(self, vect_filepath=None):
        """Load CorpusVect.

        Parameters
        ----------
        vect_filepath : string
            path to a specific file to load

        """
        if vect_filepath is not None:
            logging.info('Loading from: {}'.format(vect_filepath))
            with open(vect_filepath, 'rb') as f:
                self.df_preprocessed, self.vectorizer, self.dt_matrix = pickle.load(f)
        else:
            vect_path = os.path.join(self.histo_path,
                                     'vect_{}'.format(self.corpus_col))
            vect_file = sorted(os.listdir(vect_path))[-1]
            vect_filepath = os.path.join(vect_path, vect_file)
            print('Loading from: {}'.format(vect_filepath))
            with open(vect_filepath, 'rb') as f:
                self.df_preprocessed, self.vectorizer, self.dt_matrix = pickle.load(f)


def distance_to_description(corpus_vect, input_data):
    """Compute distance between the input text and each document of the
    'description' column.

    Parameters
    ----------
    corpus_vect : CorpusVect
        instance of the CorpusVect class
    input_data : string
        user search

    Returns
    -------
    corpus_vect.df_preprocessed : pd.DataFrame
        dataframe with the 'similarity' column containing the calculated distances

    """
    input_vect = corpus_vect.vectorizer.transform([input_data])

    cosine_similarities = cosine_similarity(input_vect,
                                            corpus_vect.dt_matrix).flatten()
    corpus_vect.df_preprocessed['similarity'] = cosine_similarities

    return corpus_vect.df_preprocessed


def distance_to_comment(corpus_vect, input_data):
    """Compute distance between the input text and each document of the
    'comment' column.

    Parameters
    ----------
    corpus_vect : CorpusVect
        instance of the CorpusVect class
    input_data : string
        user search

    Returns
    -------
    corpus_vect.df_preprocessed : pd.DataFrame
        dataframe with the 'similarity' column containing the calculated distances

    """
    corpus_vect.df_preprocessed['similarity'] = 0.

    for word in input_data.split():
        try:
            idx = corpus_vect.vectorizer.vocabulary_[word]
            dt_matrix_idx = corpus_vect.dt_matrix[:, idx].toarray() \
                                       .astype(float)[:, 0]
            count_similarity = dt_matrix_idx / dt_matrix_idx.sum()
            count_similarity[count_similarity == 0] = -1
            corpus_vect.df_preprocessed['similarity'] += count_similarity
        except KeyError:
            pass

    max_sim = corpus_vect.df_preprocessed['similarity'].max()
    min_sim = corpus_vect.df_preprocessed['similarity'].min()
    corpus_vect.df_preprocessed['similarity'] = ((corpus_vect.df_preprocessed['similarity']
                                                 - min_sim)
                                                 / (max_sim - min_sim))

    return corpus_vect.df_preprocessed
