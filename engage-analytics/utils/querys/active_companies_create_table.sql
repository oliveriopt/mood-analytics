CREATE TABLE mood_insights_develop.logs_active_company (
    ID varchar(255)  NOT NULL,
    date DATETIME,
    survey_year int,
    survey_week int,
    percent_accuracy DECIMAL(4,2),
    error_msg longtext,
    PRIMARY KEY (ID)
);



CREATE TABLE mood_insights_develop.logs_detail_active_company(
    ID varchar(255)  NOT NULL,
    log_id varchar(255) NOT NULL,
    company_id varchar(255) NOT NULL,
    label_company_python tinyint,
    label_company_php tinyint,
    PRIMARY KEY (ID),
    FOREIGN KEY ( log_id ) REFERENCES logs_active_company(ID)
);
