import unittest
import requests
import json
import lei.src.read_lei.cons as cons


class TestImportLeiFile(unittest.TestCase):

    def test_read_link(self):
        response = requests.get(cons.PATH_LINK_URL_LEI_FILE)
        var_json = json.loads(response.content.decode(cons.FORMAT_DECODE))
        assert response.ok
        assert cons.KEYS_JSON_FILE[0] in var_json
        assert cons.KEYS_JSON_FILE[1] in var_json[cons.KEYS_JSON_FILE[0]][0]
        assert cons.KEYS_JSON_FILE[2] in var_json[cons.KEYS_JSON_FILE[0]][0] \
            [cons.KEYS_JSON_FILE[1]]
        assert cons.KEYS_JSON_FILE[3] in var_json[cons.KEYS_JSON_FILE[0]][0] \
            [cons.KEYS_JSON_FILE[1]][cons.KEYS_JSON_FILE[2]]
        assert cons.KEYS_JSON_FILE[4] in var_json[cons.KEYS_JSON_FILE[0]][0] \
            [cons.KEYS_JSON_FILE[1]][cons.KEYS_JSON_FILE[2]][cons.KEYS_JSON_FILE[3]]
