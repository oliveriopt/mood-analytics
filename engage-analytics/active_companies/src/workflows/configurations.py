"""
Script that deals with different configurations for pipeline like parameters
"""


class Parameters:

    @staticmethod
    def split(all_parameters: dict, levels: list) -> dict:
        """
        Split parameter in different levels
        :param all_parameters: dict with all parameters with keys like key_levels
        :param levels: list with all the levels presents
        :return: dict with separated dicts
        """

        dict_with_level = {}

        for key in all_parameters.keys():
            # check the code
            split_number = key.rfind("_")
            keyword = key[split_number + 1:]
            if keyword in levels:
                code_name = key[:split_number]
            else:
                code_name = key
                keyword = 'common'

            if keyword not in dict_with_level.keys():
                dict_with_level[keyword] = {}

            dict_with_level[keyword][code_name] = all_parameters[key]

        return dict_with_level

    @staticmethod
    def split_by_sources(all_parameters: dict, sources: list ) -> dict:
        """
        Split parameter by different sources
        All keys should be source_table or source_column_names
        :param all_parameters: dict with all parameters with keys like source_keys
        :param sources: list with all levels present
        :return: dict with separated dicts
        """
        dict_with_sources = {}

        for key in all_parameters.keys():

            code_source = key.replace("_table", "")
            code_source = code_source.replace("_columns_names", "")
            # check the source
            if code_source in sources:
                keyword = code_source
            else:
                keyword = 'common'

            if keyword not in dict_with_sources.keys():
                dict_with_sources[keyword] = {}

            dict_with_sources[keyword][key] = all_parameters[key]
        return dict_with_sources