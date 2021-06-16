import logging
from pyspark.sql import functions as F

from diaman.configuration.data import DataConfig
from diaman.domain.vectorizer import CorpusVect


def run(spark_session, standard_data_path):
    """Create, train & save the main objects of the application, which can
    operate on a corpus of text documents.

    Parameters
    ----------
    standard_data_path : string
        path to the hdfs standard data directory

    """
    logging.info('===========================================================')
    logging.info('Starting training pipeline')

    # Configurations
    data_config = DataConfig()

    # Load raw compas reports from the gpfs repository & select only the useful cols
    df = spark_session.read.parquet(standard_data_path)
    df = df.filter(df["AUART"] == "ZURG") \
           .filter((df["KTEXT"].isNotNull()) &
                   (df["COMMENTAIRE"].isNotNull())) \
           .select([col for col, _ in data_config.gmt_columns.items()]) \
           .toDF(*[new_col for _, new_col in data_config.gmt_columns.items()]) \
           .withColumn("DURA_EQUI", F.col("DURA_EQUI").cast("float") * 60) \
           .withColumn("CONSTRUCTOR",
                       F.when(F.col("CONSTRUCTOR") != "", F.upper(F.col("CONSTRUCTOR")))
                       .otherwise("UNKNOWN")) \
           .withColumn("RATING", F.lit(-1)) \
           .distinct()

    df.persist()
    logging.info(f"Total number of reports used for the train: {df.count()}")

    # Train models for each tuple (language, shop)
    for language in data_config.indus_languages:
        for code_shop in data_config.get_shops(language):
            df_language_shop = df.filter(df["CODE_SITE"].isin(data_config.get_sites(language))) \
                                 .filter(df["CODE_SHOP"] == code_shop.upper()) \
                                 .toPandas()
            # Add spare part to the COMMENT
            df_language_shop['COMMENT'] += df_language_shop['COMPONENTS'] \
                .apply(lambda components: ' ' + ' '.join([component[0]
                                                          for component in components]))
            make_train_language_shop(df_language_shop, language, code_shop)

    logging.info('*** Training pipeline finished ***')


def make_train_language_shop(df, language, code_shop, remove_numbers=False,
                             remove_small_words=False):
    """Train CorpusVect objects for a specific tuple (language, shop).

    Parameters
    ----------
    df : pd.DataFrame
        dataframe with the reports corresponding to the tuple (language, code_shop)
    language : string
        language of the reports
    code_shop : string
        code_shop of the plant ('emb', 'fer' ...)
    remove_numbers : bool
        True if numbers are removed
    remove_small_words : bool
        True if small words are removed

    """
    logging.info('Training for the {} language and the {} shop'.format(language, code_shop))

    # Load specific language data configuration
    data_config_language = DataConfig(language)

    # Create corpus_vect objects
    for corpus_col in ['DESCR_ORDER', 'COMMENT']:
        logging.info('Creating {}_vect'.format(corpus_col))
        corpus_vect = CorpusVect(language, code_shop, corpus_col)
        corpus_vect.preprocess_corpus(df, data_config_language.stopwords,
                                      data_config_language.word_dict,
                                      remove_numbers, remove_small_words)
        corpus_vect.create_vectorizer()
        corpus_vect.save()
