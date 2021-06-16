import logging
import datetime

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation


def extract_topics(df, processing_params, corpus_col='corpus_lda', n_top_words=4):
    """Extract topics from a corpus of text documents.

    Parameters
    ----------
    df : pd.DataFrame
        dataframe with a corpus column
    processing_params : collections
        training parameters
    corpus_col : string
        name of the column containing the text information
    n_top_words : int
        number of top words of each topic to return

    Returns
    -------
    top_words_topics : list
        list of the top words of each topic

    """
    # Create vectorizer & dt_matrix from corpus
    (vectorizer,
     dt_matrix,
     feature_names) = vectorize_corpus(df, processing_params, corpus_col)

    # Train LDA
    lda = train(vectorizer, dt_matrix, processing_params)

    # Get top words of each topic
    top_words_topics = get_top_words_topics(lda, feature_names, n_top_words)

    return top_words_topics


def vectorize_corpus(df, vect_params, corpus_col='corpus_lda'):
    """Create and fit a CountVectorizer.

    Parameters
    ----------
    df : pd.DataFrame
        dataframe with a corpus column
    vect_params : configuration.data.ProcessingParameters
        vectorization parameters recorded in conf/data/processing_conf.yml
    corpus_col : string
        name of the column containing the text information

    Returns
    -------
    vectorizer : CountVectorizer
        vectorizer fitted to a corpus of text documents
    dt_matrix : Document-term matrix
        document-term matrix of the corpus text documents
    feature_names : list
        list of the words (columns) of the dt_matrix

    """
    logging.info('Vectorizing corpus')
    corpus = df[corpus_col].values.tolist()

    # Create vectorizer
    strip_accents = vect_params.strip_accents
    lowercase = vect_params.lowercase
    max_df = vect_params.max_df
    min_df = vect_params.min_df
    ngram_range = vect_params.ngram_range

    vectorizer = CountVectorizer(strip_accents=strip_accents,
                                 lowercase=lowercase, max_df=max_df,
                                 min_df=min_df, ngram_range=ngram_range)

    vectorizer = vectorizer.fit(corpus)
    feature_names = vectorizer.get_feature_names()

    # Create document-term matrix
    dt_matrix = vectorizer.transform(corpus)

    return vectorizer, dt_matrix, feature_names


def train(vectorizer, dt_matrix, lda_params):
    """Train a LatentDirichletAllocation.

    Parameters
    ----------
    vectorizer : CountVectorizer
        vectorizer fitted to a corpus of text documents
    dt_matrix : array of floats
        document-term matrix of the corpus text documents
    lda_params : configuration.data.ProcessingParameters
        lda parameters recorded in conf/data/processing_conf.yml

    Returns
    -------
    lda : LatentDirichletAllocation
        lda fitted to a dt_matrix

    """
    logging.info('Training LDA')
    start_time = datetime.datetime.now()
    max_iter = lda_params.max_iter
    evaluate_every = lda_params.evaluate_every
    perp_tol = lda_params.perp_tol
    n_components = lda_params.n_components
    learning_method = lda_params.learning_method
    random_state = lda_params.random_state

    lda = LatentDirichletAllocation(max_iter=max_iter,
                                    evaluate_every=evaluate_every,
                                    perp_tol=perp_tol,
                                    n_components=n_components,
                                    learning_method=learning_method,
                                    random_state=random_state)
    lda.fit(dt_matrix)

    training_time = round((datetime.datetime.now() - start_time).total_seconds())
    logging.info('LDA training time: {}'.format(training_time))

    return lda


def get_top_words_topics(model, feature_names, n_top_words):
    """Get the most frequent words of each topic.

    Parameters
    ----------
    model : LatentDirichletAllocation
        lda fitted to a dt_matrix
    feature_names : list
        list of the words (columns) of the dt_matrix
    n_top_words : int
        number of top words of each topic to return

    Returns
    -------
    top_words_topics : list
        list of the top words of each topic

    """
    logging.info('Getting top words of each topic')
    top_words_topics = []

    for topic_idx, topic in enumerate(model.components_):
        top_words = [feature_names[i]
                     for i in topic.argsort()[:-n_top_words-1:-1]]
        top_words_topics.append(top_words)

    return top_words_topics


def get_top_words_corpus(df, corpus_col='corpus_lda', n_top_words=4):
    """Create the list of the top words of the corpus.

    Parameters
    ----------
    df : pd.DataFrame
        dataframe with a corpus column
    corpus_col : string
        name of the column containing the text information
    n_top_words : int
        number of top words to return

    """
    corpus = df['corpus_lda'].values.tolist()
    cv = CountVectorizer().fit(corpus)
    words_count = cv.transform(corpus).sum(axis=0)
    feature_names = cv.get_feature_names()

    return [[feature_names[i]
             for i in words_count.argsort().tolist()[0][:-n_top_words-1:-1]]]
