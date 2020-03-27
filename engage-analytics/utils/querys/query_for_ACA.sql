-- Select Companies--
SELECT 
    *
FROM
    companies;

-- Clean table of companies: Prepare viable companies --
--------------------------------------------------------
-- Step 1.1: Filter test Companies --
SELECT 
    *
FROM
    companies
WHERE
    domain NOT IN ('guerrilla.net' , 'guerrillamail.net',
        'mood0253.com',
        'grr.la',
        'sharklasers.com');
-- Step 1.2: Filter not enabled companies--
SELECT 
    *
FROM
    companies
WHERE
    domain NOT IN ('guerrilla.net' , 'guerrillamail.net',
        'mood0253.com',
        'grr.la',
        'sharklasers.com')
        AND is_enabled = 1;
-- Step 1.3: Filter not deleted companies
-- Query to select viable companies
SELECT 
    *
FROM
    companies
WHERE
    domain NOT IN ('guerrilla.net' , 'guerrillamail.net',
        'mood0253.com',
        'grr.la',
        'sharklasers.com')
        AND is_enable = 1
        AND deleted_at IS NULL;

SELECT
    surveys.company_id AS company_id,
    mood_develop.survey_mood_company_groups.company_group_id AS company_group_id,
    survey_id,
    survey_iteration_id,
    `year` AS `y`,
    `week` AS `w`,
    COUNT(*) AS votes,
    AVG(rating) AS rating,
    SUM(survey_replies.id IS NOT NULL) AS replies
FROM
    mood_develop.survey_mood_company_groups
        JOIN
    mood_develop.survey_moods ON (mood_develop.survey_moods.id = mood_develop.survey_mood_company_groups.survey_mood_id)
        JOIN
    mood_develop.survey_questions ON (survey_question_id = survey_questions.id)
        JOIN
    mood_develop.survey_iterations ON (survey_iteration_id = survey_iterations.id)
        JOIN
    mood_develop.surveys ON (survey_id = surveys.id)
        LEFT JOIN
    mood_develop.survey_replies ON (survey_replies.survey_mood_id = survey_moods.id
        AND survey_replies.deleted_at IS NULL)
WHERE
    `year` = 2018 AND `week` = 45
        AND mood_develop.survey_mood_company_groups.company_group_id = 'c4312095-3ef8-11e8-9266-42010a9c0028'
GROUP BY company_id , survey_id , survey_iteration_id , company_group_id
ORDER BY w DESC;

   -- Expected Result votes 3 rating 4.333 replies 0