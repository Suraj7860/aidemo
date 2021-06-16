import numpy as np

from . import preprocessing


""" ----------------------------------------------------------------------------
----------------------------- GET MATCHING REPORTS -----------------------------
---------------------------------------------------------------------------- """


def get_matching_reports(kernel, search):
    """Get reports which correspond to the user search.

    Parameters
    ----------
    kernel : interface.kernel.AppKernel
        instance
    search : string
        user search

    Returns
    -------
    df_reports : pd.DataFrame
        dataframe with the matching reports, which are filtered and sorted

    """
    # User search preprocessing
    input_data = preprocessing.preprocess_corpus(search, 'user_input',
                                                 kernel.stopwords,
                                                 kernel.word_dict)
    input_data = input_data[0]

    # Compute the distances between the input and the text columns
    kernel.description_vect.compute_distance(input_data)
    kernel.comment_vect.compute_distance(input_data)

    # Create df_reports
    df_reports = kernel.comment_vect.df_preprocessed \
        .rename(columns={'similarity': 'sim_comment'})
    df_reports['sim_failure'] = kernel.description_vect.df_preprocessed['similarity']

    # Compute the final similarity
    w = kernel.slider_sim_weight
    df_reports['similarity'] = ((1.-w) * df_reports['sim_failure']
                                + w * df_reports['sim_comment']) / 2

    df_reports = df_reports \
        .loc[df_reports['similarity'] > 0] \
        .sort_values(by='similarity', ascending=False) \
        .drop(columns=['sim_comment', 'sim_failure']) \
        .reset_index(drop=True)

    if len(df_reports) == 0:
        raise ValueError(('No reports found matching the search, '
                          'please modify your search.'))
    else:
        return df_reports


""" ----------------------------------------------------------------------------
-------------------------------- FILTER REPORTS --------------------------------
---------------------------------------------------------------------------- """


def filter_reports(df_reports, site_filters, constructor_filters,
                   equipment_filters):
    """Filter reports given the selected filters.

    Parameters
    ----------
    df_reports : pd.DataFrame
        dataframe with the matching reports
    site_filters : list
        sites selected by the user
    constructor_filters : list
        constructors selected by the user
    equipment_filters : list
        equipments selected by the user

    Returns
    -------
    df_filtered : pd.DataFrame
        dataframe filtered given the selected filters
    matching_sites : list
        unique values of the 'site' column of the filtered dataframe
    matching_constructors : list
        unique values of the 'constructor' column of the filtered dataframe
    matching_equipments : list
        unique values of the 'description_technical_object' column of the
        filtered dataframe

    """
    # Get filter masks
    site_mask = get_filter_mask(df_reports, 'CODE_SITE',
                                site_filters)
    constructor_mask = get_filter_mask(df_reports, 'CONSTRUCTOR',
                                       constructor_filters)
    equipment_mask = get_filter_mask(df_reports, 'DESCR_EQUI',
                                     equipment_filters)

    mask = site_mask & constructor_mask & equipment_mask
    df_filtered = df_reports[mask]

    matching_sites = get_matching_entities(df_filtered, 'CODE_SITE')
    matching_constructors = get_matching_entities(df_filtered, 'CONSTRUCTOR')
    matching_equipments = get_matching_entities(df_filtered,
                                                'DESCR_EQUI')

    return df_filtered, matching_sites, matching_constructors, matching_equipments


def get_filter_mask(df_reports, filter_col, filters):
    """Get mask of the 'filter_col' column given the selected filters.

    Parameters
    ----------
    df_reports : pd.DataFrame
        dataframe with the matching reports
    filter_col : string
        column on which to filter
    filters : list
        list of the 'filter_col' values selected by the user

    """
    if len(filters) == 0:
        return (1 - df_reports[filter_col].isna()).astype(bool)
    else:
        return df_reports[filter_col].isin(filters)


def get_matching_entities(df_filtered, filter_col):
    """Get unique values of the 'filter_col' column of the filtered dataframe.

    Parameters
    ----------
    df_filtered : pd.DataFrame
        dataframe filtered given the selected filters
    filter_col :
        column used to filter

    """
    return df_filtered[filter_col].drop_duplicates() \
                                  .sort_values(ascending=True) \
                                  .tolist()


""" ---------------------------------------------------------------------------
--------------------------------- SORT REPORTS --------------------------------
--------------------------------------------------------------------------- """


def sort_reports(df_reports, slider_coeff_detail):
    """Sort the reports according to the similarity score and the level of
    detail of the comment.

    Parameters
    ----------
    df_reports : pd.DataFrame
        dataframe with the filtered reports
    slider_coeff_detail : float
        weight given at the level of detail

    """
    # Evaluate the level of detail of each document of the corpus
    df_reports = compute_detail_level(df_reports)

    # Get the particular values
    max_similarity = df_reports['similarity'].max()
    min_similarity = df_reports['similarity'].min()

    max_detail_level = df_reports['detail_level'].max()
    min_detail_level = df_reports['detail_level'].min()

    # Compute the sort
    df_reports['sorting_score'] = ((1. - slider_coeff_detail)
                                   * (df_reports['similarity'] - min_similarity)
                                   / (max_similarity - min_similarity)
                                   + slider_coeff_detail
                                   * (df_reports['detail_level'] - min_detail_level)
                                   / (max_detail_level - min_detail_level))

    return df_reports.sort_values(by='sorting_score', ascending=False) \
                     .reset_index(drop=True)


def compute_detail_level(df_reports):
    """Evaluate the level of detail of each document of the corpus.

    Parameters
    ----------
    df_reports : pd.DataFrame
        dataframe with the filtered reports

    Returns
    -------
    df_reports : pd.DataFrame
        dataframe with the 'detail_level' column containing the level of detail
        of each comment

    """
    # Create corpus variable
    if isinstance(df_reports['corpus'], str):
        corpus = [df_reports['corpus']]
    else:
        corpus = df_reports['corpus'].values.tolist()

    # Calculate max_detail_level
    max_detail_level = calculate_max_detail_level(corpus)

    # Evaluate the level of detail of each document
    detail_level = []
    for text in corpus:
        words_list = list(set(text.split()))  # list of unique words
        detail_level.append(float(len(words_list)) / float(max_detail_level))

    df_reports['detail_level'] = np.array(detail_level)
    return df_reports


def calculate_max_detail_level(corpus):
    """Calculate the max detail level of the documents of the corpus.

    Parameters
    ----------
    corpus: list
        list containing the text documents

    Returns
    -------
    max_detail_level : int
        max level of detail of all the documents

    """
    max_detail_level = 0
    for text in corpus:
        words_list = list(set(text.split()))  # list of unique words
        if len(words_list) > max_detail_level:
            max_detail_level = len(words_list)

    return max_detail_level
