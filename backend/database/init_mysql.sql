-- ============================================================
-- 数据分析系统综合实践 — MySQL 完整建表脚本
-- 数据库: data_analysis_system
-- 字符集: utf8mb4 / utf8mb4_unicode_ci
-- 生成日期: 2026-06-22
-- ============================================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS data_analysis_system
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE data_analysis_system;

-- 关闭外键检查（便于重建）
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================
-- 1. users — 用户表
-- ============================================================
DROP TABLE IF EXISTS user_feedback;
DROP TABLE IF EXISTS study_progress;
DROP TABLE IF EXISTS knowledge_bookmarks;
DROP TABLE IF EXISTS topic_views;
DROP TABLE IF EXISTS teacher_conversations;
DROP TABLE IF EXISTS tts_records;
DROP TABLE IF EXISTS qa_answers;
DROP TABLE IF EXISTS chat_messages;
DROP TABLE IF EXISTS chat_sessions;
DROP TABLE IF EXISTS knowledge_files;
DROP TABLE IF EXISTS file_tags;
DROP TABLE IF EXISTS system_announcements;
DROP TABLE IF EXISTS operation_logs;
DROP TABLE IF EXISTS system_config;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    user_id       BIGINT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL UNIQUE              COMMENT '用户名',
    password      VARCHAR(255) NOT NULL                     COMMENT '密码哈希(bcrypt)',
    email         VARCHAR(100) NOT NULL UNIQUE              COMMENT '邮箱',
    phone         VARCHAR(20)  DEFAULT NULL                 COMMENT '手机号',
    nickname      VARCHAR(50)  DEFAULT NULL                 COMMENT '昵称',
    role          ENUM('student','teacher','admin') DEFAULT 'student' COMMENT '角色',
    avatar        VARCHAR(255) DEFAULT '/static/avatars/default.png' COMMENT '头像URL',
    status        TINYINT      DEFAULT 1                    COMMENT '状态: 0-禁用 1-启用',
    login_count   INT          DEFAULT 0                   COMMENT '登录次数',
    last_login    DATETIME     DEFAULT NULL                COMMENT '最后登录时间',
    last_login_ip VARCHAR(45)  DEFAULT NULL               COMMENT '最后登录IP',
    created_at    DATETIME     DEFAULT CURRENT_TIMESTAMP    COMMENT '注册时间',
    updated_at    DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_role (role),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- ============================================================
-- 2. chat_sessions — 对话会话表
-- ============================================================
DROP TABLE IF EXISTS chat_sessions;
CREATE TABLE chat_sessions (
    session_id    VARCHAR(64)  PRIMARY KEY                 COMMENT '会话ID(UUID)',
    user_id       BIGINT       NOT NULL                     COMMENT '用户ID',
    title         VARCHAR(200) DEFAULT '新对话'             COMMENT '会话标题',
    summary       VARCHAR(500) DEFAULT NULL                 COMMENT '会话摘要(AI生成)',
    course        VARCHAR(50)  DEFAULT NULL                 COMMENT '关联课程',
    message_count INT          DEFAULT 0                    COMMENT '消息数量',
    status        TINYINT      DEFAULT 1                    COMMENT '状态: 0-已删除 1-活跃 2-已归档',
    pinned        TINYINT      DEFAULT 0                    COMMENT '是否置顶: 0-否 1-是',
    created_at    DATETIME     DEFAULT CURRENT_TIMESTAMP    COMMENT '创建时间',
    updated_at    DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_course (course),
    INDEX idx_status (status),
    INDEX idx_pinned (pinned),
    INDEX idx_updated (updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='对话会话表';

-- ============================================================
-- 3. chat_messages — 对话消息表
-- ============================================================
DROP TABLE IF EXISTS chat_messages;
CREATE TABLE chat_messages (
    message_id    BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id    VARCHAR(64)  NOT NULL                     COMMENT '会话ID',
    role          ENUM('user','assistant','system') NOT NULL COMMENT '消息角色',
    content       MEDIUMTEXT   NOT NULL                     COMMENT '消息内容',
    content_type  ENUM('text','markdown','json') DEFAULT 'markdown' COMMENT '内容类型',
    token_count   INT          DEFAULT 0                    COMMENT 'Token数量',
    model_name    VARCHAR(100) DEFAULT NULL                 COMMENT '生成该消息的模型名',
    created_at    DATETIME     DEFAULT CURRENT_TIMESTAMP    COMMENT '创建时间',

    FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
    INDEX idx_session (session_id),
    INDEX idx_role (role),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='对话消息表';

-- ============================================================
-- 4. qa_answers — 问答记录表
-- ============================================================
DROP TABLE IF EXISTS qa_answers;
CREATE TABLE qa_answers (
    answer_id         VARCHAR(64)  PRIMARY KEY              COMMENT '回答ID',
    session_id        VARCHAR(64)  NOT NULL                 COMMENT '会话ID',
    user_id           BIGINT       NOT NULL                 COMMENT '用户ID',
    question          TEXT         NOT NULL                 COMMENT '用户问题',
    answer            MEDIUMTEXT   NOT NULL                 COMMENT 'AI回答',
    course            VARCHAR(50)  DEFAULT NULL             COMMENT '课程',
    enable_rag        BOOLEAN      DEFAULT TRUE             COMMENT '是否启用RAG',
    enable_graph      BOOLEAN      DEFAULT TRUE             COMMENT '是否启用知识图谱',
    references_json  JSON         DEFAULT NULL             COMMENT '引用来源(JSON数组)',
    graph_context_json JSON        DEFAULT NULL             COMMENT '图谱上下文(JSON)',
    related_nodes_json JSON       DEFAULT NULL             COMMENT '关联知识点节点(JSON数组)',
    model_name        VARCHAR(100) DEFAULT 'deepseek-r1:7b' COMMENT '回答所用模型',
    temperature       FLOAT        DEFAULT 0.7              COMMENT '生成温度',
    prompt_tokens     INT          DEFAULT 0                COMMENT '输入Token',
    completion_tokens INT          DEFAULT 0                COMMENT '输出Token',
    total_tokens      INT          DEFAULT 0                COMMENT '总Token',
    response_time_ms  INT          DEFAULT 0                COMMENT '响应时间(毫秒)',
    is_streaming      BOOLEAN      DEFAULT TRUE             COMMENT '是否流式返回',
    created_at        DATETIME     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_session (session_id),
    INDEX idx_user (user_id),
    INDEX idx_course (course),
    INDEX idx_model (model_name),
    INDEX idx_rag (enable_rag),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='问答记录表';

-- ============================================================
-- 5. user_feedback — 用户反馈表
-- ============================================================
DROP TABLE IF EXISTS user_feedback;
CREATE TABLE user_feedback (
    feedback_id  BIGINT AUTO_INCREMENT PRIMARY KEY,
    answer_id    VARCHAR(64)  NOT NULL                     COMMENT '回答ID',
    user_id      BIGINT       NOT NULL                     COMMENT '用户ID',
    rating       TINYINT      NOT NULL                     COMMENT '评分1-5',
    is_helpful   BOOLEAN      DEFAULT NULL                 COMMENT '是否有帮助',
    comment      TEXT         DEFAULT NULL                  COMMENT '评价内容',
    created_at   DATETIME     DEFAULT CURRENT_TIMESTAMP    COMMENT '创建时间',

    FOREIGN KEY (answer_id) REFERENCES qa_answers(answer_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    UNIQUE KEY uk_answer_user (answer_id, user_id),
    INDEX idx_rating (rating),
    INDEX idx_helpful (is_helpful),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户反馈表';

-- ============================================================
-- 6. knowledge_files — 知识库文件表
-- ============================================================
DROP TABLE IF EXISTS knowledge_files;
CREATE TABLE knowledge_files (
    file_id       VARCHAR(64) PRIMARY KEY                  COMMENT '文件ID',
    filename      VARCHAR(255) NOT NULL                    COMMENT '原始文件名',
    file_path     VARCHAR(500) NOT NULL                    COMMENT '存储路径',
    file_type     VARCHAR(20)  NOT NULL                    COMMENT '文件类型: pdf/txt/docx/md',
    file_size     BIGINT       NOT NULL                    COMMENT '文件大小(字节)',
    file_hash     VARCHAR(64)  DEFAULT NULL                COMMENT '文件MD5哈希(去重)',
    course        VARCHAR(50)  NOT NULL                    COMMENT '所属课程',
    tag_id        BIGINT       DEFAULT NULL                 COMMENT '分类标签ID',
    description   TEXT         DEFAULT NULL                 COMMENT '文件描述',
    total_chunks  INT          DEFAULT 0                    COMMENT '总分块数',
    total_tokens  INT          DEFAULT 0                    COMMENT '总Token数',
    status        ENUM('uploading','processing','completed','failed') DEFAULT 'uploading',
    error_message TEXT         DEFAULT NULL                 COMMENT '处理失败原因',
    uploaded_by   BIGINT       NOT NULL                    COMMENT '上传者ID',
    created_at    DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (uploaded_by) REFERENCES users(user_id),
    FOREIGN KEY (tag_id) REFERENCES file_tags(tag_id),
    INDEX idx_course (course),
    INDEX idx_tag (tag_id),
    INDEX idx_status (status),
    INDEX idx_hash (file_hash),
    INDEX idx_uploaded (uploaded_by)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='知识库文件表';

-- ============================================================
-- 7. file_tags — 文件分类标签表
-- ============================================================
DROP TABLE IF EXISTS file_tags;
CREATE TABLE file_tags (
    tag_id      BIGINT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(50)  NOT NULL UNIQUE               COMMENT '标签名',
    course      VARCHAR(50)  DEFAULT NULL                  COMMENT '所属课程(为空则全局通用)',
    color       VARCHAR(20)  DEFAULT '#409EFF'            COMMENT '标签颜色(前端展示)',
    sort_order  INT          DEFAULT 0                     COMMENT '排序',
    created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_course (course),
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文件分类标签表';

-- ============================================================
-- 8. file_chunks — 文件分块表
-- ============================================================
DROP TABLE IF EXISTS file_chunks;
CREATE TABLE file_chunks (
    chunk_id      BIGINT AUTO_INCREMENT PRIMARY KEY,
    file_id       VARCHAR(64) NOT NULL                     COMMENT '所属文件ID',
    chunk_index   INT        NOT NULL                      COMMENT '分块序号(从0开始)',
    content       TEXT       NOT NULL                      COMMENT '分块内容',
    token_count   INT        DEFAULT 0                     COMMENT 'Token数量',
    char_count    INT        DEFAULT 0                     COMMENT '字符数',
    start_page    INT        DEFAULT NULL                  COMMENT '起始页码',
    end_page      INT        DEFAULT NULL                  COMMENT '结束页码',
    faiss_index   INT        DEFAULT NULL                  COMMENT 'FAISS中的向量索引位置',
    created_at    DATETIME   DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (file_id) REFERENCES knowledge_files(file_id) ON DELETE CASCADE,
    UNIQUE KEY uk_file_chunk (file_id, chunk_index),
    INDEX idx_file (file_id),
    INDEX idx_faiss (faiss_index),
    INDEX idx_page (start_page)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文件分块表';

-- ============================================================
-- 9. study_progress — 学习进度表
-- ============================================================
DROP TABLE IF EXISTS study_progress;
CREATE TABLE study_progress (
    progress_id    BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id        BIGINT       NOT NULL                   COMMENT '用户ID',
    course         VARCHAR(50)  NOT NULL                   COMMENT '课程',
    topic          VARCHAR(100) NOT NULL                   COMMENT '知识点名称',
    node_id        VARCHAR(64)  DEFAULT NULL               COMMENT '图谱节点ID',
    question_count INT          DEFAULT 0                   COMMENT '该知识点提问次数',
    correct_count  INT          DEFAULT 0                   COMMENT '自评已掌握次数',
    mastery_level  FLOAT        DEFAULT 0.0                COMMENT '掌握度0.0-1.0',
    study_duration_sec INT      DEFAULT 0                  COMMENT '学习时长(秒)',
    last_study     DATETIME     DEFAULT CURRENT_TIMESTAMP   COMMENT '最后学习时间',
    created_at     DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at     DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    UNIQUE KEY uk_user_topic (user_id, course, topic),
    INDEX idx_user (user_id),
    INDEX idx_course (course),
    INDEX idx_mastery (mastery_level),
    INDEX idx_last_study (last_study)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='学习进度表';

-- ============================================================
-- 10. knowledge_bookmarks — 知识点收藏表
-- ============================================================
DROP TABLE IF EXISTS knowledge_bookmarks;
CREATE TABLE knowledge_bookmarks (
    bookmark_id  BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id      BIGINT       NOT NULL                     COMMENT '用户ID',
    node_id      VARCHAR(64)  NOT NULL                     COMMENT '图谱节点ID',
    node_label   VARCHAR(100) NOT NULL                    COMMENT '节点名称(冗余便于展示)',
    course       VARCHAR(50)  DEFAULT NULL                COMMENT '课程',
    note         TEXT         DEFAULT NULL                  COMMENT '用户备注',
    created_at   DATETIME     DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    UNIQUE KEY uk_user_node (user_id, node_id),
    INDEX idx_user (user_id),
    INDEX idx_course (course),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='知识点收藏表';

-- ============================================================
-- 11. topic_views — 知识点浏览记录表
-- ============================================================
DROP TABLE IF EXISTS topic_views;
CREATE TABLE topic_views (
    view_id     BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id     BIGINT       DEFAULT NULL                  COMMENT '用户ID(为空则匿名)',
    node_id     VARCHAR(64)  NOT NULL                      COMMENT '图谱节点ID',
    node_label   VARCHAR(100) NOT NULL                    COMMENT '节点名称',
    course       VARCHAR(50)  DEFAULT NULL                COMMENT '课程',
    view_source  ENUM('graph_search','graph_click','qa_recommend','bookmark') DEFAULT 'graph_click' COMMENT '浏览来源',
    duration_sec INT          DEFAULT 0                    COMMENT '停留时长(秒)',
    created_at   DATETIME     DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_user (user_id),
    INDEX idx_node (node_id),
    INDEX idx_course (course),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='知识点浏览记录表';

-- ============================================================
-- 12. teacher_conversations — 数字教师对话表
-- ============================================================
DROP TABLE IF EXISTS teacher_conversations;
CREATE TABLE teacher_conversations (
    msg_id        BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id       BIGINT       NOT NULL                    COMMENT '用户ID',
    session_id    VARCHAR(64)  DEFAULT NULL                COMMENT '会话ID(可复用chat_sessions)',
    role          ENUM('student','teacher') NOT NULL       COMMENT '消息角色',
    question      TEXT         NOT NULL                    COMMENT '学生提问',
    answer        MEDIUMTEXT   DEFAULT NULL                COMMENT '教师回答',
    emotion       VARCHAR(30)  DEFAULT 'normal'            COMMENT '教师情绪: normal/happy/serious/encouraging',
    action        VARCHAR(30)  DEFAULT 'explain'          COMMENT '教师动作: explain/demonstrate/encourage/summarize',
    voice_url     VARCHAR(255) DEFAULT NULL                COMMENT '语音文件URL',
    voice_duration_ms INT      DEFAULT 0                   COMMENT '语音时长(毫秒)',
    references_json JSON       DEFAULT NULL                COMMENT '引用来源(JSON)',
    model_name    VARCHAR(100) DEFAULT 'deepseek-r1:7b'    COMMENT '所用模型',
    response_time_ms INT       DEFAULT 0                   COMMENT '响应时间',
    created_at    DATETIME     DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_session (session_id),
    INDEX idx_emotion (emotion),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='数字教师对话表';

-- ============================================================
-- 13. tts_records — 语音合成记录表
-- ============================================================
DROP TABLE IF EXISTS tts_records;
CREATE TABLE tts_records (
    tts_id        BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id       BIGINT       DEFAULT NULL                 COMMENT '用户ID',
    source_type   ENUM('qa_answer','teacher','custom') DEFAULT 'teacher' COMMENT '语音来源类型',
    source_id     VARCHAR(64)  DEFAULT NULL                 COMMENT '来源记录ID',
    text          TEXT         NOT NULL                     COMMENT '合成文本',
    voice         VARCHAR(50)  DEFAULT 'female_zh'         COMMENT '音色',
    speed         FLOAT        DEFAULT 1.0                  COMMENT '语速',
    audio_url     VARCHAR(255) NOT NULL                    COMMENT '音频文件URL',
    audio_format  VARCHAR(10)  DEFAULT 'mp3'               COMMENT '音频格式',
    duration_ms   INT          DEFAULT 0                   COMMENT '音频时长(毫秒)',
    file_size     BIGINT       DEFAULT 0                   COMMENT '文件大小(字节)',
    created_at    DATETIME     DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_user (user_id),
    INDEX idx_source (source_type, source_id),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='语音合成记录表';

-- ============================================================
-- 14. system_announcements — 系统公告表
-- ============================================================
DROP TABLE IF EXISTS system_announcements;
CREATE TABLE system_announcements (
    announcement_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    title            VARCHAR(200) NOT NULL                 COMMENT '公告标题',
    content          TEXT         NOT NULL                  COMMENT '公告内容',
    type             ENUM('info','warning','success','update') DEFAULT 'info' COMMENT '公告类型',
    target_role      ENUM('all','student','teacher','admin') DEFAULT 'all' COMMENT '目标角色',
    is_pinned        BOOLEAN      DEFAULT FALSE             COMMENT '是否置顶',
    is_active        BOOLEAN      DEFAULT TRUE              COMMENT '是否启用',
    view_count       INT          DEFAULT 0                 COMMENT '浏览次数',
    created_by       BIGINT       DEFAULT NULL              COMMENT '创建者ID',
    created_at       DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at       DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    expired_at       DATETIME     DEFAULT NULL              COMMENT '过期时间',

    FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_type (type),
    INDEX idx_active (is_active),
    INDEX idx_pinned (is_pinned),
    INDEX idx_target_role (target_role),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统公告表';

-- ============================================================
-- 15. system_config — 系统配置表
-- ============================================================
DROP TABLE IF EXISTS system_config;
CREATE TABLE system_config (
    config_id    INT AUTO_INCREMENT PRIMARY KEY,
    config_key   VARCHAR(100) NOT NULL UNIQUE              COMMENT '配置键',
    config_value TEXT         NOT NULL                     COMMENT '配置值(JSON)',
    value_type   ENUM('string','int','float','bool','json') DEFAULT 'string' COMMENT '值类型',
    description  VARCHAR(255) DEFAULT NULL                  COMMENT '配置说明',
    is_editable  BOOLEAN      DEFAULT TRUE                  COMMENT '是否可编辑',
    updated_by   BIGINT       DEFAULT NULL                  COMMENT '更新者ID',
    created_at   DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (updated_by) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_key (config_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统配置表';

-- ============================================================
-- 16. operation_logs — 操作日志表
-- ============================================================
DROP TABLE IF EXISTS operation_logs;
CREATE TABLE operation_logs (
    log_id      BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id     BIGINT       DEFAULT NULL                  COMMENT '用户ID',
    action      VARCHAR(50)  NOT NULL                      COMMENT '操作类型',
    module      VARCHAR(50)  NOT NULL                     COMMENT '模块: auth/graph/qa/teacher/files/system',
    detail      TEXT         DEFAULT NULL                  COMMENT '操作详情(JSON)',
    method      VARCHAR(10)  DEFAULT NULL                 COMMENT 'HTTP方法',
    path        VARCHAR(255) DEFAULT NULL                 COMMENT '请求路径',
    status_code INT          DEFAULT NULL                  COMMENT 'HTTP状态码',
    ip_address  VARCHAR(45)  DEFAULT NULL                 COMMENT 'IP地址',
    user_agent  VARCHAR(500) DEFAULT NULL                 COMMENT 'User-Agent',
    duration_ms INT          DEFAULT 0                     COMMENT '请求耗时(毫秒)',
    created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_user (user_id),
    INDEX idx_action (action),
    INDEX idx_module (module),
    INDEX idx_status (status_code),
    INDEX idx_ip (ip_address),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='操作日志表';

-- 恢复外键检查
SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- 初始化数据
-- ============================================================

-- ---------- 用户 ----------
-- 默认密码均为 123456 的 bcrypt 哈希
INSERT INTO users (username, password, email, phone, nickname, role, avatar) VALUES
('admin',    '$2b$12$LJ3m4ys3Lz7ZkQXqFqYxJ.GxJ.fQ8Y8Y8Y8Y8Y8Y8Y8Y8Y8Y8Y8Y', 'admin@example.com',    '13800000001', '系统管理员', 'admin',   '/static/avatars/admin.png'),
('teacher1', '$2b$12$LJ3m4ys3Lz7ZkQXqFqYxJ.GxJ.fQ8Y8Y8Y8Y8Y8Y8Y8Y8Y8Y8Y8Y', 'teacher1@example.com', '13800000002', '王老师',     'teacher', '/static/avatars/teacher1.png'),
('student1', '$2b$12$LJ3m4ys3Lz7ZkQXqFqYxJ.GxJ.fQ8Y8Y8Y8Y8Y8Y8Y8Y8Y8Y8Y8Y', 'student1@example.com', '13800000003', '张三',       'student', '/static/avatars/student1.png'),
('student2', '$2b$12$LJ3m4ys3Lz7ZkQXqFqYxJ.GxJ.fQ8Y8Y8Y8Y8Y8Y8Y8Y8Y8Y8Y8Y', 'student2@example.com', '13800000004', '李四',       'student', '/static/avatars/student2.png');

-- ---------- 文件标签 ----------
INSERT INTO file_tags (name, course, color, sort_order) VALUES
('教材',   'machine_learning', '#409EFF', 1),
('课件',   'machine_learning', '#67C23A', 2),
('笔记',   'machine_learning', '#E6A23C', 3),
('教材',   'data_mining',       '#409EFF', 1),
('课件',   'data_mining',       '#67C23A', 2),
('笔记',   'data_mining',       '#E6A23C', 3),
('通用',   NULL,                '#909399', 99);

-- ---------- 系统配置 ----------
INSERT INTO system_config (config_key, config_value, value_type, description, is_editable) VALUES
('ollama_base_url',       '"http://127.0.0.1:11434"',  'string', 'Ollama服务地址',                 TRUE),
('ollama_model',           '"deepseek-r1:7b"',          'string', '默认大语言模型',                 TRUE),
('ollama_temperature',     '0.7',                       'float',  'LLM生成温度',                    TRUE),
('ollama_max_tokens',      '2048',                      'int',    'LLM最大生成Token数',             TRUE),
('ollama_context_window',  '4096',                      'int',    'LLM上下文窗口大小',              TRUE),
('neo4j_uri',              '"bolt://127.0.0.1:7687"',   'string', 'Neo4j连接地址',                  TRUE),
('neo4j_user',             '"neo4j"',                   'string', 'Neo4j用户名',                    TRUE),
('neo4j_database',         '"knowledge_graph"',         'string', 'Neo4j数据库名',                  TRUE),
('rag_chunk_size',         '500',                       'int',    'RAG分块大小(字符)',              TRUE),
('rag_chunk_overlap',      '50',                        'int',    'RAG分块重叠(字符)',              TRUE),
('rag_top_k',              '5',                         'int',    'RAG检索Top-K',                   TRUE),
('rag_similarity_threshold','0.7',                      'float',  'RAG相似度阈值',                  TRUE),
('embedding_model',        '"BAAI/bge-small-zh-v1.5"',  'string', 'Embedding模型名',                 TRUE),
('embedding_dim',          '512',                       'int',    '向量维度',                       TRUE),
('sd_model_path',          '"models/stable-diffusion-v1-5"', 'string', 'Stable Diffusion模型路径', TRUE),
('sd_default_steps',       '20',                        'int',    'SD默认采样步数',                 TRUE),
('sd_default_cfg',         '7.5',                       'float',  'SD默认CFG Scale',               TRUE),
('sd_device',              '"cuda"',                    'string', 'SD运行设备',                     TRUE),
('tts_voice',               '"female_zh"',               'string', 'TTS默认音色',                    TRUE),
('tts_speed',              '1.0',                        'float',  'TTS默认语速',                    TRUE),
('gpu_total_memory_gb',    '8',                         'int',    'GPU总显存(GB)',                  TRUE),
('gpu_strategy',           '"alternate"',               'string', 'GPU加载策略: alternate/exclusive', TRUE),
('jwt_secret',              '"change-me-in-production"', 'string', 'JWT密钥',                       TRUE),
('jwt_expire_hours',      '2',                          'int',    'JWT过期时间(小时)',              TRUE),
('jwt_refresh_expire_hours','168',                      'int',    'Refresh Token过期时间(小时)',    TRUE),
('system_name',            '"课程知识图谱与智能问答平台"', 'string', '系统名称',                     TRUE),
('system_version',         '"1.0.0"',                   'string', '系统版本',                       FALSE);

-- ---------- 系统公告 ----------
INSERT INTO system_announcements (title, content, type, target_role, is_pinned, is_active, created_by) VALUES
('欢迎使用课程知识图谱与智能问答平台',
 '本系统支持机器学习与数据挖掘两门课程的知识图谱可视化、RAG智能问答和数字教师交互。请在"智能问答"页面提问，或在"知识图谱"页面浏览课程知识结构。',
 'info', 'all', TRUE, TRUE, 1),
('机器学习知识图谱已上线',
 '机器学习课程知识图谱已完成建模，包含监督学习、无监督学习、深度学习等9个核心知识点，欢迎探索！',
 'success', 'all', FALSE, TRUE, 1),
('数据挖掘知识图谱已上线',
 '数据挖掘课程知识图谱已完成建模，包含关联规则、分类与预测、降维等知识点，欢迎探索！',
 'success', 'all', FALSE, TRUE, 1),
('RAG知识库支持PDF上传',
 '教师角色可上传PDF/TXT/DOCX文档到知识库，系统将自动分块、向量化并纳入RAG检索范围。',
 'update', 'teacher', FALSE, TRUE, 1);

-- ---------- 会话样例 ----------
INSERT INTO chat_sessions (session_id, user_id, title, summary, course, message_count, status) VALUES
('sess_demo_001', 3, '关于SVM的讨论', '讨论了支持向量机的基本原理和核函数', 'machine_learning', 4, 1),
('sess_demo_002', 4, 'K-Means聚类学习', '了解了K-Means算法的原理和应用场景', 'machine_learning', 2, 1),
('sess_demo_003', 3, '关联规则挖掘',   '讨论了Apriori算法和支持度计算',     'data_mining',       3, 1);

-- ---------- 消息样例 ----------
INSERT INTO chat_messages (session_id, role, content, content_type, token_count, model_name) VALUES
('sess_demo_001', 'user',      '什么是支持向量机？',                'text',     8,   NULL),
('sess_demo_001', 'assistant', '支持向量机（SVM）是一种二分类模型，其基本模型是定义在特征空间上的间隔最大的线性分类器...', 'markdown', 156, 'deepseek-r1:7b'),
('sess_demo_001', 'user',      'SVM的核函数有哪些？',              'text',     10,  NULL),
('sess_demo_001', 'assistant', '常见的核函数包括：\n1. **线性核** $K(x,y)=x^Ty$\n2. **多项式核** $K(x,y)=(\\gamma x^Ty+r)^d$\n3. **RBF核** $K(x,y)=e^{-\\gamma||x-y||^2}$\n4. **Sigmoid核** $K(x,y)=\\tanh(\\gamma x^Ty+r)$', 'markdown', 198, 'deepseek-r1:7b'),
('sess_demo_002', 'user',      'K-Means聚类的原理是什么？',        'text',     12,  NULL),
('sess_demo_002', 'assistant', 'K-Means是一种划分式聚类算法，通过迭代将数据集划分为K个簇...', 'markdown', 142, 'deepseek-r1:7b'),
('sess_demo_003', 'user',      '什么是关联规则？',                 'text',     7,   NULL),
('sess_demo_003', 'assistant', '关联规则是数据挖掘中用于发现项之间关联关系的方法...', 'markdown', 110, 'deepseek-r1:7b'),
('sess_demo_003', 'user',      'Apriori算法怎么计算支持度？',      'text',     13,  NULL);

-- ---------- 问答记录样例 ----------
INSERT INTO qa_answers (answer_id, session_id, user_id, question, answer, course, enable_rag, enable_graph, references_json, graph_context_json, related_nodes_json, model_name, temperature, prompt_tokens, completion_tokens, total_tokens, response_time_ms) VALUES
('ans_demo_001', 'sess_demo_001', 3, '什么是支持向量机？',
 '支持向量机（SVM）是一种二分类模型，其基本模型是定义在特征空间上的间隔最大的线性分类器。SVM的学习策略就是使间隔最大化，可形式化为一个求解凸二次规划的问题。',
 'machine_learning', TRUE, TRUE,
 '[{"source":"机器学习教材.pdf","page":45,"content":"SVM通过寻找最大间隔超平面进行分类","score":0.92}]',
 '{"related_nodes":["kp_svm","kp_kernel"],"relations":["SVM依赖核函数"]}',
 '["kp_svm","kp_kernel","kp_logr"]',
 'deepseek-r1:7b', 0.7, 512, 156, 668, 3200),
('ans_demo_002', 'sess_demo_001', 3, 'SVM的核函数有哪些？',
 '常见的核函数包括：线性核、多项式核、RBF核（高斯核）、Sigmoid核。其中RBF核是最常用的核函数。',
 'machine_learning', TRUE, TRUE,
 '[{"source":"机器学习教材.pdf","page":47,"content":"核函数将数据映射到高维空间","score":0.89}]',
 '{"related_nodes":["kp_kernel","kp_svm"]}',
 '["kp_kernel","kp_svm"]',
 'deepseek-r1:7b', 0.7, 480, 198, 678, 3500);

-- ---------- 反馈样例 ----------
INSERT INTO user_feedback (answer_id, user_id, rating, is_helpful, comment) VALUES
('ans_demo_001', 3, 5, TRUE, '回答很清晰，帮助理解了SVM的基本原理'),
('ans_demo_002', 3, 4, TRUE, NULL);

-- ---------- 知识点收藏样例 ----------
INSERT INTO knowledge_bookmarks (user_id, node_id, node_label, course, note) VALUES
(3, 'kp_svm',    '支持向量机',   'machine_learning', '重点复习内容'),
(3, 'kp_kmeans', 'K-Means聚类',  'machine_learning', NULL),
(4, 'kp_apriori', 'Apriori算法', 'data_mining',       '关联规则必考');

-- ---------- 学习进度样例 ----------
INSERT INTO study_progress (user_id, course, topic, node_id, question_count, mastery_level, study_duration_sec) VALUES
(3, 'machine_learning', '支持向量机',  'kp_svm',    3, 0.75, 1800),
(3, 'machine_learning', '线性回归',    'kp_lr',     1, 0.90, 900),
(3, 'machine_learning', 'K-Means聚类', 'kp_kmeans', 1, 0.60, 600),
(4, 'machine_learning', 'K-Means聚类', 'kp_kmeans', 1, 0.50, 450),
(4, 'data_mining',       'Apriori算法','kp_apriori',1, 0.40, 300);

-- ---------- 数字教师对话样例 ----------
INSERT INTO teacher_conversations (user_id, session_id, role, question, answer, emotion, action, voice_url, voice_duration_ms, model_name, response_time_ms) VALUES
(3, 'sess_demo_001', 'student', '请讲解一下K-Means聚类算法',
 '好的！K-Means是一种经典的聚类算法，它的核心思想是将数据集划分为K个簇，使得每个数据点到其所属簇中心的距离最小。',
 'encouraging', 'explain', '/static/voice/teacher_001.mp3', 5200, 'deepseek-r1:7b', 4200),
(3, 'sess_demo_001', 'teacher', 'K-Means和DBSCAN有什么区别？',
 'K-Means是基于划分的聚类，需要预先指定K值；DBSCAN是基于密度的聚类，能发现任意形状的簇并识别噪声点。',
 'normal', 'demonstrate', '/static/voice/teacher_002.mp3', 4800, 'deepseek-r1:7b', 3800);

-- ---------- TTS记录样例 ----------
INSERT INTO tts_records (user_id, source_type, source_id, text, voice, speed, audio_url, audio_format, duration_ms, file_size) VALUES
(3, 'teacher', '1', '好的！K-Means是一种经典的聚类算法...', 'female_zh', 1.0, '/static/voice/teacher_001.mp3', 'mp3', 5200, 83200),
(3, 'teacher', '2', 'K-Means和DBSCAN有什么区别...',       'female_zh', 1.0, '/static/voice/teacher_002.mp3', 'mp3', 4800, 76800);

-- ---------- 知识点浏览记录样例 ----------
INSERT INTO topic_views (user_id, node_id, node_label, course, view_source, duration_sec) VALUES
(3, 'kp_svm',    '支持向量机',   'machine_learning', 'graph_click',  120),
(3, 'kp_kernel', '核函数',       'machine_learning', 'qa_recommend',  45),
(3, 'kp_kmeans', 'K-Means聚类',  'machine_learning', 'graph_search',  200),
(4, 'kp_apriori','Apriori算法', 'data_mining',       'graph_click',   90),
(4, 'kp_nb',     '朴素贝叶斯',   'data_mining',       'bookmark',      60);

-- ---------- 操作日志样例 ----------
INSERT INTO operation_logs (user_id, action, module, detail, method, path, status_code, ip_address, duration_ms) VALUES
(3, 'login',     'auth',    '{"username":"student1"}',                        'POST', '/api/v1/auth/login',              200, '192.168.1.100', 120),
(3, 'ask',       'qa',      '{"question":"什么是支持向量机？"}',               'POST', '/api/v1/qa/ask',                  200, '192.168.1.100', 3200),
(3, 'view_graph','graph',   '{"course":"machine_learning"}',                  'GET',  '/api/v1/graph/visualization',     200, '192.168.1.100', 85),
(3, 'bookmark',  'graph',   '{"node_id":"kp_svm"}',                           'POST', '/api/v1/graph/bookmarks',         200, '192.168.1.100', 30),
(4, 'login',     'auth',    '{"username":"student2"}',                        'POST', '/api/v1/auth/login',              200, '192.168.1.101', 115),
(4, 'ask',       'qa',      '{"question":"K-Means聚类的原理是什么？"}',      'POST', '/api/v1/qa/ask',                  200, '192.168.1.101', 2800),
(1, 'login',     'auth',    '{"username":"admin"}',                           'POST', '/api/v1/auth/login',              200, '192.168.1.1',   98),
(1, 'update_config','system','{"key":"rag_top_k","value":8}',                 'PUT',  '/api/v1/system/config',           200, '192.168.1.1',   45);

-- ============================================================
-- 验证查询
-- ============================================================

-- 表数量验证
SELECT CONCAT('共创建 ', COUNT(*), ' 张表') AS summary
FROM information_schema.tables
WHERE table_schema = 'data_analysis_system';

-- 各表行数
SELECT
    t.table_name                                                AS 表名,
    t.table_comment                                             AS 说明,
    IFNULL(r.rows, 0)                                           AS 行数
FROM information_schema.tables t
LEFT JOIN (
    SELECT table_name, table_rows AS rows
    FROM information_schema.tables
    WHERE table_schema = 'data_analysis_system'
) r ON t.table_name = r.table_name
WHERE t.table_schema = 'data_analysis_system'
ORDER BY t.table_name;

-- 外键关系验证
SELECT
    kcu.table_name       AS 子表,
    kcu.column_name      AS 外键列,
    kcu.referenced_table_name AS 父表,
    kcu.referenced_column_name AS 父表列
FROM information_schema.key_column_usage kcu
WHERE kcu.table_schema = 'data_analysis_system'
  AND kcu.referenced_table_name IS NOT NULL
ORDER BY kcu.table_name;
