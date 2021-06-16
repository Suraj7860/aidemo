import unicodedata

from diaman.domain import report, lda


def make_search(kernel, search, site_filters, constructor_filters,
                equipment_filters, n_reports=50):
    """Output the results of the comparison between the user search and the
    database reports.

    Parameters
    ----------
    kernel : interface.kernel.AppKernel
        instance containing the main objects of the application
    search : string
        user search
    site_filters : list
        sites selected by the user
    constructor_filters : list
        constructors selected by the user
    equipment_filters : list
        equipments selected by the user
    n_reports : int
        number of reports to return

    Returns
    -------
    df_reports : pd.DataFrame
        dataframe with the matching reports, which are filtered and sorted
    matching_sites : list
        unique values of the 'site' column of the filtered dataframe
    matching_constructors : list
        unique values of the 'constructor' column of the filtered dataframe
    matching_equipments : list
        unique values of the 'description_technical_object' column of the
        filtered dataframe

    """
    # Get the reports which correspond to the user search
    df_reports = report.get_matching_reports(kernel, search)

    # Filter the reports given the selected filters
    (df_reports,
     matching_sites,
     matching_constructors,
     matching_equipments) = report.filter_reports(df_reports,
                                                  site_filters,
                                                  constructor_filters,
                                                  equipment_filters)

    # Sort the reports according to the similarity score and the level of
    # detail of the comment
    df_reports = report.sort_reports(df_reports, kernel.slider_coeff_detail)

    return (df_reports.head(n_reports), matching_sites,
            matching_constructors, matching_equipments)


def make_refine(kernel, search):
    """Output the results of the topics extraction from the matching reports.

    Parameters
    ----------
    kernel : interface.kernel.AppKernel
        instance containing the main objects of the application
    search : string
        user search

    top_words_topics : list of strings
        list containing the top words of the topics

    """
    # Get the reports which correspond to the user search
    df_reports = report.get_matching_reports(kernel, search)

    # Select only the 500 most similar reports with a similarity score > 0.05
    df_reports = df_reports[df_reports['similarity'] > 0.05] \
        .head(500) \
        .reset_index(drop=True)

    # Extract the top words
    try:
        top_words_topics = lda.extract_topics(df_reports, kernel.processing_params)
    except ValueError:
        top_words_topics = lda.get_top_words_corpus(df_reports)

    # User search preprocessing
    search = unicodedata.normalize('NFKD', search) \
        .encode('ascii', 'ignore') \
        .decode('utf-8')

    # Add the search to the top_words_topics
    top_words_topics = [' '.join([search] + topic)
                        for topic in top_words_topics]

    return top_words_topics
