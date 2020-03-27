path_image_kununu = "/engage-analytics/sentiment_analysis/images/logo-kununu.png"
path_image_sr_wc = "/engage-analytics/sentiment_analysis/images/sr_wc_text.png"
path_image_topics_wc = "/engage-analytics/sentiment_analysis/images/topics_wc_text.png"
output_pdf_file = "/report_pdf/"

title = "engage Insights"

subtitle_sr = "Survey Replies by type of sentiment"

subtitle_topics = "Headlines of topics by type of sentiment"

subtitle_topics_comments = "Topic comments by type of sentiment"

subtitle_sr_wc = "Word cloud of surveys replies"

subtitle_topics_wc = "Word cloud of topics"

subtitle_sr_no_comments = "For this week, we do not have any comments"

open_body = """<body>"""

open_table = """<table class="table table-striped">"""

columns_names_surveys_replies = ["Dimension", "Question", "Comment", "Sentiment"]

columns_names_topics = ["Headline", "Sentiment"]

columns_names_surveys_reply_percentage = {"Dimension": "3%",
                                          "Question": "26%",
                                          "Comment": "70%",
                                          "Sentiment": "3%"
                                          }

columns_names_topics_percentage = {
    "Topic ID": "5%",
    "Content": "85%",
    "Sentiment": "10%"
}

dimensions = ["Mood", "Communication", "Interesting Challenges", "Leadership", "Team Spirit", "Work-Life Balance",
              'Working Conditions', 'Work Climate']
