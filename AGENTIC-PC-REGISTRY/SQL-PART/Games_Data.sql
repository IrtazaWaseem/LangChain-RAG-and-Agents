DROP TABLE GAMES CASCADE CONSTRAINTS;

CREATE TABLE GAMES (
    Game_ID NUMBER PRIMARY KEY,
    Title VARCHAR2(150) NOT NULL UNIQUE,
    Developer VARCHAR2(100),
    Release_Year NUMBER(4),
    Category_ID NUMBER,
    Storage_Required_GB NUMBER NOT NULL,
    CONSTRAINT chk_game_storage CHECK (Storage_Required_GB > 0),
    CONSTRAINT fk_game_category FOREIGN KEY (Category_ID) REFERENCES GAME_CATEGORIES(Category_ID)
);

INSERT INTO GAMES VALUES (1, 'Cyberpunk 2077', 'CD Projekt Red', 2020, 3, 70);
INSERT INTO GAMES VALUES (2, 'The Witcher 3: Wild Hunt', 'CD Projekt Red', 2015, 3, 50);
INSERT INTO GAMES VALUES (3, 'Red Dead Redemption 2', 'Rockstar Games', 2018, 3, 120);
INSERT INTO GAMES VALUES (4, 'Grand Theft Auto V', 'Rockstar Games', 2013, 3, 110);
INSERT INTO GAMES VALUES (5, 'Elden Ring', 'FromSoftware', 2022, 3, 60);
INSERT INTO GAMES VALUES (6, 'The Elder Scrolls V: Skyrim', 'Bethesda', 2011, 3, 15);
INSERT INTO GAMES VALUES (7, 'Fallout 4', 'Bethesda', 2015, 3, 30);
INSERT INTO GAMES VALUES (8, 'Starfield', 'Bethesda', 2023, 3, 125);
INSERT INTO GAMES VALUES (9, 'Baldurs Gate 3', 'Larian Studios', 2023, 3, 150);
INSERT INTO GAMES VALUES (10, 'Horizon Zero Dawn', 'Guerrilla Games', 2020, 3, 100);

INSERT INTO GAMES VALUES (11, 'Counter-Strike 2', 'Valve', 2023, 2, 50);
INSERT INTO GAMES VALUES (12, 'Valorant', 'Riot Games', 2020, 2, 30);
INSERT INTO GAMES VALUES (13, 'Apex Legends', 'Respawn Entertainment', 2019, 2, 75);
INSERT INTO GAMES VALUES (14, 'Rainbow Six Siege', 'Ubisoft', 2015, 2, 85);
INSERT INTO GAMES VALUES (15, 'Overwatch 2', 'Blizzard Entertainment', 2022, 2, 50);
INSERT INTO GAMES VALUES (16, 'Call of Duty: Warzone', 'Raven Software', 2020, 2, 125);
INSERT INTO GAMES VALUES (17, 'PUBG: Battlegrounds', 'Krafton', 2017, 2, 40);

INSERT INTO GAMES VALUES (18, 'God of War', 'Santa Monica Studio', 2018, 1, 70);
INSERT INTO GAMES VALUES (19, 'The Last of Us Part I', 'Naughty Dog', 2023, 1, 75);
INSERT INTO GAMES VALUES (20, 'Marvels Spider-Man Remastered', 'Insomniac Games', 2022, 1, 75);
INSERT INTO GAMES VALUES (21, 'Sekiro: Shadows Die Twice', 'FromSoftware', 2019, 1, 25);
INSERT INTO GAMES VALUES (22, 'Batman: Arkham Knight', 'Rocksteady Studios', 2015, 1, 55);
INSERT INTO GAMES VALUES (23, 'Shadow of the Tomb Raider', 'Eidos-Montreal', 2018, 1, 40);
INSERT INTO GAMES VALUES (24, 'Control', 'Remedy Entertainment', 2019, 1, 42);
INSERT INTO GAMES VALUES (25, 'Hogwarts Legacy', 'Avalanche Software', 2023, 1, 85);

INSERT INTO GAMES VALUES (26, 'Forza Horizon 5', 'Playground Games', 2021, 4, 130);
INSERT INTO GAMES VALUES (27, 'Microsoft Flight Simulator', 'Asobo Studio', 2020, 4, 150);
INSERT INTO GAMES VALUES (28, 'Assetto Corsa', 'Kunos Simulazioni', 2014, 4, 15);
INSERT INTO GAMES VALUES (29, 'F1 23', 'Codemasters', 2023, 4, 50);
INSERT INTO GAMES VALUES (30, 'Euro Truck Simulator 2', 'SCS Software', 2012, 4, 12);
INSERT INTO GAMES VALUES (31, 'Dirt Rally 2.0', 'Codemasters', 2019, 4, 100);
INSERT INTO GAMES VALUES (32, 'Need for Speed Unbound', 'Criterion Games', 2022, 4, 50);

INSERT INTO GAMES VALUES (33, 'EA SPORTS FC 24', 'EA Sports', 2023, 5, 100);
INSERT INTO GAMES VALUES (34, 'NBA 2K24', 'Visual Concepts', 2023, 5, 110);
INSERT INTO GAMES VALUES (35, 'WWE 2K23', 'Visual Concepts', 2023, 5, 80);
INSERT INTO GAMES VALUES (36, 'Street Fighter 6', 'Capcom', 2023, 5, 60);
INSERT INTO GAMES VALUES (37, 'Tekken 8', 'Bandai Namco', 2024, 5, 100);
INSERT INTO GAMES VALUES (38, 'Mortal Kombat 1', 'NetherRealm Studios', 2023, 5, 100);
INSERT INTO GAMES VALUES (39, 'Rocket League', 'Psyonix', 2015, 5, 20);

INSERT INTO GAMES VALUES (40, 'League of Legends', 'Riot Games', 2009, 6, 16);
INSERT INTO GAMES VALUES (41, 'Dota 2', 'Valve', 2013, 6, 40);
INSERT INTO GAMES VALUES (42, 'Civilization VI', 'Firaxis Games', 2016, 6, 17);
INSERT INTO GAMES VALUES (43, 'Age of Empires IV', 'Relic Entertainment', 2021, 6, 50);
INSERT INTO GAMES VALUES (44, 'StarCraft II', 'Blizzard Entertainment', 2010, 6, 30);

INSERT INTO GAMES VALUES (45, 'Resident Evil 4 Remake', 'Capcom', 2023, 7, 70);
INSERT INTO GAMES VALUES (46, 'Dead Space Remake', 'Motive', 2023, 7, 50);
INSERT INTO GAMES VALUES (47, 'Rust', 'Facepunch Studios', 2013, 7, 25);
INSERT INTO GAMES VALUES (48, 'Minecraft', 'Mojang', 2011, 7, 2);
INSERT INTO GAMES VALUES (49, 'Phasmophobia', 'Kinetic Games', 2020, 7, 21);
INSERT INTO GAMES VALUES (50, 'Lethal Company', 'Zeekerss', 2023, 7, 1);

COMMIT;