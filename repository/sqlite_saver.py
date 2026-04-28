import sqlite3
import json

class SQLiteRepository:
    def __init__(self, database_name="league_testtest.db"):
        self.conection = sqlite3.connect(database_name)
        self.conection.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.conection.cursor()
        
        self._create_tables()

    def _create_tables(self):

        query_leagues = """
        CREATE TABLE IF NOT EXISTS leagues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            league_name TEXT UNIQUE NOT NULL,
            league_link TEXT UNIQUE NOT NULL
        )
        """
        query_matches = """
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            league_id INTEGER NOT NULL,
            team_1 TEXT,
            team_2 TEXT,
            score_1 TEXT,
            score_2 TEXT,
            best_of TEXT,
            patch TEXT,
            date TEXT,
            match_url TEXT UNIQUE NOT NULL,

            FOREIGN KEY (league_id) REFERENCES leagues(id) ON DELETE CASCADE
        )
        """

        query_games = """
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER NOT NULL,
            winner TEXT,
            time TEXT,
            t_blue TEXT,
            t_red TEXT,
            blue_kills INT,
            blue_towers INT,
            blue_dragons INT,
            blue_nashors INT,
            blue_gold REAL,
            red_kills INT,
            red_towers INT,
            red_dragons INT,
            red_nashors INT,
            red_gold REAL,
            blue_players TEXT,
            red_players TEXT,

            FOREIGN KEY (match_id) REFERENCES matches(id) ON DELETE CASCADE
        )
        """

        query_drafts = """
        CREATE TABLE IF NOT EXISTS drafts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            
            team TEXT NOT NULL CHECK(team IN ('blue', 'red')),
            action TEXT NOT NULL CHECK(action IN ('pick', 'ban')),
            champ TEXT NOT NULL,
            
            lane TEXT CHECK(lane IN ('top', 'jg', 'mid', 'adc', 'sup') OR lane IS NULL),

            FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
        )
        """
        try:
            self.cursor.execute(query_leagues)
            self.cursor.execute(query_matches)
            self.cursor.execute(query_games)
            self.cursor.execute(query_drafts)
            self.conection.commit()
        except Exception as e:
            print("Erro ao criar as tabelas")
            print(e)

    def save_data(self, full_data):
            for data in full_data:
                try:
                    self.cursor.execute("""
                        INSERT OR IGNORE INTO leagues (league_name, league_link) 
                        VALUES (?, ?)
                    """, (data.get('league'), data.get('league_link')))
                    
                    self.cursor.execute("SELECT id FROM leagues WHERE league_name = ?", (data.get('league'),))
                    league_id = self.cursor.fetchone()[0]
                    
                    for match in data.get('matches'):
                            
                        for game in match.get("games"):
                            query_match = """
                            INSERT OR IGNORE INTO matches (league_id, team_1, team_2, score_1, score_2, best_of, patch, date, match_url)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """
                            self.cursor.execute(query_match, (
                                league_id, 
                                match.get('team1'), 
                                match.get('team2'),
                                match.get('score1'),
                                match.get('score2'),
                                game.get('best_of'),
                                match.get('patch'),
                                match.get('date'),
                                match.get('url_match'),
                            ))

                            match_id = self.cursor.lastrowid


                        players_team1_json = json.dumps(game.get('t1_players', []))
                        players_team2_json = json.dumps(data.get('t2_players', []))


                        query_game = """
                        INSERT INTO games (match_id, winner, time, t_blue, t_red, blue_kills, blue_towers, blue_dragons, blue_nashors, blue_gold, red_kills, red_towers, red_dragons, red_nashors, red_gold, blue_players, red_players)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """
                        self.cursor.execute(query_game, (
                            match_id,
                            game.get('winner'),
                            game.get('time'),
                            game.get('t1'),
                            game.get('t2'),
                            game.get('t1_kills'),
                            game.get('t1_towers'),
                            game.get('t1_dragons'),
                            game.get('t1_nashors'),
                            game.get('t1_gold'),
                            game.get('t2_kills'),
                            game.get('t2_towers'),
                            game.get('t2_dragons'),
                            game.get('t2_nashors'),
                            game.get('t2_gold'),
                            players_team1_json,
                            players_team2_json
                        ))

                        game_id = self.cursor.lastrowid

                        query_draft = """
                        INSERT INTO drafts (game_id, team, action, champ, lane)
                        VALUES (?, ?, ?, ?, ?)
                        """
                        lanes = ['top', 'jg', 'mid', 'adc', 'sup']
                        
                        picks_blue = data.get('t1_picks', [])
                        for lane, champ in zip(lanes, picks_blue):
                            self.cursor.execute(query_draft, (game_id, 'blue', 'pick', champ, lane))

                        bans_blue = data.get('t1_bans', [])
                        for champ in bans_blue:
                            self.cursor.execute(query_draft, (game_id, 'blue', 'ban', champ, None))

                        picks_red = data.get('t2_picks', [])
                        for lane, champ in zip(lanes, picks_red):
                            self.cursor.execute(query_draft, (game_id, 'red', 'pick', champ, lane))

                        bans_red = data.get('t2_bans', [])
                        for champ in bans_red:
                            self.cursor.execute(query_draft, (game_id, 'red', 'ban', champ, None))
                    

                except Exception as e:
                    print(e)
                    print("ERRO AO PROCESSAR DADO")
                    self.conection.rollback() 

            self.conection.commit()
            print("Processado com sucesso")

    def close(self):
        self.conection.close()