DROP TABLE IF EXISTS input_verificate_code;

CREATE TABLE input_verificate_code (
    email VARCHAR NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    verificate_code VARCHAR NOT NULL
    input_verificate_code VARCHAR NOT NULL
);    