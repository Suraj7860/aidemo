import json

from .kernel import DiamanKernel
from ..configuration.data import DataConfig
from ..pipeline import search_pipeline


class DiamanHelp(DataConfig):
    """Instantiate kernels for each tuple (language, code_shop) and provide
    the user with the search methods.

    Attributes
    ----------
    indus_languages : list of strings
        list of the languages integrated into the industrialisation
    kernels : dict of diaman.interface.kernel.DiamanKernel
        dict containing the kernels for each tuple (language, code_shop)

    """
    def __init__(self):
        DataConfig.__init__(self)
        self._instantiate_kernels()

    def _instantiate_kernels(self):
        """Instantiate a kernel for each tuple (language, code_shop)."""
        self.kernels = {}
        for language in self.indus_languages:
            for code_shop in self.get_shops(language):
                self.kernels['{}_{}'.format(language, code_shop)] = DiamanKernel(language,
                                                                                 code_shop)

    def _get_language_if_valid_search(self, code_site, code_shop):
        """Check if the site & the shop of the user are supported in diaman &
        return the related language.

        Parameters
        ----------
        code_site : string
            user site
        code_shop : string
            user shop

        """
        # Check if the code_site is valid
        if code_site not in self.psa_sites:
            raise ValueError((f'The code_site {code_site} is not related to a PSA site. '
                              'Please enter a valid code_site.'))

        # Get the related language & check if it's in the indus perimeter
        language = self.get_language(code_site)

        if language not in self.indus_languages:
            raise ValueError((f'The language {language} is not supported by diaman at this time. '
                              'The supported languages are: {}.'
                              .format(', '.join(self.indus_languages))))

        # Check if the data is available for the code_shop
        if code_shop not in self.get_shops(language):
            raise ValueError((f'No data available for the {code_shop} shop at {code_site}. '
                              'Please choose a code_shop among: {}.'
                              .format(', '.join(self.get_shops(language)))))

        return language

    def get_search_results(self, code_site, code_shop, search, site_filters,
                           constructor_filters, equipment_filters):
        """Transform the dataframe with the matching reports into a json file
        and add the lists with the options for each filter (site, constructor,
        equipment).

        Parameters
        ----------
        code_site : string
            user site
        code_shop : string
            user shop
        search : string
            user search
        site_filters : list
            sites selected by the user
        constructor_filters : list
            constructors selected by the user
        equipment_filters : list
            equipments selected by the user

        """
        # Transform params in capital letters
        code_site = code_site.upper()
        code_shop = code_shop.upper()

        # Get language if valid search
        language = self._get_language_if_valid_search(code_site, code_shop)

        # Make search
        (df_reports,
         matching_sites,
         matching_constructors,
         matching_equipments) = search_pipeline.make_search(self.kernels['{}_{}'.format(language,
                                                                                        code_shop)],
                                                            search,
                                                            site_filters,
                                                            constructor_filters,
                                                            equipment_filters)

        # Format the entries of the final json file
        df_reports['ERDAT'] = df_reports['ERDAT'].astype(str)
        df_reports['COMMENT'] = df_reports['COMMENT'].apply(lambda x: [x])
        df_reports['OPERATION'] = df_reports['DURA_EQUI'].apply(lambda x: [{"DURA_EQUI": x}])
        df_reports['COMPONENTS'] = df_reports['COMPONENTS'] \
            .apply(lambda components: [{"MATNR": component[0], "MATL_DESC": "string",
                                        "QUANTITY": component[2]} for component in components])
        df_reports['MEDIAS'] = df_reports['MEDIAS'] \
            .apply(lambda medias: [{"DOC_URL": media[0], "DOC_TYPE": media[1]}
                                   for media in medias])

        # Create the json file
        df_reports = df_reports[self.diaman_search_cols].to_json(orient='index')
        json_reports = json.loads(df_reports)
        return {'ORDER_LIST': [json_reports[k] for k in json_reports.keys()],
                'SITES': matching_sites,
                'CONSTRUCTORS': matching_constructors,
                'EQUIPMENTS': matching_equipments}

    def get_refine_results(self, code_site, code_shop, search):
        """Transform the list with the top words of the topics related to
        the search into a json file.

        Parameters
        ----------
        code_site : string
            user site
        code_shop : string
            user shop
        search : string
            user search

        """
        # Transform params in capital letters
        code_site = code_site.upper()
        code_shop = code_shop.upper()

        # Get language if valid search
        language = self._get_language_if_valid_search(code_site, code_shop)

        # Make refine
        top_words_topics = search_pipeline.make_refine(self.kernels['{}_{}'.format(language,
                                                                                   code_shop)],
                                                       search)
        return {'top_words_topics': top_words_topics}
