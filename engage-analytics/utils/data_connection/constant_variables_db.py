"""
List of variables common to every workflow, that can change the result in multiple workflows
"""

# Table Names
COMPANY_TABLE = "companies"
COMPANY_USERS_TABLE = "company_users"
SURVEYS_REPLIES_TABLE = "survey_replies"
COMPANIES_TABLE = 'companies'
SURVEYS_QUESTIONS_TABLE = 'survey_questions'
SURVEYS_ITERATIONS_TABLE = "survey_iterations"
TOPIC_ENTITIES_TABLE = "company_topic_entities"
SURVEY_ITERATION_ENTITIES_TABLE = "survey_iteration_entities"
SURVEY_ENTITIES_TABLE_SURVEY_ITERATION_ID = "survey_iteration_id"
ENTITIES_TABLE_COMPANY_ID = "company_id"
TOPIC_ENTITIES_TABLE_COMPANY_TOPIC_ID = "company_topic_id"
ENTITIES_TABLE_YEAR = "year"
ENTITIES_TABLE_WEEK = "week"
TOPIC_ENTITIES_TABLE_CATEGORIES = "categories"
TOPIC_ENTITIES_TABLE_TAGS = "tags"
SURVEYS_TABLE = "surveys"
QUESTIONS_TABLE = "questions"
DIMENSIONS_TABLE = "dimensions"
TOPICS_TABLE = "company_topics"
TOPIC_COMMENTS_TABLE = "company_topic_comments"
COMPANY_FF_TABLE = "company_feature_flags"
COMPANY_WEEK_TABLE = "company_week"

# Table Names for Active Companies
ACTIVE_COMPANIES_TABLE = "weekly_active_companies"

# Column names for mood_release
COMPANIES_COLUMN_NAMES = ["id", "name", "domain", "created_at", 'language', 'is_enabled', 'deleted_at']

COMPANY_USERS_COLUMN_NAMES = ["id", "company_id", "user_id", "is_general_manager",
                              "is_admin", "roles", "created_at", "deleted_at", "is_enabled"]

SURVEYS_REPLIES_COLUMN_NAMES = ["id", "survey_question_id", "user_id", "rating",
                                "created_at", "user_timezone", "system_timezone",
                                "survey_iteration_token_id", "comment", "comment_deleted_at"]

TOPICS_COLUMN_NAMES = ["topic_id", "company_id", 'is_archived', "topic_content", "created_at", "topic_comment"]

ACTIVE_COMPANIES_COLUMNS = ["company_ids"]

SURVEY_REPLIES_DIMENSIONS_QUESTIONS_COLUMN_NAMES = ["survey_reply_id", 'user_id', 'rating', 'comment_created_at',
                                                    'comment',
                                                    'survey_iteration_id', 'survey_iteration_created_at',
                                                    'iteration_year', 'iteration_week',
                                                    'company_id', 'question_id', 'question_description', "dimension_id",
                                                    'question_week',
                                                    'dimension_description']

# Tables Names
JOBS_ACTIVE_COMPANIES_TABLE = "logs_active_company"
JOBS_ACTIVE_COMPANIES_DETAILS_TABLE = "logs_detail_active_company"

# Columns Names for validation_logs
JOBS_ACTIVE_COMPANIES_COLUMNS_NAMES = ["ID", "date", "survey_year", "survey_week", "percent_accuracy", "error_msg"]
JOBS_ACTIVE_COMPANIES_DETAILS_COLUMNS_NAMES = ["ID", "log_id", "company_id", "label_company_python",
                                               "label_company_php"]

TEST_COMPANIES = ["guerrilla.net", "guerrillamail.net", "mood0253.com", "grr.la", "sharklasers.com"]

# Oliver Classifiers Algorithms
##############################################################

# Variable to Connect to CSV files

PATH_COMPANY = "/data_connection/companies.csv"
PATH_USER = "/data_connection/company_users"
PATH_SURVEY_MOOD = "/data_connection/survey_moods.csv"

# Oliver Classifiers Time Series Algorithms
##########################################################################
TIME_TRIAL = 10
DELAY_WEEKS = 2

