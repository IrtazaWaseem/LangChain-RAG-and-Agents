DROP TABLE USERS CASCADE CONSTRAINTS;

CREATE TABLE USERS (
    User_ID NUMBER PRIMARY KEY,
    Username VARCHAR2(50) NOT NULL UNIQUE,
    Email VARCHAR2(100) NOT NULL UNIQUE,
    Password_Hash VARCHAR2(255) NOT NULL,
    Join_Date DATE DEFAULT SYSDATE
);

INSERT INTO USERS (User_ID, Username, Email, Password_Hash) VALUES (1, 'Irtaza', 'irtaza@student.edu', 'hash123');
INSERT INTO USERS (User_ID, Username, Email, Password_Hash) VALUES (2, 'Faisal_Nawaz', 'faisal@student.edu', 'hash456');
INSERT INTO USERS (User_ID, Username, Email, Password_Hash) VALUES (3, 'Ali_Tallaeem', 'ali@student.edu', 'hash789');
INSERT INTO USERS (User_ID, Username, Email, Password_Hash) VALUES (4, 'Ayesha_Khan', 'ayesha.k@gmail.com', 'hash101');
INSERT INTO USERS (User_ID, Username, Email, Password_Hash) VALUES (5, 'Bilal_Ahmed', 'bilal.a@yahoo.com', 'hash112');
INSERT INTO USERS (User_ID, Username, Email, Password_Hash) VALUES (6, 'Omar_Farooq', 'omar.f@student.edu', 'hash123');
INSERT INTO USERS (User_ID, Username, Email, Password_Hash) VALUES (7, 'Zain_Malik', 'zain.m@gmail.com', 'hash134');
INSERT INTO USERS (User_ID, Username, Email, Password_Hash) VALUES (8, 'Hassan_Raza', 'hassan.r@hotmail.com', 'hash145');
INSERT INTO USERS (User_ID, Username, Email, Password_Hash) VALUES (9, 'Sana_Javed', 'sana.j@student.edu', 'hash156');
INSERT INTO USERS (User_ID, Username, Email, Password_Hash) VALUES (10, 'Usman_Saeed', 'usman.s@gmail.com', 'hash167');

COMMIT;