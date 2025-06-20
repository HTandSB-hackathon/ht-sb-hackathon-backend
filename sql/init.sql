-- 都道府県の初期データ
INSERT INTO prefectures (id, name) VALUES 
(1, '北海道'), (2, '青森県'), (3, '岩手県'), (4, '宮城県'), (5, '秋田県'), (6, '山形県'), (7, '福島県'),
(8, '茨城県'), (9, '栃木県'), (10, '群馬県'), (11, '埼玉県'), (12, '千葉県'), (13, '東京都'), (14, '神奈川県'),
(15, '新潟県'), (16, '富山県'), (17, '石川県'), (18, '福井県'), (19, '山梨県'), (20, '長野県'), (21, '岐阜県'),
(22, '静岡県'), (23, '愛知県'), (24, '三重県'), (25, '滋賀県'), (26, '京都府'), (27, '大阪府'), (28, '兵庫県'),
(29, '奈良県'), (30, '和歌山県'), (31, '鳥取県'), (32, '島根県'), (33, '岡山県'), (34, '広島県'), (35, '山口県'),
(36, '徳島県'), (37, '香川県'), (38, '愛媛県'), (39, '高知県'), (40, '福岡県'), (41, '佐賀県'), (42, '長崎県'),
(43, '熊本県'), (44, '大分県'), (45, '宮崎県'), (46, '鹿児島県'), (47, '沖縄県');

-- 職業の初期データ
INSERT INTO occupations (name) VALUES 
('会社員'), ('公務員'), ('自営業'), ('フリーランス'), ('学生'), ('主婦・主夫'),
('医師'), ('看護師'), ('教師'), ('エンジニア'), ('デザイナー'), ('営業'),
('研究者'), ('芸術家'), ('農業'), ('漁業'), ('建設業'), ('運輸業');

-- 信頼レベルの初期データ
INSERT INTO trust_levels (name) VALUES 
('初対面'), ('顔見知り'), ('友人'), ('親友'), ('家族同然');

-- 市区町村の初期データ（福島県）
INSERT INTO municipalities (prefecture_id, name, kana) VALUES
(7, '福島市', 'フクシマシ'),
(7, '会津若松市', 'アイヅワカマツシ'),
(7, '郡山市', 'コオリヤマシ'),
(7, 'いわき市', 'イワキシ'),
(7, '白河市', 'シラカワシ'),
(7, '須賀川市', 'スカガワシ'),
(7, '喜多方市', 'キタカタシ'),
(7, '相馬市', 'ソウマシ'),
(7, '二本松市', 'ニホンマツシ'),
(7, '田村市', 'タムラシ'),
(7, '南相馬市', 'ミナミソウマシ'),
(7, '伊達市', 'ダテシ'),
(7, '本宮市', 'モトミヤシ'),
(7, '桑折町', 'コオリマチ'),
(7, '国見町', 'クニミマチ'),
(7, '川俣町', 'カワマタマチ'),
(7, '大玉村', 'オオタマムラ'),
(7, '鏡石町', 'カガミイシマチ'),
(7, '天栄村', 'テンエイムラ'),
(7, '下郷町', 'シモゴウマチ'),
(7, '檜枝岐村', 'ヒノエマタムラ'),
(7, '只見町', 'タダミマチ'),
(7, '南会津町', 'ミナミアイヅマチ'),
(7, '北塩原村', 'キタシオバラムラ'),
(7, '西会津町', 'ニシアイヅマチ'),
(7, '磐梯町', 'バンダイマチ'),
(7, '猪苗代町', 'イナワシロマチ'),
(7, '会津坂下町', 'アイヅバンゲマチ'),
(7, '湯川村', 'ユガワムラ'),
(7, '柳津町', 'ヤナイヅマチ'),
(7, '三島町', 'ミシママチ'),
(7, '金山町', 'カネヤママチ'),
(7, '昭和村', 'ショウワムラ'),
(7, '会津美里町', 'アイヅミサトマチ'),
(7, '西郷村', 'ニシゴウムラ'),
(7, '泉崎村', 'イズミザキムラ'),
(7, '中島村', 'ナカジマムラ'),
(7, '矢吹町', 'ヤブキマチ'),
(7, '棚倉町', 'タナグラマチ'),
(7, '矢祭町', 'ヤマツリマチ'),
(7, '塙町', 'ハナワマチ'),
(7, '鮫川村', 'サメガワムラ'),
(7, '石川町', 'イシカワマチ'),
(7, '玉川村', 'タマカワムラ'),
(7, '平田村', 'ヒラタムラ'),
(7, '浅川町', 'アサカワマチ'),
(7, '古殿町', 'フルドノマチ'),
(7, '三春町', 'ミハルマチ'),
(7, '小野町', 'オノマチ'),
(7, '広野町', 'ヒロノマチ'),
(7, '楢葉町', 'ナラハマチ'),
(7, '富岡町', 'トミオカマチ'),
(7, '川内村', 'カワウチムラ'),
(7, '大熊町', 'オオクママチ'),
(7, '双葉町', 'フタバマチ'),
(7, '浪江町', 'ナミエマチ'),
(7, '葛尾村', 'カツラオムラ'),
(7, '新地町', 'シンチマチ'),
(7, '飯舘村', 'イイタテムラ');


INSERT INTO characters (
    name,
    age,
    gender,
    occupation_id,
    profile_image_url,
    cover_image_url,
    introduction,
    personality,
    hobbies,
    specialties,
    is_active,
    prefecture_id,
    municipality_id,
    tasuki_project_id,
    unlock_condition,
    created_date,
    updated_date
) VALUES (
    'ちえこ',
    78,
    1, -- 女性
    (SELECT id FROM occupations WHERE name = '自営業' LIMIT 1),
    'http://host.docker.internal:8000/api/v1/files/images/ちえこ.png',
    'http://host.docker.internal:8000/api/v1/files/images/ちえこ.png',
    '飯舘村で「気まぐれ茶屋ちえこ」という農家レストランを運営',
    ARRAY['温厚', '面倒見が良い', '話し上手']::text[],
    ARRAY['料理', '園芸']::text[],
    ARRAY['飯館村の歴史', '人生相談']::text[],
    true,
    (SELECT id FROM prefectures WHERE name = '福島県' LIMIT 1),
    (SELECT id FROM municipalities WHERE name = '飯舘村' AND prefecture_id = (SELECT id FROM prefectures WHERE name = '福島県') LIMIT 1),
    'bfb33a20-e896-4006-8505-e0776c3563ba', -- tasuki_project_id
    '「気まぐれ茶屋ちえこ」で食事をすると解放',
    NOW(),
    NOW()
),(
    'しゅうへい',
    82,
    0, -- 男性
    (SELECT id FROM occupations WHERE name = '農業' LIMIT 1),
    'http://host.docker.internal:8000/api/v1/files/images/しゅうへい.png',
    'http://host.docker.internal:8000/api/v1/files/images/しゅうへい.png',
    '郡山で長年看護師として地域医療に貢献してきたおばあちゃん。退職後もボランティアで健康相談に乗ったり、編み物教室を開いたりしている。',
    ARRAY['優しい', '親切', '頼りになる', '明るい']::text[],
    ARRAY['園芸', 'ガーデニング', '健康相談']::text[],
    ARRAY['方言']::text[],
    true,
    (SELECT id FROM prefectures WHERE name = '福島県' LIMIT 1),
    (SELECT id FROM municipalities WHERE name = '会津若松市' AND prefecture_id = (SELECT id FROM prefectures WHERE name = '福島県') LIMIT 1),
    '1062624a-6f00-462e-b317-1186a9eb87f6', -- tasuki_project_id
    '会津若松市の棚田で自撮り撮影した写真をSNSでタグ付きでアップロードすると解放',
    NOW(),
    NOW()
);

INSERT INTO stories (
    character_id,
    required_trust_level,
    title,
    content,
    created_date,
    updated_date
) VALUES (
    (SELECT id FROM characters WHERE name = 'ちえこ' LIMIT 1),
    1,
    '畑での一日',
    '毎朝、日の出とともに畑に出かけます。土の香りと新鮮な空気が大好きです。今日はキュウリの収穫をしました。大きく育ったキュウリを見ると、達成感でいっぱいになります。',
    NOW(),
    NOW()
),(
    (SELECT id FROM characters WHERE name = 'しゅうへい' LIMIT 1),
    1,
    '新しい野菜の挑戦',
    '今年は新しい品種の野菜に挑戦しています。特に珍しいトマトを育てているのですが、色とりどりの実がなってきて、とても楽しみです。収穫が待ち遠しいです。',
    NOW(),
    NOW()
);

INSERT INTO level_thresholds (
    character_id,
    trust_level_id,
    required_points,
    required_conversations,
    required_days_from_first
) VALUES 
(1, (SELECT id FROM trust_levels WHERE name = '初対面' LIMIT 1), 10, 10, 0),
(1, (SELECT id FROM trust_levels WHERE name = '顔見知り' LIMIT 1), 50, 20, 5),
(1, (SELECT id FROM trust_levels WHERE name = '友人' LIMIT 1), 100, 50, 15),
(1, (SELECT id FROM trust_levels WHERE name = '親友' LIMIT 1), 300, 100, 30),
(1, (SELECT id FROM trust_levels WHERE name = '家族同然' LIMIT 1), 1000, 200, 50),
(2, (SELECT id FROM trust_levels WHERE name = '初対面' LIMIT 1), 50, 10, 0),
(2, (SELECT id FROM trust_levels WHERE name = '顔見知り' LIMIT 1), 100, 25, 5),
(2, (SELECT id FROM trust_levels WHERE name = '友人' LIMIT 1), 500, 50, 10),
(2, (SELECT id FROM trust_levels WHERE name = '親友' LIMIT 1), 1000, 200,15),
(2, (SELECT id FROM trust_levels WHERE name = '家族同然' LIMIT 1), 2000, 500, 80);

INSERT INTO achivements (
    name,
    description,
    icon_image_url,
    created_date,
    updated_date
) VALUES (
    'ようこそ、福島県へ',
    '初めてのキャラクターの取得を行った',
    'http://host.docker.internal:8000/api/v1/files/images/achievement_first_conversation.jpg',
    NOW(),
    NOW()
),(
    '初めての会話',
    'キャラクターと初めて会話をした',
    'http://host.docker.internal:8000/api/v1/files/images/achievement_first_conversation.jpg',
    NOW(),
    NOW()
),(
    '親友の証',
    'キャラクターとの信頼レベルが「親友」になった',
    'http://host.docker.internal:8000/api/v1/files/images/achievement_best_friend.png',
    NOW(),
    NOW()
), (
    '家族同然の絆',
    'キャラクターとの信頼レベルが「家族同然」になった',
    'http://host.docker.internal:8000/api/v1/files/images/achievement_family.png',
    NOW(),
    NOW()
),(
    '福島県マスター',
    '福島県のキャラクターと50人と会話をした',
    'http://host.docker.internal:8000/api/v1/files/images/achievement_fukushima_all_characters.png',
    NOW(),
    NOW()
),(
    '福島県の魅力発見',
    '福島県のキャラクターと10人と会話をした',
    'http://host.docker.internal:8000/api/v1/files/images/achievement_fukushima_all_characters.png',
    NOW(),
    NOW()
),(
    '初めての福島県の物語',
    'はじめて、福島県のキャラクターのストーリーを読んだ',
    'http://host.docker.internal:8000/api/v1/files/images/achievement_fukushima_all_stories.png',
    NOW(),
    NOW()
);
