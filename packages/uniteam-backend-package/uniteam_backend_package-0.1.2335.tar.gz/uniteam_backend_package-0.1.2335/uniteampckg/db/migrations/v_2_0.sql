CREATE TABLE company_module_map (
    company_id VARCHAR primary KEY REFERENCES company(company_id),
    module_feed JSONB,
    module_connect JSONB,
    module_survey JSONB,
    module_contest JSONB,
    module_recognition JSONB,
    module_events JSONB,
    module_analytics JSONB,
    module_shop JSONB,
    module_notification JSONB,
    module_user_management JSONB,
    module_authentication JSONB,

    hris_intergration JSONB,
    role_based_access JSONB,
    auto_user_grouping JSONB,

    auth_email JSONB,
    auth_sso JSONB,

    custom_branding JSONB,
    custom_color_theme JSONB,

    feed_story JSONB,
    feed_community JSONB,
    feed_recognition JSONB,
    feed_polls JSONB,
    feed_profanity_check JSONB,

    connect_dms JSONB,
    connect_space JSONB,
    connect_huddle JSONB,
    connect_meet JSONB,
    connect_threads JSONB,
    connect_campaigns JSONB,
    connect_recognition JSONB,

    survey_recurring JSONB,

    notification_emails JSONB,
    notification_sms JSONB,
    notification_push JSONB,

    shop_custom_catalog JSONB,
    shop_gitf_card JSONB,
    shop_donation JSONB,
    shop_prepaid_points JSONB,

    auto_occasion JSONB,
);