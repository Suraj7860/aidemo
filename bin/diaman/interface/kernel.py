from ..configuration.data import DataConfig
from ..domain.vectorizer import CorpusVect


class DiamanKernel(object):
    """Instantiate a kernel for each tuple (language, code_shop)."""
    def __init__(self, language, code_shop,
                 description_vect_path=None, comment_vect_path=None):
        # DataConfig instance
        data_config = DataConfig(language)
        self.stopwords = data_config.stopwords
        self.word_dict = data_config.word_dict
        self.processing_params = data_config.processing_params

        # Vectorizers for the 'description' and 'comment' columns
        self.description_vect = CorpusVect(language, code_shop, 'DESCR_ORDER')
        self.description_vect.load(description_vect_path)

        self.comment_vect = CorpusVect(language, code_shop, 'COMMENT')
        self.comment_vect.load(comment_vect_path)

        # Weights used for the outputs
        self.slider_sim_weight = 0.8
        self.slider_coeff_detail = 0.2
