import logging
import unicodedata
import re
import pandas as pd


def preprocess_corpus(df, corpus_col, stopwords, word_dict,
                      remove_numbers=False, remove_small_words=False):
    """Make pipeline to preprocess text.

    Parameters
    ----------
    df : pd.DataFrame
        input dataframe with the corpus_col to preprocess
    corpus_col : string
        name of the column containing the text information
    stopwords : list of strings
        list containing the stopwords
    word_dict : dict
        personalized correction dictionnary
    remove_numbers : bool
        True if numbers are removed
    remove_small_words : bool
        True if small words are removed

    Returns
    -------
    corpus : pd.Series
        One-dimensional ndarray containing the result of the corpus_col
        preprocessing

    """
    logging.info("Preprocessing the '{}' column".format(corpus_col))

    # Perform conventional text processing
    corpus = refine_corpus(df, corpus_col, stopwords,
                           remove_numbers, remove_small_words)

    # Correct the words of the corpus
    corpus = correct_words(corpus, word_dict)

    return corpus


def refine_corpus(df, corpus_col, stopwords, remove_numbers, remove_small_words):
    """Perform conventional text processing.

    Parameters
    ----------
    df : pd.DataFrame
        input dataframe with the corpus_col to preprocess
    corpus_col : string
        name of the column containing the text information
    stopwords : list
        list containing the words to remove from the corpus
    remove_numbers : bool
        True if numbers are removed
    remove_small_words : bool
        True if small words are removed

    Returns
    -------
    corpus : pd.Series
        One-dimensional ndarray containing the result of the corpus_col
        preprocessing

    """
    logging.info('Performing conventional text processing')
    if ((isinstance(df, str)) & (corpus_col == 'user_input')):
        df = pd.DataFrame(columns=[corpus_col], data=[df], dtype=str)
    corpus = df[corpus_col]

    # Lower case
    corpus = corpus.apply(lambda x: x.lower())

    # Normalize
    corpus = corpus.apply(lambda x: unicodedata.normalize('NFKD', x)
                                               .encode('ascii', 'ignore'))

    # Decode utf-8
    corpus = corpus.str.decode('utf-8')

    # Remove comment header
    if corpus_col == 'COMMENT':
        corpus = corpus.apply(lambda x: remove_comment_header(x))

    # Tokenize, remove punctuation & stopwords
    corpus = corpus.apply(lambda x: re.findall('\w+(?:[\?\-\"_]\w+)*', x, re.M+re.DOTALL)) \
        .apply(lambda x: [w for w in x if w not in stopwords]) \
        .apply(lambda x: " ".join(x))

    # Remove numbers
    if remove_numbers:
        corpus = corpus.apply(lambda x: ''.join(e for e in x
                                                if e not in "0123456789/_->()"))

    # Remove small words
    if remove_small_words:
        corpus = corpus.apply(lambda x: ' '.join(e for e in x.split(" ")
                                                 if len(e) >= 4))

    return corpus


def remove_comment_header(comment):
    """Remove the header from the 'comment' column, which contains the name,
    the id and the number of the Maintenance Agent.

    Parameters
    ----------
    comment : string
        comment from which to remove the header

    """
    # First regex with the telephone number
    regex_1 = r"\d{2}\.\d{2}\.\d{4}.{10,40}\([a-z]\d{6}\) tel. \d{2,10} \d{2,10}"
    comment = ''.join(e for e in re.compile(regex_1).split(comment))

    # Second regex with another type of telephone number
    regex_1 = r"\d{2}\.\d{2}\.\d{4}.{10,40}\([a-z]\d{6}\) tel. \d{2,10}"
    comment = ''.join(e for e in re.compile(regex_1).split(comment))

    # Third regex without the telephone number
    regex_2 = r"\d{2}\.\d{2}\.\d{4}.{10,40}\([a-z]\d{6}\)"
    comment = ''.join(e for e in re.compile(regex_2).split(comment))

    return comment


def correct_words(corpus, word_dict):
    """Correct the words of the corpus.

    Parameters
    ----------
    corpus : pd.Series
        One-dimensional ndarray containing the corpus_col to preprocess
    word_dict : dict
        personalized correction dictionnary: {'true word': [words to replace]}

    Returns
    -------
    corpus : pd.Series
        One-dimensional ndarray with the corrected words

    """
    logging.info('Correcting words')
    corrected_corpus = []
    for sentence in corpus.values.tolist():
        corrected_sentence = ''
        tokenized_sentence = sentence.split(' ')
        for word in tokenized_sentence:
            for key, value in word_dict.items():
                if word in value:
                    word = key
                    break
            corrected_sentence = ' '.join([corrected_sentence, word])
        corrected_sentence = corrected_sentence.lstrip(' ')
        corrected_corpus.append(corrected_sentence)

    corpus = pd.Series(data=corrected_corpus)

    return corpus
