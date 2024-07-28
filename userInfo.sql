DROP TABLE IF EXISTS userInfo;

CREATE TABLE userInfo (
    userid INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    username VARCHAR DROP NOT NULL,
    verificate_code VARCHAR NOT NULL,
    input_verificate_code VARCHAR NOT NULL,
    password TEXT NOT NULL
);    