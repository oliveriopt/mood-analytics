import unittest
import tests.lei.test_cons as test_cons
from lei.src.read_lei.read_transform_files import ParserJSON


class TestTakePath(unittest.TestCase):

    def setup(self):
        mock_dict = test_cons.lei_test
        other_ent_names_tuple = (4,
                                 [['001GPB6A9XPE8XJICC14', 'Jennison 20/20 Focus Fund'],
                                  ['001GPB6A9XPE8XJICC14', 'Prudential 20/20 Focus Fund'],
                                  ['001GPB6A9XPE8XJICC14', 'Prudential 20/20 Fund'],
                                  ['001GPB6A9XPE8XJICC14', 'Prudential Jennison 20/20 Focus Fund']])
        test_other_add = ['001GPB6A9XPE8XJICC14',
                          '27 GERRARD ROADIKOYI',
                          'LAGOS',
                          'NG-LA',
                          'NG',
                          '23401']

        mock_dict_rr = test_cons.rr_test

        return mock_dict, other_ent_names_tuple, test_other_add, mock_dict_rr

    def teardown(self, mock_dict, other_ent_names_tuple, test_other_add, mock_dict_rr):
        del mock_dict, other_ent_names_tuple, test_other_add, mock_dict_rr

    def test_parser_lei_info(self):
        mock_dict, other_ent_names_tuple, test_other_add, mock_dict_rr = TestTakePath.setup(self)

        self.assertEqual(mock_dict['records'][0]['LEI']["$"], ParserJSON.read_lei(mock_dict))
        self.assertEqual(mock_dict['records'][0]["Entity"]["LegalName"]["$"],
                         ParserJSON.take_basic_information(mock_dict, ["records", "Entity", "LegalName"]))

        self.assertEqual(mock_dict['records'][0]["Entity"]["EntityStatus"]["$"],
                         ParserJSON.take_basic_information(mock_dict, ["records", "Entity", "EntityStatus"]))

        self.assertEqual(other_ent_names_tuple, ParserJSON.append_other_entity_names(mock_dict, []))
        self.assertEqual(test_other_add, ParserJSON.insert_other_address(mock_dict, 0))
        self.assertEqual("245 summer street ", ParserJSON.take_address(mock_dict, "LegalAddress"))
        self.assertEqual("Boston", ParserJSON.take_region_country_postal_code(mock_dict, "LegalAddress", "City"))
        self.assertEqual("US-MA",
                         ParserJSON.take_region_country_postal_code(mock_dict, "LegalAddress", "Region"))
        self.assertEqual("US", ParserJSON.take_region_country_postal_code(mock_dict, "LegalAddress", "Country"))
        self.assertEqual("02110", ParserJSON.take_region_country_postal_code(mock_dict, "LegalAddress", "PostalCode"))

        self.assertEqual("2012-11-29T16:33:00.000Z", ParserJSON.take_basic_information(mock_dict,
                                                                                       ["records", 'Registration',
                                                                                        "InitialRegistrationDate"]))
        self.assertEqual("ISSUED", ParserJSON.take_basic_information(mock_dict, ["records", 'Registration',
                                                                                 "RegistrationStatus"]))
        self.assertEqual("2020-06-14T10:17:00.000Z",
                         ParserJSON.take_basic_information(mock_dict, ["records", 'Registration',
                                                                       "NextRenewalDate"]))
        self.assertEqual("FULLY_CORROBORATED", ParserJSON.take_basic_information(mock_dict, ["records", 'Registration',
                                                                                             "ValidationSources"]))
        self.teardown(mock_dict, other_ent_names_tuple, test_other_add, mock_dict_rr)

    def test_parser_rr_info(self):
        mock_dict, other_ent_names_tuple, test_other_add, mock_dict_rr = TestTakePath.setup(self)
        self.assertEqual(mock_dict['records'][0]['LEI']["$"], ParserJSON.take_basic_information_rr(mock_dict_rr,
                                                                                                   ["relations",
                                                                                                    "RelationshipRecord",
                                                                                                    "Relationship",
                                                                                                    "StartNode",
                                                                                                    "NodeID"]))
        self.assertEqual("C7J4FOV6ELAVE39B7M82", ParserJSON.take_basic_information_rr(mock_dict_rr,
                                                                                      ["relations",
                                                                                       "RelationshipRecord",
                                                                                       "Relationship",
                                                                                       "EndNode", "NodeID"]))
        self.assertEqual("IS_DIRECTLY_CONSOLIDATED_BY",
                         ParserJSON.take_basic_information_rr(mock_dict_rr, ["relations", "RelationshipRecord",
                                                                             "Relationship",
                                                                             "RelationshipType"]))
        self.assertEqual("ACTIVE", ParserJSON.take_basic_information_rr(mock_dict_rr,
                                                                        ["relations", "RelationshipRecord",
                                                                         "Relationship", "RelationshipStatus"]))
        self.assertEqual("2012-10-10T12:35:00.000Z", ParserJSON.take_basic_information_rr(mock_dict_rr, ["relations",
                                                                                                         "RelationshipRecord",
                                                                                                         "Registration",
                                                                                                         "InitialRegistrationDate"]))
        self.assertEqual("2018-04-12T21:12:00.000Z", ParserJSON.take_basic_information_rr(mock_dict_rr,
                                                                                          ["relations",
                                                                                           "RelationshipRecord",
                                                                                           "Registration",
                                                                                           "LastUpdateDate"]))
        self.assertEqual("FULLY_CORROBORATED", ParserJSON.take_basic_information_rr(mock_dict_rr,
                                                                                    ["relations",
                                                                                     "RelationshipRecord",
                                                                                     "Registration",
                                                                                     "ValidationSources"]))
        self.teardown(mock_dict, other_ent_names_tuple, test_other_add, mock_dict_rr)
