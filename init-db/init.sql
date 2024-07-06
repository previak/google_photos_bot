CREATE TABLE user_flows (
    user_id BIGINT PRIMARY KEY,
    state TEXT,
    flow TEXT
);

CREATE TABLE user_creds (
    user_id BIGINT PRIMARY KEY,
    credentials TEXT
);
