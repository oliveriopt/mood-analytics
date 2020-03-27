import logging

import lei.src.read_lei.cons as cons

from pypika import Table
from pypika.terms import Values
from pypika import MySQLQuery

from utils import Connector

logger = logging.getLogger()


class BuildInjectQuery:

    @staticmethod
    def build_query_insert(table, key_duplicate, list_values):
        """
        Build query Insert
        :param key_duplicate : boolean in oredr to have dupliacte key on query
        :param table : table name
        :param list_values: list of values to insert
        return query
        """
        table = Table(table)
        values_table = []
        for i in range(len(list_values)):
            values_table.append(tuple(list_values[i]))

        q = BuildInjectQuery.function_insert(MySQLQuery.into(table).insert(values_table[0]), values_table, table, 0)

        if key_duplicate:
            q = q.on_duplicate_key_update(table.lei, Values(table.lei)) \
                .on_duplicate_key_update(table.entity_legalname, \
                                         Values(table.entity_legalname)) \
                .on_duplicate_key_update(table.entity_entity_status, \
                                         Values(table.entity_entity_status)) \
                .on_duplicate_key_update(table.entity_legalname, \
                                         Values(table.entity_legalname)) \
                .on_duplicate_key_update(table.entity_otherentity_names, \
                                         Values(table.entity_otherentity_names)) \
                .on_duplicate_key_update(table.entity_other_addresses, \
                                         Values(table.entity_other_addresses)) \
                .on_duplicate_key_update(table.entity_legal_address_firstaddressline, \
                                         Values(table.entity_legal_address_firstaddressline)) \
                .on_duplicate_key_update(table.entity_legal_address_city, \
                                         Values(table.entity_legal_address_city)) \
                .on_duplicate_key_update(table.entity_legal_address_region, \
                                         Values(table.entity_legal_address_region)) \
                .on_duplicate_key_update(table.entity_legal_address_country, \
                                         Values(table.entity_legal_address_country)) \
                .on_duplicate_key_update(table.entity_legal_address_postalcode, \
                                         Values(table.entity_legal_address_postalcode)) \
                .on_duplicate_key_update(table.entity_headquarter_address_firstaddressline, \
                                         Values(table.entity_headquarter_address_firstaddressline)) \
                .on_duplicate_key_update(table.entity_headquarter_address_city, \
                                         Values(table.entity_headquarter_address_city)) \
                .on_duplicate_key_update(table.entity_headquarter_address_region, \
                                         Values(table.entity_headquarter_address_region)) \
                .on_duplicate_key_update(table.entity_headquarter_address_country, \
                                         Values(table.entity_headquarter_address_country)) \
                .on_duplicate_key_update(table.entity_headquarter_address_postalcode, \
                                         Values(table.entity_headquarter_address_postalcode)) \
                .on_duplicate_key_update(table.registration_initial_registration_date, \
                                         Values(table.registration_initial_registration_date)) \
                .on_duplicate_key_update(table.registration_registration_status, \
                                         Values(table.registration_registration_status)) \
                .on_duplicate_key_update(table.registration_next_renewal_date, \
                                         Values(table.registration_next_renewal_date)) \
                .on_duplicate_key_update(table.registration_validation_sources, \
                                         Values(table.registration_validation_sources))

        return str(q)

    @staticmethod
    def function_insert(q, values, table, i):
        """
        Isnert values of list on query
        :param q : list of entities
        :param table : table name
        :param values : values of the list
        :param i : index
        return query
        """

        if i == 0:
            return BuildInjectQuery.function_insert(q, values, table, i + 1)
        if i != 0 and i < len(values):
            q = q.insert(values[i])
            return BuildInjectQuery.function_insert(q, values, table, i + 1)
        else:
            return q

    @staticmethod
    def action_table_if_exist(database, table, action):
        """
        Inject to database
        :param database : list of entities
        :param table : list of other names
        :param action : list of other addresses
        return query
        """

        if action == "DROP":
            q = "DROP TABLE IF EXISTS " + database + "." + table
            return q

        if action == "CREATE TABLE OTHER ADD":
            q = "CREATE TABLE " + database + "." + table + "(`lei_2` VARCHAR(45) NOT NULL,\
                                                              `other_adress_firstaddressline`  VARCHAR(2000) NULL,\
                                                              `other_adress_city`  VARCHAR(255) NULL,\
                                                              `other_adress_region`  VARCHAR(255) NULL,\
                                                              `other_adress_country`  VARCHAR(255) NULL,\
                                                              `other_adress_postalcode`  VARCHAR(1000) NULL);"
            return q

        if action == "CREATE TABLE OTHER NAMES":
            q = "CREATE TABLE " + database + "." + table + "( `lei_2` VARCHAR(45)  NOT NULL, `other_entity_names`  VARCHAR(2000) NULL);"
            return q

        if action == "CREATE TABLE RR":
            q = "CREATE TABLE " + database + "." + table + "(  `lei_2` VARCHAR(45) NOT NULL, `father_lei`VARCHAR(45) NOT NULL, " \
                                                           "`relationship_type` VARCHAR(45) NULL, `relationship_status`  VARCHAR(50) NULL," \
                                                           "`registration_initial_registration_date`  VARCHAR(50) NULL,`registration_last_update_date`  VARCHAR(50) NULL," \
                                                           "`registration_validation_sources`  VARCHAR(50) NULL);"
            return q


class InjectSQLtoDB:

    @staticmethod
    def drop_create_tables() -> None:
        """
        Drop and create tables
        """
        BuildInjectQuery.action_table_if_exist(cons.DATABASE_NAME, "DROP", cons.LEI_OTHER_ADRESSES)
        BuildInjectQuery.action_table_if_exist(cons.DATABASE_NAME, "CREATE TABLE OTHER ADD", cons.LEI_OTHER_ADRESSES)
        BuildInjectQuery.action_table_if_exist(cons.DATABASE_NAME, "DROP", cons.LEI_OTHER_ENTITIES_NAME)
        BuildInjectQuery.action_table_if_exist(cons.DATABASE_NAME, "CREATE TABLE OTHER NAMES",
                                               cons.LEI_OTHER_ENTITIES_NAME)
        BuildInjectQuery.action_table_if_exist(cons.DATABASE_NAME, "DROP", cons.LEI_RELATIONSHIP_ENTITIES)
        BuildInjectQuery.action_table_if_exist(cons.DATABASE_NAME, "CREATE TABLE RR", cons.LEI_RELATIONSHIP_ENTITIES)

    @staticmethod
    def inject_to_db_entity(conn: Connector, entity: list, other_names: list, other_add: list,
                            first_step: bool) -> None:
        """
        Inject to database
        :param conn: Connector
        :param entity : list of entities
        :param other_names : list of other names
        :param other_add : list of other addresses
        :param first_step:
        """

        q = BuildInjectQuery.build_query_insert(cons.LEI_ENTITIES_TABLE, True, entity)
        rows_affected = conn.insert_query(q)
        logger.info(msg="Rows Affected: " + str(rows_affected) + " rows")

        if first_step: InjectSQLtoDB.drop_create_tables()

        if len(other_add) > 0:
            q = BuildInjectQuery.build_query_insert(cons.LEI_OTHER_ADRESSES, False, other_add)
            conn.insert_query(q)
        if len(other_names) > 0:
            q = BuildInjectQuery.build_query_insert(cons.LEI_OTHER_ENTITIES_NAME, False, other_names)
            conn.insert_query(q)

    @staticmethod
    def inject_to_db_rr(conn: Connector, relationships: list) -> None:
        """
        Inject to database
        :param conn DB connector
        :param relationships
        """

        q = BuildInjectQuery.build_query_insert(cons.LEI_RELATIONSHIP_ENTITIES, False, relationships)
        conn.insert_query(q)