import os

from diaman.interface.kernel import DiamanKernel
from diaman.domain import report


description_vect_path = os.path.join(os.environ['BIN'], 'test', 'resources',
                                     'vect_DESCR_ORDER_20191112_1405.pkl')
comment_vect_path = os.path.join(os.environ['BIN'], 'test', 'resources',
                                 'vect_COMMENT_20191112_1405.pkl')


""" ----------------------------------------------------------------------------
----------------------------- GET MATCHING REPORTS -----------------------------
---------------------------------------------------------------------------- """


def test_get_matching_reports():
    """[domain][report] Check function to get reports which correspond to the user search."""
    kernel = DiamanKernel('fr', 'STA', description_vect_path, comment_vect_path)
    user_search = 'coussin'

    df_reports = report.get_matching_reports(kernel, user_search)

    output = df_reports['similarity'][:5].tolist()
    expected_output = [0.47818181818181815, 0.4618507717676723, 0.4585066780215813,
                       0.4571725166040756, 0.45066691491439875]
    assert output == expected_output


""" ----------------------------------------------------------------------------
-------------------------------- FILTER REPORTS --------------------------------
---------------------------------------------------------------------------- """


def test_filter_reports():
    """[domain][report] Check filter reports"""
    kernel = DiamanKernel('fr', 'STA', description_vect_path, comment_vect_path)
    user_search = 'coussin'

    df_reports = report.get_matching_reports(kernel, user_search)

    df_reports, _, _, _ = report.filter_reports(df_reports,
                                                site_filters=['PY'],
                                                constructor_filters=['SCHULER'],
                                                equipment_filters=[])

    sites = df_reports['CODE_SITE'].unique().tolist()
    constructors = df_reports['CONSTRUCTOR'].unique().tolist()
    expected_sites = ['PY']
    expected_constructors = ['SCHULER']
    assert sites == expected_sites
    assert constructors == expected_constructors


def test_get_filter_mask():
    """[domain][report] Check get mask of the 'filter_col'."""
    kernel = DiamanKernel('fr', 'STA', description_vect_path, comment_vect_path)
    user_search = 'coussin'

    df_reports = report.get_matching_reports(kernel, user_search)
    site_mask = report.get_filter_mask(df_reports, 'CODE_SITE', ['MU'])[:5]

    expected_output = [False, False, False, False, True]
    assert site_mask.tolist() == expected_output


def test_get_matching_entities():
    """[domain][report] Check get unique values of the 'filter_col' column of
    the filtered dataframe."""
    kernel = DiamanKernel('fr', 'STA', description_vect_path, comment_vect_path)
    user_search = 'coussin'

    df_reports = report.get_matching_reports(kernel, user_search)
    matching_constructors = report.get_matching_entities(df_reports, 'CONSTRUCTOR')

    expected_matching_constructors = ['FAGOR', 'SCHULER', 'UNKNOWN']
    assert matching_constructors == expected_matching_constructors


""" ----------------------------------------------------------------------------
--------------------------------- SORT REPORTS ---------------------------------
---------------------------------------------------------------------------- """


def test_compute_detail_level():
    """[domain][report] Check the level of detail calculation."""
    kernel = DiamanKernel('fr', 'STA', description_vect_path, comment_vect_path)
    user_search = 'coussin'

    df_reports = report.get_matching_reports(kernel, user_search)

    df_reports, _, _, _ = report.filter_reports(df_reports,
                                                site_filters=['MU'],
                                                constructor_filters=[],
                                                equipment_filters=[])

    df_reports = report.compute_detail_level(df_reports)

    detail_level = list(df_reports['detail_level'].sort_values(ascending=False)[:5])
    expected_output = [1.0, 0.90625, 0.46875, 0.390625, 0.296875]
    assert detail_level == expected_output


def test_calculate_max_detail_level():
    """[domain][report] Check the max detail level calculation."""
    kernel = DiamanKernel('fr', 'STA', description_vect_path, comment_vect_path)
    user_search = 'coussin'

    df_reports = report.get_matching_reports(kernel, user_search)

    df_reports, _, _, _ = report.filter_reports(df_reports,
                                                site_filters=['MU'],
                                                constructor_filters=[],
                                                equipment_filters=[])

    corpus = df_reports['corpus'].values.tolist()

    max_detail_level = report.calculate_max_detail_level(corpus)
    assert max_detail_level == 64
