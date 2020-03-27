import json


class ParserJSON:

    @staticmethod
    def take_basic_information(dict: dict, fields_elements: list) -> list:
        """
        Take information for json file of entity
        :param dict : dictionary from json file
        :param fields_elements: element to extract from json file
        return add: string with the information
        """
        add = "NOT " + fields_elements[1].upper()

        if fields_elements[2] in dict[fields_elements[0]][0][fields_elements[1]]:
            add = (dict[fields_elements[0]][0][fields_elements[1]][fields_elements[2]]["$"])

        return add

    @staticmethod
    def take_address(dict: dict, type_add: str) -> str:
        """
        Take information for json file for address
        :param dict : dictionary from json file
        :param type_add: type of addrese (Headquarter or Legal Address)
        return add: string with the information
        """
        add = ""
        if "FirstAddressLine" in dict['records'][0]['Entity'][type_add]:
            add = dict['records'][0]['Entity'][type_add]["FirstAddressLine"]["$"] + " "

        if "AdditionalAddressLine" in dict['records'][0]['Entity'][type_add]:
            number = len(dict['records'][0]['Entity'][type_add]["AdditionalAddressLine"])
            if number == 1:
                add = add + dict['records'][0]['Entity'][type_add]["AdditionalAddressLine"]["$"]
            if number > 1:
                for j in range(number):
                    add = add + dict['records'][0]['Entity'][type_add]["AdditionalAddressLine"][j]["$"]

        return add.replace("\"", "").replace("'", "").replace("\\", "").lower()

    @staticmethod
    def take_region_country_postal_code(dict: dict, type_add: str, type: str) -> str:
        """
        Take information for json file for address
        :param dict : dictionary from json file
        :param type_add: type of addrese (Headquarter or Legal Address)
        return add: string with the information
        """
        add = ""
        if type in dict['records'][0]['Entity'][type_add]:
            add = dict['records'][0]['Entity'][type_add][type]["$"]
        else:
            add = "NOT " + type.upper() + " INFORMATION"
        return add

    @staticmethod
    def take_info_other_address(dict, k: int, type_address: str) -> str:

        if type_address in dict['records'][0]['Entity']["OtherAddresses"]["OtherAddress"][k]:
            field = dict['records'][0]['Entity']["OtherAddresses"]["OtherAddress"][k][type_address]["$"]
        else:
            field = ""

        return field

    @staticmethod
    def insert_other_address(dict: dict, k: int) -> list:
        """
        Replace special characters
        :param dict: dictionay of the information from json file
        return string: string already replaced
        """
        lei = ""
        first_add = ""
        city = ""
        region = ""
        country = ""
        postalcode = ""
        lei = dict['records'][0]['LEI']["$"]
        if "FirstAddressLine" in dict['records'][0]['Entity']["OtherAddresses"]["OtherAddress"][k]:
            first_add = dict['records'][0]['Entity']["OtherAddresses"]["OtherAddress"][k]["FirstAddressLine"]["$"]
        else:
            first_add = ""

        if "AdditionalAddressLine" in dict['records'][0]['Entity']["OtherAddresses"]["OtherAddress"][k]:
            number = len(dict['records'][0]['Entity']["OtherAddresses"]["OtherAddress"][k]["AdditionalAddressLine"])
            if number == 1:
                first_add = first_add + \
                            dict['records'][0]['Entity']["OtherAddresses"]["OtherAddress"][k]["AdditionalAddressLine"][
                                "$"]
            if number > 1:
                for j in range(number):
                    first_add = first_add + dict['records'][0]['Entity']["OtherAddresses"]["OtherAddress"][k][
                        "AdditionalAddressLine"][j]["$"]

        city = ParserJSON.take_info_other_address(dict, k, "City")
        region = ParserJSON.take_info_other_address(dict, k, "Region")
        country = ParserJSON.take_info_other_address(dict, k, "Country")
        postalcode = ParserJSON.take_info_other_address(dict, k, "PostalCode")

        l = [lei, first_add, city, region, country, postalcode]

        return l

    @staticmethod
    def replace_special_character(string: str) -> str:
        """
        Replace special characters
        :param string: string to replace specials characters
        return string: string already replaced
        """

        return string.replace("\"", "").replace("\\", "").replace("'", "").lower()

    @staticmethod
    def append_other_entity_names(dict, other_names):

        entity_otherentity_names = len(dict['records'][0]['Entity']["OtherEntityNames"]["OtherEntityName"])
        if entity_otherentity_names > 0:
            for i in range(entity_otherentity_names):
                other_names.append([dict['records'][0]['LEI']["$"],
                                    dict['records'][0]['Entity']["OtherEntityNames"]["OtherEntityName"][i][
                                        "$"]])

        return entity_otherentity_names, other_names

    @staticmethod
    def entity_address(dict, type_address: str) -> tuple:

        entity_firstaddressline = ParserJSON.replace_special_character(
            ParserJSON.take_address(dict, type_address))
        entity_city = ParserJSON.replace_special_character(
            ParserJSON.take_region_country_postal_code(dict, type_address, "City"))
        entity_region = ParserJSON.replace_special_character(
            ParserJSON.take_region_country_postal_code(dict, type_address, "Region"))
        entity_country = ParserJSON.replace_special_character(
            ParserJSON.take_region_country_postal_code(dict, type_address, "Country"))
        entity_postalcode = ParserJSON.replace_special_character(
            ParserJSON.take_region_country_postal_code(dict, type_address, "PostalCode"))

        return entity_firstaddressline, entity_city, \
               entity_region, entity_country, entity_postalcode

    @staticmethod
    def read_registration_date(dict) -> tuple:

        registration_initial_registration_date = ParserJSON.take_basic_information(dict,
                                                                                   ["records", 'Registration',
                                                                                    "InitialRegistrationDate"])
        registration_registration_status = ParserJSON.take_basic_information(dict, ["records", 'Registration',
                                                                                    "RegistrationStatus"])
        registration_next_renewal_date = ParserJSON.take_basic_information(dict, ["records", 'Registration',
                                                                                  "NextRenewalDate"])
        registration_validation_sources = ParserJSON.take_basic_information(dict, ["records", 'Registration',
                                                                                   "ValidationSources"])
        return registration_initial_registration_date, registration_registration_status, \
               registration_next_renewal_date, registration_validation_sources

    @staticmethod
    def read_lei(dict) -> str:

        if "LEI" in dict['records'][0]:
            lei = dict['records'][0]['LEI']["$"]
        else:
            lei = "NOT LEI"

        return lei

    @staticmethod
    def read_transform_json_file(dest_folder: str) -> tuple:
        """
        Take information for json file
        :param dict : dictionary from json file
        :param fields_elements: element to extract from json file
        return add: string with the information
        """

        entity = []
        other_names = []
        other_add = []
        with open(dest_folder, 'r', encoding="utf-8") as json_file:
            for line in json_file:
                dict = json.loads(line)

                lei = ParserJSON.read_lei(dict)

                entity_legalname = ParserJSON.take_basic_information(dict, ["records", "Entity", "LegalName"])

                entity_entity_status = ParserJSON.take_basic_information(dict, ["records", "Entity", "EntityStatus"])

                if "OtherEntityNames" in dict['records'][0]['Entity']:
                    entity_otherentity_names, other_names = ParserJSON.append_other_entity_names(dict, other_names)
                else:
                    entity_otherentity_names = 0

                if "OtherAddresses" in dict['records'][0]['Entity']:
                    entity_other_addresses = len(dict['records'][0]['Entity']["OtherAddresses"]["OtherAddress"])
                    for m in range(0, entity_other_addresses):
                        if entity_other_addresses >= 1:
                            other_add.append(ParserJSON.insert_other_address(dict, m))
                else:
                    entity_other_addresses = 0

                entity_legal_address_firstaddressline, entity_legal_address_city, \
                entity_legal_address_region, entity_legal_address_country, \
                entity_legal_address_postalcode = ParserJSON.entity_address(dict, "LegalAddress")

                entity_headquarter_address_firstaddressline, entity_headquarter_address_city, \
                entity_headquarter_address_region, entity_headquarter_address_country, \
                entity_headquarter_address_postalcode = ParserJSON.entity_address(dict, "HeadquartersAddress")

                registration_initial_registration_date, registration_registration_status, registration_next_renewal_date, \
                registration_validation_sources = ParserJSON.read_registration_date(dict)

                entity.append(
                    [lei, entity_legalname, entity_entity_status, entity_otherentity_names, entity_other_addresses,
                     entity_legal_address_firstaddressline,
                     entity_legal_address_city, entity_legal_address_region, entity_legal_address_country,
                     entity_legal_address_postalcode,
                     entity_headquarter_address_firstaddressline, entity_headquarter_address_city,
                     entity_headquarter_address_region,
                     entity_headquarter_address_country, entity_headquarter_address_postalcode,
                     registration_initial_registration_date,
                     registration_registration_status, registration_next_renewal_date, registration_validation_sources])

        return entity, other_names, other_add

    @staticmethod
    def take_basic_information_rr(dict, fields_elements) -> str:
        """
        Take information for json file of relationship
        :param dicte : dictionary from json file
        :param fields_elements: element to extract from json file
        return add: string with the information
        """
        add = []
        if len(fields_elements) == 4:
            if fields_elements[3] in dict[fields_elements[0]][0][fields_elements[1]][fields_elements[2]]:
                add = dict[fields_elements[0]][0][fields_elements[1]][fields_elements[2]][fields_elements[3]]["$"]
            else:
                add = "NOT " + fields_elements[3].upper()

        if len(fields_elements) == 5:
            if fields_elements[4] in dict[fields_elements[0]][0][fields_elements[1]][fields_elements[2]][
                fields_elements[3]]:
                add = dict[fields_elements[0]][0][fields_elements[1]][fields_elements[2]][fields_elements[3]][
                    fields_elements[4]]["$"]
            else:
                add = "NOT " + fields_elements[4].upper()

        return add

    @staticmethod
    def read_transform_json_file_rr(dest_folder: str) -> list:
        """
        Put information from json file into a list
        :param dest_folder : path of file
        """
        relationships = []
        with open(dest_folder, 'r', encoding="utf-8") as json_file:
            for line in json_file:
                dict_info = json.loads(line)
                lei = ParserJSON.take_basic_information_rr(dict_info,
                                                           ["relations", "RelationshipRecord", "Relationship",
                                                            "StartNode", "NodeID"])
                father_lei = ParserJSON.take_basic_information_rr(dict_info,
                                                                  ["relations", "RelationshipRecord", "Relationship",
                                                                   "EndNode", "NodeID"])
                relationship_type = ParserJSON.take_basic_information_rr(dict_info, ["relations", "RelationshipRecord",
                                                                                     "Relationship",
                                                                                     "RelationshipType"])
                relationship_status = ParserJSON.take_basic_information_rr(dict_info,
                                                                           ["relations", "RelationshipRecord",
                                                                            "Relationship", "RelationshipStatus"])
                registration_initial_registration_date = ParserJSON.take_basic_information_rr(dict_info, ["relations",
                                                                                                          "RelationshipRecord",
                                                                                                          "Registration",
                                                                                                          "InitialRegistrationDate"])
                registration_last_update_date = ParserJSON.take_basic_information_rr(dict_info,
                                                                                     ["relations", "RelationshipRecord",
                                                                                      "Registration", "LastUpdateDate"])
                registration_validation_sources = ParserJSON.take_basic_information_rr(dict_info,
                                                                                       ["relations",
                                                                                        "RelationshipRecord",
                                                                                        "Registration",
                                                                                        "ValidationSources"])
                relationships.append(
                    [lei, father_lei, relationship_type, relationship_status, registration_initial_registration_date,
                     registration_last_update_date, registration_validation_sources])

        return relationships

    @staticmethod
    def read_files(path_file: str) -> tuple:
        """
        Put information from json file into a list
        :param path_file : path of file
        """
        entity, other_names, other_add = ParserJSON.read_transform_json_file(path_file)
        return entity, other_names, other_add

    @staticmethod
    def read_files_rr(path_file: str) -> json:
        """
        Put information from json file into a list
        :param path_file : path of file
        """
        relationships = ParserJSON.read_transform_json_file_rr(path_file)

        return relationships