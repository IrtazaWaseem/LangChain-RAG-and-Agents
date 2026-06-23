DROP TABLE HARDWARE_TIERS CASCADE CONSTRAINTS;
CREATE TABLE HARDWARE_TIERS (
    Tier_ID NUMBER PRIMARY KEY,
    Tier_Name VARCHAR2(50) NOT NULL UNIQUE,
    Description VARCHAR2(255)
);


INSERT INTO HARDWARE_TIERS VALUES (1, 'Entry-Level', 'Budget hardware for 1080p gaming');
INSERT INTO HARDWARE_TIERS VALUES (2, 'Mid-Range', 'Standard hardware for 1440p gaming');
INSERT INTO HARDWARE_TIERS VALUES (3, 'Enthusiast', 'High-end hardware for 4K gaming');

COMMIT;
PROMPT>>> Table HARDWARE_TIERS created and populated successfully.';
