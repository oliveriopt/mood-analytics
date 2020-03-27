CREATE DATABASE IF NOT EXISTS `mood_core_engage_mapping`;
USE `mood_core_engage_mapping`;
DROP TABLE IF EXISTS `mood_core_engage_mapping`.`entities`;
DROP TABLE IF EXISTS `mood_core_engage_mapping`.`other_entities_names`;
DROP TABLE IF EXISTS `mood_core_engage_mapping`.`relationship_entities`;
DROP TABLE IF EXISTS `mood_core_engage_mapping`.`other_address`;

CREATE TABLE `mood_core_engage_mapping`.`entities`
(
  `lei`                                         VARCHAR(45)   NOT NULL,
  `entity_legalname`                            VARCHAR(500)  NOT NULL,
  `entity_entity_status`                        VARCHAR(50)   NULL,
  `entity_otherentity_names`                    SMALLINT      NULL,
  `entity_other_addresses`                      SMALLINT      NULL,
  `entity_legal_address_firstaddressline`       VARCHAR(2000) NULL,
  `entity_legal_address_city`                   VARCHAR(255)  NULL,
  `entity_legal_address_region`                 VARCHAR(255)  NULL,
  `entity_legal_address_country`                VARCHAR(255)  NULL,
  `entity_legal_address_postalcode`             VARCHAR(1000) NULL,
  `entity_headquarter_address_firstaddressline` VARCHAR(2000) NULL,
  `entity_headquarter_address_city`             VARCHAR(255)  NULL,
  `entity_headquarter_address_region`           VARCHAR(255)  NULL,
  `entity_headquarter_address_country`          VARCHAR(255)  NULL,
  `entity_headquarter_address_postalcode`       VARCHAR(255)  NULL,
  `registration_initial_registration_date`      VARCHAR(255)  NULL,
  `registration_registration_status`            VARCHAR(50)   NULL,
  `registration_next_renewal_date`              VARCHAR(50)   NULL,
  `registration_validation_sources`             VARCHAR(50)   NULL,

  PRIMARY KEY (`lei`)
);

CREATE TABLE `mood_core_engage_mapping`.`other_entities_names`
(
  `lei`                VARCHAR(45)   NOT NULL,
  `other_entity_names` VARCHAR(2000) NULL
);

CREATE TABLE `mood_core_engage_mapping`.`other_address`
(
  `lei`                           VARCHAR(45)   NoT NULL,
  `other_adress_firstaddressline` VARCHAR(2000) NULL,
  `other_adress_city`             VARCHAR(255)  NULL,
  `other_adress_region`           VARCHAR(255)  NULL,
  `other_adress_country`          VARCHAR(255)  NULL,
  `other_adress_postalcode`       VARCHAR(1000) NULL
);


CREATE TABLE `mood_core_engage_mapping`.`relationship_entities`
(
  `lei`                                    VARCHAR(45) NOT NULL,
  `father_lei`                             VARCHAR(45) NOT NULL,
  `relationship_type`                      VARCHAR(45) NULL,
  `relationship_status`                    VARCHAR(50) NULL,
  `registration_initial_registration_date` VARCHAR(50) NULL,
  `registration_last_update_date`          VARCHAR(50) NULL,
  `registration_validation_sources`        VARCHAR(50) NULL
);
