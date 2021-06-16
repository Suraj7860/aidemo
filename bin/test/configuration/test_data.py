from diaman.configuration.data import DataConfig


data_config = DataConfig('fr')


def test_processing_conf():
    """[conf] Check processing conf parameters."""
    nb_params = len(data_config.processing_params)
    assert nb_params == 11


def test_stopwords():
    """[conf] Check stopwords process."""
    assert len(data_config.stopwords) >= 173
    expected_output = ['defaut', 'defauts', 'def', 'df', 'dft', 'dfts', 'hs',
                       'panne', 'pannes', 'probleme', 'problemes', 'pb', 'pbs',
                       'suite', 'fait', 'bug', 'controle', 'deja']
    output = [stopword for stopword in data_config.stopwords
              if stopword in expected_output]
    assert(sorted(expected_output) == sorted(output))


def test_word_dict():
    """[conf] Check words dict process"""
    word_dict = data_config.word_dict
    assert len(word_dict) >= 331
    expected = ['abaisser', 'accelerer', 'accident', 'accordeon', 'accoster',
                'accoupler', 'accumulateur', 'acquittement', 'actemium']
    assert all(word in data_config.word_dict.keys() for word in expected)
