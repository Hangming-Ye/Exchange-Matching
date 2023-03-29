CREATE TABLE ACCOUNT(
    accout_id SERIAL,
    balance REAL,
    PRIMARY KEY (accout_id),
);

CREATE TYPE StatusType AS ENUM('open','canceled','executed');
CREATE TABLE ORDER(
    tran_id SERIAL,
    symbol VARCHAR(256),
    remain_amount REAL,
    limit_price REAL,
    status StatusType,
    accout_id INT,
    time BIGINT,
    PRIMARY KEY (tran_id),
    FOREIGN KEY (accout_id) REFERENCES ACCOUNT(accout_id) ON DELETE SET NULL ON UPDATE CASCADE,
);

CREATE TABLE EXECUTED( 
    executed_id SERIAL,
    tran_id INT,
    price REAL,
    time BIGINT,
    PRIMARY KEY (executed_id),
    FOREIGN KEY (tran_id) REFERENCES ORDER(tran_id) ON DELETE SET NULL ON UPDATE CASCADE,
);

CREATE TABLE POSITION( 
    position_id SERIAL,
    accout_id, INT
    amount real,
    symbol VARCHAR(256),
    PRIMARY KEY (position_id),
    FOREIGN KEY (accout_id) REFERENCES ACCOUNT(accout_id) ON DELETE SET NULL ON UPDATE CASCADE,
);