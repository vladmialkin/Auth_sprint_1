CREATE SCHEMA IF NOT EXISTS auth;

CREATE TABLE IF NOT EXISTS auth.user (
    id uuid PRIMARY KEY,
    email varchar(254) NOT NULL UNIQUE,
    password TEXT NOT NULL,
    salt bytea NOT NULL,
    is_active boolean NOT NULL DEFAULT true,
    is_staff boolean NOT NULL DEFAULT false,
    is_super_user boolean NOT NULL DEFAULT false,
    last_login timestamp with time zone,
    created timestamp with time zone DEFAULT NOW(),
    modified timestamp with time zone DEFAULT NOW() ON UPDATE NOW()
);

CREATE TABLE IF NOT EXISTS auth.role(
    id uuid PRIMARY KEY,
    name varchar(100) NOT NULL UNIQUE,
    created timestamp with time zone DEFAULT NOW(),
    modified timestamp with time zone DEFAULT NOW() ON UPDATE NOW()
);

CREATE TABLE IF NOT EXISTS auth.user_role(
    id uuid PRIMARY KEY,
    user_id uuid NOT NULL REFERENCES auth.user (id) ON DELETE CASCADE,
    role_id uuid NOT NULL REFERENCES auth.role (id) ON DELETE CASCADE,
    created timestamp with time zone DEFAULT NOW(),
    modified timestamp with time zone DEFAULT NOW() ON UPDATE NOW(),
    UNIQUE(user_id, role_id)
);

CREATE TABLE IF NOT EXISTS auth.session(
    id uuid PRIMARY KEY,
    user_id uuid NOT NULL REFERENCES auth.user (id) ON DELETE CASCADE,
    refresh_token_id uuid NOT NULL REFERENCES auth.refresh_token (id) ON DELETE CASCADE,
    user_agent varchar(254) NOT NULL UNIQUE,
    created timestamp with time zone DEFAULT NOW(),
    modified timestamp with time zone DEFAULT NOW() ON UPDATE NOW()
);

CREATE TABLE IF NOT EXISTS auth.refresh_token(
    id uuid PRIMARY KEY,
    token TEXT NOT NULL,
    expiration_date timestamp with time zone NOT NULL,
    created timestamp with time zone DEFAULT NOW(),
    modified timestamp with time zone DEFAULT NOW() ON UPDATE NOW(),
    UNIQUE(token)
);

#Индекс на поле is_active, если часто фильтровать пользователей по этому полю.
CREATE INDEX idx_user_is_active ON auth.user (is_active);

#Индексы на поле created или modified, если выполнять запросы, основанные на времени создания или изменения.
CREATE INDEX idx_role_created ON auth.role (created);

#Индекс на user_id и role_id для ускорения соединений и поиска по этим полям, особенно если делать выборки на основе ролей пользователей.
CREATE INDEX idx_user_role_user ON auth.user_role (user_id);
CREATE INDEX idx_user_role_role ON auth.user_role (role_id);

#Индекс на user_id для быстрого доступа к сессиям пользователя.
CREATE INDEX idx_session_user ON auth.session (user_id);

#Индекс на expiration_date, чтобы быстро находить токены, которые истекают.
CREATE INDEX idx_refresh_token_expiration ON auth.refresh_token (expiration_date);
