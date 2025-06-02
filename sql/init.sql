-- 都道府県の初期データ
INSERT INTO prefectures (name) VALUES 
('北海道'), ('青森県'), ('岩手県'), ('宮城県'), ('秋田県'), ('山形県'), ('福島県'),
('茨城県'), ('栃木県'), ('群馬県'), ('埼玉県'), ('千葉県'), ('東京都'), ('神奈川県'),
('新潟県'), ('富山県'), ('石川県'), ('福井県'), ('山梨県'), ('長野県'), ('岐阜県'),
('静岡県'), ('愛知県'), ('三重県'), ('滋賀県'), ('京都府'), ('大阪府'), ('兵庫県'),
('奈良県'), ('和歌山県'), ('鳥取県'), ('島根県'), ('岡山県'), ('広島県'), ('山口県'),
('徳島県'), ('香川県'), ('愛媛県'), ('高知県'), ('福岡県'), ('佐賀県'), ('長崎県'),
('熊本県'), ('大分県'), ('宮崎県'), ('鹿児島県'), ('沖縄県');

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
    name_kana,
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
    unlocked_condition,
    created_date,
    updated_date
) VALUES (
    '佐藤 花子',
    'サトウ ハナコ',
    28,
    1, -- 1: 女性 (based on schema: 0: 男性, 1: 女性, 2: その他)
    (SELECT id FROM occupations WHERE name = '農業' LIMIT 1), -- occupation_id for 農業
    'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&h=400&fit=crop',
    'https://images.unsplash.com/photo-1625948515291-69613efd103f?w=800&h=400&fit=crop',
    '須賀川でキュウリとお米を作っています。毎日畑で汗を流していますが、それが私の生きがいです。新鮮な野菜の美味しさを、もっと多くの人に知ってもらいたいです。',
    ARRAY['優しい', '世話好き', '明るい', '頑張り屋']::text[], -- personality array
    ARRAY['家庭菜園', '料理', '手芸', '散歩']::text[], -- hobbies array
    ARRAY['きゅうりの漬物', 'おふくろの味', '野菜作り']::text[], -- specialties array
    true, -- is_active
    (SELECT id FROM prefectures WHERE name = '福島県' LIMIT 1), -- prefecture_id
    (SELECT id FROM municipalities WHERE name = '須賀川市' AND prefecture_id = (SELECT id FROM prefectures WHERE name = '福島県') LIMIT 1), -- municipality_id
    1001, -- tasuki_project_id (assuming a project ID)
    "このキャラクターは現在取得できません",
    NOW(), -- created_date
    NOW() -- updated_date
),(
    '鈴木 美月',
    'スズキ ミツキ',
    35,
    1, -- 1: 女性 (based on schema: 0: 男性, 1: 女性, 2: その他)
    (SELECT id FROM occupations WHERE name = '農業' LIMIT 1), -- occupation_id for 農業
    'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&h=400&fit=crop',
    'https://images.unsplash.com/photo-1625948515291-69613efd103f?w=800&h=400&fit=crop',
    '須賀川でキュウリとお米を作っています。毎日畑で汗を流していますが、それが私の生きがいです。新鮮な野菜の美味しさを、もっと多くの人に知ってもらいたいです。',
    ARRAY['優しい', '頑張り屋']::text[], -- personality array
    ARRAY['家庭菜園', '散歩']::text[], -- hobbies array
    ARRAY['だいこんの漬物', 'おふくろの味', '野菜作り']::text[], -- specialties array
    true, -- is_active
    (SELECT id FROM prefectures WHERE name = '福島県' LIMIT 1), -- prefecture_id
    (SELECT id FROM municipalities WHERE name = '中島村' AND prefecture_id = (SELECT id FROM prefectures WHERE name = '福島県') LIMIT 1), -- municipality_id
    1002, -- tasuki_project_id (assuming a project ID)
    "このキャラクターは現在取得できません",
    NOW(), -- created_date
    NOW() -- updated_date
);

INSERT INTO stories (
    character_id,
    required_trust_level,
    title,
    content,
    created_date,
    updated_date
) VALUES (
    (SELECT id FROM characters WHERE name = '佐藤 花子' LIMIT 1),
    1,
    '畑での一日',
    '毎朝、日の出とともに畑に出かけます。土の香りと新鮮な空気が大好きです。今日はキュウリの収穫をしました。大きく育ったキュウリを見ると、達成感でいっぱいになります。',
    NOW(),
    NOW()
),(
    (SELECT id FROM characters WHERE name = '鈴木 美月' LIMIT 1),
    1,
    '新しい野菜の挑戦',
    '今年は新しい品種の野菜に挑戦しています。特に珍しいトマトを育てているのですが、色とりどりの実がなってきて、とても楽しみです。収穫が待ち遠しいです。',
    NOW(),
    NOW()
);