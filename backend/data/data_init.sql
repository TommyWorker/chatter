DELETE FROM "public"."m_general";
DELETE FROM "public"."m_category";

INSERT INTO "public"."m_category"
(category, display_name, maintenance_flag, sort_key, remarks, create_user, create_date, update_user, update_date, del_flag)
VALUES 
('authority_code', 'ログイン者権限', TRUE, 1150, '', 'SYSTEM', NOW(), 'SYSTEM', NOW(), FALSE);

INSERT INTO "public"."m_general"
(category, code, code_value, code_reserve01_text, code_reserve02_text, code_reserve01_flag, code_reserve02_flag, code_reserve01_code, code_reserve02_code, sort_key, remarks, create_user, create_date, update_user, update_date, del_flag)
VALUES 
('authority_code', 0, '一般利用者権限', NULL, NULL, FALSE, FALSE, NULL, NULL, 1000, '権限コード', 'SYSTEM', NOW(), 'SYSTEM', NOW(), FALSE),
('authority_code', 99, '管理者権限', NULL, NULL, FALSE, FALSE, NULL, NULL, 1030, '権限コード', 'SYSTEM', NOW(), 'SYSTEM', NOW(), FALSE);


CREATE EXTENSION IF NOT EXISTS pgcrypto;

TRUNCATE TABLE "public"."m_user" RESTART IDENTITY CASCADE;

INSERT INTO "public"."m_user"
(id, mail_address, user_name, hashed_password, authority_code, create_user, create_date, update_user, update_date, del_flag)
OVERRIDING SYSTEM VALUE
VALUES
(
    1,
    'dummy1@test.com',
    '管理者',
    encode(digest('test', 'sha256'), 'hex'),
    99,
    'SYSTEM',
    NOW(),
    'SYSTEM',
    NOW(),
    FALSE
),
(
    2,
    'dummy2@test.com',
    '三野稔英',
    encode(digest('test', 'sha256'), 'hex'),
    0,
    'SYSTEM',
    NOW(),
    'SYSTEM',
    NOW(),
    FALSE
);

SELECT setval(
    pg_get_serial_sequence('m_user', 'id'),
    COALESCE((SELECT MAX(id) FROM m_user), 0) + 1,
    false
);