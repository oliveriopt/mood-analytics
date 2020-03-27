from unittest import TestCase, mock

from sentiment_analysis.src.report.interface_report import InterFaceReport


class TestInterFaceReport(TestCase):

    def setUp(self):
        self.company_id = 'e9464795-d6e0-11e7-9246-42010a840018'
        self.weeks = ['47_2019']
        self.table_surveys_replies = [{'dimension': 'Communication',
                                       'question': 'We share project relevant information or changes with each other.',
                                       'comment': 'There is definitely room for improvement there. ',
                                       'sentiment': 'neutral'},
                                      {'dimension': 'Team Spirit', 'question': 'How well do you work as a team?',
                                       'comment': 'We can do better but significant progress is happening',
                                       'sentiment': 'negative'},
                                      {'dimension': 'Team Spirit', 'question': 'How well do you work as a team?',
                                       'comment': 'Our team works together very well, however, I find that we can do better in regard to cross-department collaboration (i.e. as "kununu as a whole").',
                                       'sentiment': 'positive'}]
        self.redis_data = {'c3d7066d-99f2-4f9a-adc6-221dabc0170e': {'dimension': 'communication',
                                                                    'text': 'There is definitely room for improvement there. ',
                                                                    'score': 0.5,
                                                                    'entities_text': ['room', 'improvement'],
                                                                    'entities_type': ['LOCATION', 'OTHER']},
                           'aa94c329-51d7-4b61-b88d-adb3d89d3a92': {'dimension': 'teamspirit',
                                                                    'text': 'We can do better but significant progress is happening',
                                                                    'score': -0.20000000298023224,
                                                                    'entities_text': ['progress'],
                                                                    'entities_type': ['OTHER']},
                           'fdc80e5c-e070-4ee9-869b-5b460e7b7f12': {'dimension': 'teamspirit',
                                                                    'text': 'very smoothly running team',
                                                                    'score': 0.10000000149011612,
                                                                    'entities_text': ['team'],
                                                                    'entities_type': ['ORGANIZATION']},
                           '18c2ae84-78b6-4099-8c38-d7d8299f2f3c': {'dimension': 'teamspirit',
                                                                    'text': 'Our team works together very well, however, I find that we can do better in regard to cross-department collaboration (i.e. as "kununu as a whole").',
                                                                    'score': 0.10000000149011612,
                                                                    'entities_text': ['team', 'regard', 'collaboration',
                                                                                      'whole'],
                                                                    'entities_type': ['ORGANIZATION', 'OTHER']}}

        self.surveys = {}
        self.topics = {'e9464795-d6e0-11e7-9246-42010a840018': {
            '13383120-049b-11ea-81c0-42010a9c0006': {'created_at': '2019-11-11 15:51:07', 'headline': {
                'topic_content': 'Moritz: would support a quarter with no power point / google slides as a Test (pioneering new work). Please vote up if you would support, down if you don’t.',
                'entities_text': ['test', 'slides', 'power point', 'work'], 'entities_type': ['OTHER'],
                'topic_score': -0.10000000149011612}, 'comments': [{
                'topic_comment': '(Yenia): Interesting idea! I first heard about this through this Amazon piece of news (https://www.inc.com/carmine-gallo/jeff-bezos-bans-powerpoint-in-meetings-his-replacement-is-brilliant.html) and it could be an interesting experiment for us. It would however mean that we would need to work a lot more with pre-reads as a company. Very curious to hear more opinions on this one!',
                'topic_comment_id': '1fdb55cc-07a9-11ea-81c0-42010a9c0006',
                'entities_text': ['experiment', 'idea', 'news',
                                  'company', 'opinions'],
                'entities_type': ['ORGANIZATION', 'OTHER'],
                'topic_comment_score': 0.20000000298023224}, {
                'topic_comment': '[Moritz]: I dont know what tool we would use but I would seek for comprehensive summaries on one single page. Or if we update one another lets just look at the standard tools like tableau, okrs, ... instead of creating new documents.\nWhy do I bring this up: I am worried that too much time goes into creating presentations that could and should be used for deep thinking and listening to customers and users.',
                'topic_comment_id': '4a5f9943-0be6-11ea-81c0-42010a9c0006',
                'entities_text': ['tool', 'summaries', 'page',
                                  'presentations', 'tools',
                                  'tableau', 'okrs', 'another',
                                  'documents', 'thinking',
                                  'customers', 'users'],
                'entities_type': ['PERSON', 'WORK_OF_ART',
                                  'OTHER', 'EVENT'],
                'topic_comment_score': 0.0}, {
                'topic_comment': '@ Moritz: Which tool / format would you see in your test when it comes to summarize information / proposals to other groups of people?',
                'topic_comment_id': '5692067a-0518-11ea-81c0-42010a9c0006',
                'entities_text': ['  moritz', 'tool format',
                                  'test', 'groups', 'people',
                                  'information proposals'],
                'entities_type': ['PERSON', 'ORGANIZATION',
                                  'OTHER'],
                'topic_comment_score': 0.0}, {
                'topic_comment': '@ Moritz: Which tool / format would you see in your test when it comes to summarizing information / proposals to other groups of people?',
                'topic_comment_id': 'e2e38a9d-0ad1-11ea-81c0-42010a9c0006',
                'entities_text': ['  moritz', 'tool format',
                                  'test', 'groups', 'people',
                                  'information proposals'],
                'entities_type': ['PERSON', 'ORGANIZATION',
                                  'OTHER'],
                'topic_comment_score': 0.0}, {
                'topic_comment': '2/2 - I would agree in reducing as much as possible the use of detailed slides in meetings and promoting pre-readings',
                'topic_comment_id': '8c4cdc2e-04b0-11ea-81c0-42010a9c0006',
                'entities_text': ['meetings', 'pre-readings',
                                  'slides'],
                'entities_type': ['OTHER', 'EVENT'],
                'topic_comment_score': 0.20000000298023224}, {
                'topic_comment': 'I  challenge the need of doing this test. PowerPoint or Google slides are good supports that can be shared as pre-readings and remains after the meetings. This support might help to spread the word to the ones that didn’t attend or the ones that want to revisit the topic. They also enable alignment because there is no need to really only in people’s understanding on the meetings.',
                'topic_comment_id': '39eaf75b-04b0-11ea-81c0-42010a9c0006',
                'entities_text': ['supports', 'need', 'test',
                                  'powerpoint', 'ones', 'ones',
                                  'support', 'meetings',
                                  'pre-readings', 'word', 'need',
                                  'alignment', 'meetings',
                                  'understanding', 'people',
                                  'topic'],
                'entities_type': ['PERSON', 'OTHER', 'EVENT'],
                'topic_comment_score': 0.30000001192092896}, {
                'topic_comment': 'I understand your point, thank you for clarifying!',
                'topic_comment_id': 'cbd60204-0c4e-11ea-81c0-42010a9c0006',
                'entities_text': ['point'],
                'entities_type': ['OTHER'],
                'topic_comment_score': 0.699999988079071}, {
                'topic_comment': 'Is this topic *for* or *from* Moritz?',
                'topic_comment_id': 'fd6fc750-06d1-11ea-81c0-42010a9c0006',
                'entities_text': ['topic'],
                'entities_type': ['OTHER'],
                'topic_comment_score': 0.0}, {
                'topic_comment': 'Just out of interest, because it was mentioned in the OP. What is specifically "new work" about not using a presentation tool? I think everyone should use the tool that they think suits them best to transport their thoughts and ideas so that the listener can understand it in the best way. Be it powerpoint, flipcharts or single page summaries. I understand where the idea is coming from, I doubt if it will be more effective and efficient. I rather would like to see us all generally preparing more for meetings.',
                'topic_comment_id': 'eb46b3ad-0fd0-11ea-81c0-42010a9c0006',
                'entities_text': ['interest', 'tool', 'work',
                                  'presentation tool', 'ideas',
                                  'thoughts', 'flipcharts',
                                  'everyone', 'listener',
                                  'meetings', 'page summaries',
                                  'idea'],
                'entities_type': ['PERSON', 'WORK_OF_ART',
                                  'OTHER', 'EVENT'],
                'topic_comment_score': 0.20000000298023224}]},
            '29e803ba-0083-11ea-81c0-42010a9c0006': {'created_at': '2019-11-06 10:49:53', 'headline': {
                'topic_content': 'Global: I think we should start to switch to a results-only environment someday soon to compete against other employers.',
                'entities_text': ['results', 'environment', 'employers'], 'entities_type': ['ORGANIZATION', 'OTHER'],
                'topic_score': 0.0}, 'comments': [{
                'topic_comment': 'Do you have any good example of a company that implemented this mode cross all the employees and had positive results?',
                'topic_comment_id': '8d666c12-009c-11ea-81c0-42010a9c0006',
                'entities_text': ['company', 'example', 'mode', 'results',
                                  'employees'],
                'entities_type': ['ORGANIZATION', 'PERSON', 'OTHER'],
                'topic_comment_score': 0.0}, {
                'topic_comment': 'Exaclty, I think we do work like this. Specially in Berlin.',
                'topic_comment_id': '61f5e8ff-02e7-11ea-81c0-42010a9c0006',
                'entities_text': [], 'entities_type': [],
                'topic_comment_score': 0.4000000059604645}, {
                'topic_comment': 'Hi there! Could you please help me understand better what you mean by the "results-only environment" which you mentioned and also, what would come with that? Thank you in advance! Best, Johannes',
                'topic_comment_id': 'ca492498-0090-11ea-81c0-42010a9c0006',
                'entities_text': ['environment', 'advance'],
                'entities_type': ['OTHER'],
                'topic_comment_score': 0.20000000298023224}, {
                'topic_comment': 'I find it really hard to argue that we are not, for the most part, currently operating under these principles already?',
                'topic_comment_id': '32e40588-0181-11ea-81c0-42010a9c0006',
                'entities_text': ['part', 'principles'],
                'entities_type': ['OTHER'],
                'topic_comment_score': -0.6000000238418579}, {
                'topic_comment': "This sounds like a factory rather than a growing, user-focused tech company. The biggest issue I see with an approach like this is it completely lacks the human side and only focuses on KPIs which as we know don't tell a complete story.",
                'topic_comment_id': '68a58e81-045d-11ea-81c0-42010a9c0006',
                'entities_text': ['factory', 'issue', 'growing', 'tech company',
                                  'kpis', 'approach', 'story', 'human side'],
                'entities_type': ['ORGANIZATION', 'OTHER', 'LOCATION'],
                'topic_comment_score': -0.30000001192092896}, {
                'topic_comment': 'Trying to understand this a bit better: 1) does this topic imply that people at kununu are not measured by results? 2) why is a model important to compete against employers? \n\nImo we have a mindset where results matter most and not where and when you actually do your work. But maybe this is perceived otherwise by others?',
                'topic_comment_id': '394af0f0-00b0-11ea-81c0-42010a9c0006',
                'entities_text': ['topic', 'people', 'kununu', 'results',
                                  'mindset', 'model', 'results', 'employers',
                                  'work', 'others'],
                'entities_type': ['PERSON', 'ORGANIZATION', 'OTHER'],
                'topic_comment_score': -0.20000000298023224}]},
            '50dd2a04-0ae9-11ea-81c0-42010a9c0006': {'created_at': '2019-11-19 16:26:18', 'headline': {
                'topic_content': 'Global: How should we use engage/talk about engage in our daily worklife to be a "best practice" for our customers?',
                'entities_text': ['worklife', 'practice', 'customers'], 'entities_type': ['PERSON', 'OTHER'],
                'topic_score': 0.5}, 'comments': [{
                'topic_comment': '[Carlos] I think the first step should be use the tool. our weekly participation rates are still not optimal and having more representativity and more insights would allow us to improve our own worklife and developing kununu as great place to work!\nIn my opinion, in the last weeks the quality of the insights increased specially with new and challenging topics that raised lots of good comments.\nIt would be great if you can share ideas for engage here or directly to me. As an example, for the new topics page one of the ideas came from a comment in a similar topic.',
                'topic_comment_id': 'd4efa741-0b9d-11ea-81c0-42010a9c0006',
                'entities_text': ['topics', 'tool', 'insights', 'step',
                                  'representativity', 'participation rates',
                                  'opinion', 'quality', 'place', 'worklife',
                                  'lots', 'example', 'topic', 'comment', 'ideas',
                                  'ideas', 'comments'],
                'entities_type': ['WORK_OF_ART', 'OTHER'],
                'topic_comment_score': 0.5}, {
                'topic_comment': '[Moritz] I agree with Carlos wish and would encourage every single employee to actively participate in creating a better workplace for us (kununus)',
                'topic_comment_id': 'e218e90d-0be5-11ea-81c0-42010a9c0006',
                'entities_text': ['employee', 'workplace'],
                'entities_type': ['PERSON', 'LOCATION'],
                'topic_comment_score': 0.5}, {
                'topic_comment': "Absolutely. It's nice that we figured out how to become better in Vienna but if people from other locations do not use pre-fixes etc., the whole concept is not working. Actually I am surprised that kununu is surprised about that and we start to tackle that issue very late",
                'topic_comment_id': '00f06032-0b9c-11ea-81c0-42010a9c0006',
                'entities_text': ['locations', 'pre-fixes', 'vienna', 'concept',
                                  'people', 'issue'],
                'entities_type': ['PERSON', 'CONSUMER_GOOD', 'OTHER', 'LOCATION'],
                'topic_comment_score': 0.0}, {
                'topic_comment': 'Boston team has a separate group of non-managers in charge of encouraging weekly engage participation, bringing forth and helping drive solutions for important topics in and out of engage, and overall making sure we work well together (we call it the BBB or "Better business bureau :) ) It has been very positive for us since we started it last year. Members change every quarter',
                'topic_comment_id': 'dbad23e0-0cc3-11ea-81c0-42010a9c0006',
                'entities_text': ['team', 'group', 'non-managers', 'boston',
                                  'charge', 'participation', 'solutions',
                                  'topics', 'business bureau', 'members'],
                'entities_type': ['ORGANIZATION', 'PERSON', 'OTHER', 'LOCATION'],
                'topic_comment_score': 0.30000001192092896}, {
                'topic_comment': 'Let us be transparent about how engage is used in different locations, how topics are followed up and let us see how we can close the feedback loop when it comes to global topics. If we take the feedback serious and we follow up on topics, I am sure we can increase participation rate',
                'topic_comment_id': '3a2c48f9-0c79-11ea-81c0-42010a9c0006',
                'entities_text': ['topics', 'topics', 'locations',
                                  'feedback loop', 'participation rate',
                                  'feedback'],
                'entities_type': ['OTHER', 'LOCATION'],
                'topic_comment_score': 0.4000000059604645}, {
                'topic_comment': 'Since it\'s our product I see a lot of responsibility on our shoulders to pioneer best practices. I really like that we are adapting the format and I\'m intrigued to see if people gain more value from the new format. I\'m unsure how we can translate the location-based "ways of using engage" into best practices if each location doesn\'t know how the other is using engage. I also think it\'s important how we frame engage --> it\'s a conversation starter, not a silver bullet for problems.',
                'topic_comment_id': 'cafce2a8-0b71-11ea-81c0-42010a9c0006',
                'entities_text': ['product', 'responsibility', 'best practices',
                                  'shoulders', 'conversation starter', 'format',
                                  'format', 'best practices', 'value', 'people',
                                  'ways', 'other', 'problems', 'silver bullet',
                                  'location'],
                'entities_type': ['PERSON', 'CONSUMER_GOOD', 'OTHER', 'LOCATION'],
                'topic_comment_score': 0.4000000059604645}]}}}

    def TearDown(self):
        del self.company_id, self.table_surveys_replies, self.topics, self.weeks, self.redis_data

    @mock.patch("utils.data_connection.api_data_manager.APISourcesFetcher", autospec=True)
    @mock.patch("sentiment_analysis.src.clients_language_sentiments_entity.ClientsLanguageSentiment", autospec=True)
    def test_sort_by_dimension_sentiment_table(self, mock_g_client, mock_sources_fetcher):
        self.interface_report = InterFaceReport(surveys=self.surveys, topics=self.topics,
                                                company_id=self.company_id, weeks=self.weeks,
                                                g_client=mock_g_client, api_source_manager=mock_sources_fetcher)

        self.interface_report.table_surveys_replies = self.table_surveys_replies
        self.interface_report.sort_by_dimension_sentiment_table()
        assert self.interface_report.table_surveys_replies == [{'dimension': 'Communication',
                                                                'question': 'We share project relevant information or changes with each other.',
                                                                'comment': 'There is definitely room for improvement there. ',
                                                                'sentiment': 'neutral'}, {'dimension': 'Team Spirit',
                                                                                          'question': 'How well do you work as a team?',
                                                                                          'comment': 'Our team works together very well, however, I find that we can do better in regard to cross-department collaboration (i.e. as "kununu as a whole").',
                                                                                          'sentiment': 'positive'},
                                                               {'dimension': 'Team Spirit',
                                                                'question': 'How well do you work as a team?',
                                                                'comment': 'We can do better but significant progress is happening',
                                                                'sentiment': 'negative'}]

        assert isinstance(self.interface_report.table_surveys_replies, list)
