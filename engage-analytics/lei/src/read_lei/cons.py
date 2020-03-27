""""
Constans that not change
"""
DATABASE_NAME = "mood_core_engage_mapping"
LEI_ENTITIES_TABLE = "entities"
LEI_OTHER_ENTITIES_NAME = "other_entities_names"
LEI_OTHER_ADRESSES = "other_address"
LEI_RELATIONSHIP_ENTITIES = "relationship_entities"
PATH_LINK_URL_LEI_FILE = 'https://leidata-preview.gleif.org/api/v2/golden-copies/publishes'
KEYS_JSON_FILE = ["data", "lei2", "full_file", "json", "url"]
HEADER_DATABASE_LEI_INFORMATION_SQL = ["lei_2", "entity_legalname", "entity_entity_status", "entity_otherentity_names",
                                       "entity_other_addresses", "entity_legal_address_firstaddressline",
                                       "entity_legal_address_city", "entity_legal_address_region",
                                       "entity_legal_address_country", "entity_legal_address_postalcode",
                                       "entity_headquarter_address_firstaddressline", "entity_headquarter_address_city",
                                       "entity_headquarter_address_region",
                                       "entity_headquarter_address_country", "entity_headquarter_address_postalcode",
                                       "registration_initial_registration_date",
                                       "registration_registration_status", "registration_next_renewal_date",
                                       "registration_validation_sources"]
HEADER_DATABASE_OTHER_ENTITIES_NAMES_SQL = ["lei_2", "other_entity_names"]
HEADER_DATABASE_OTHER_ADDRESS_SQL = ["lei_2", "other_adress_firstaddressline", "other_adress_city", "other_adress_region",
                                     "other_adress_country", "other_adress_postalcode"]
HEADER_DATABASE_RELATIONSHIP_ENTITIES_SQL = ["lei_2", "father_lei", "relationship_type", "relationship_status",
                                             "registration_initial_registration_date", "registration_last_update_date",
                                             "registration_validation_sources"]
REGISTERS_PER_FILE = 5000
PREFIX_TEMPORARY_FILE = "test_file_"
PREFIX_TEMPORARY_FILE_RR = "test_file_rr_"
FOLDER_TO_STORAGE_DATA = "/data_connection/"

FORMAT_DECODE = "utf-8"