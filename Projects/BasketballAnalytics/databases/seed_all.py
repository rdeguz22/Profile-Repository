import psycopg2
from pymongo import MongoClient
from datetime import date, datetime, timedelta
import random

PG_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'basketball_db',
    'user': 'postgres',
    'password': 'password'  # Change this!
}

MONGO_URL = 'mongodb://localhost:27017'

def seed_postgresql():
    """Seed PostgreSQL with sample data"""
    conn = psycopg2.connect(**PG_CONFIG)
    cursor = conn.cursor()
    
    print("Seeding PostgreSQL...")
    
    # Sample
    players = [
        ('LeBron James', 'Lakers', 'SF', 81, 250, 23, '1984-12-30'),
        ('Stephen Curry', 'Warriors', 'PG', 75, 185, 30, '1988-03-14'),
        ('Kevin Durant', 'Rockets', 'PF', 82, 240, 35, '1988-09-29'),
        ('Giannis Antetokounmpo', 'Bucks', 'PF', 83, 242, 34, '1994-12-06'),
        ('Luka Dončić', 'Lakers', 'PG', 79, 230, 77, '1999-02-28'),
        ('Joel Embiid', '76ers', 'C', 84, 280, 21, '1994-03-16'),
        ('Nikola Jokić', 'Nuggets', 'C', 83, 284, 15, '1995-02-19'),
        ('Jayson Tatum', 'Celtics', 'SF', 80, 210, 0, '1998-03-03'),
        ('Damian Lillard', 'Trail Blazers', 'PG', 75, 195, 0, '1990-07-15'),
        ('Anthony Davis', 'Mavericks', 'PF', 82, 253, 3, '1993-03-11')
    ]
    
    for player in players:
        cursor.execute(
            """
            INSERT INTO players (name, team, position, height, weight, jersey_number, birth_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
            """,
            player
        )
    print(f"Inserted {len(players)} players")
    
    games = [
        ('Lakers', 'Warriors', 112, 108, date.today() - timedelta(days=10), '2024-2025', 'completed'),
        ('Bucks', 'Suns', 118, 115, date.today() - timedelta(days=9), '2024-2025', 'completed'),
        ('Celtics', 'Nuggets', 105, 110, date.today() - timedelta(days=8), '2024-2025', 'completed'),
        ('Mavericks', '76ers', 0, 0, date.today() + timedelta(days=1), '2024-2025', 'scheduled'),
        ('Lakers', 'Celtics', 0, 0, date.today() + timedelta(days=2), '2024-2025', 'scheduled'),
    ]
    
    for game in games:
        cursor.execute(
            """
            INSERT INTO games (home_team, away_team, home_score, away_score, game_date, season, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            game
        )
    print(f"Inserted {len(games)} games")
    
    sample_stats = [
        # Game 1: Lakers vs Warriors
        (1, 1, 28, 7, 9, 2, 1, 3, 10, 22, 2, 6, 6, 8, 36.5),  # LeBron
        (2, 1, 32, 6, 5, 3, 0, 2, 11, 20, 6, 12, 4, 4, 38.0),  # Curry
        (10, 1, 24, 2, 12, 1, 3, 2, 9, 15, 0, 2, 6, 8, 32.0),  # Luka
        
        # Game 2: Bucks vs Rockets
        (4, 2, 35, 5, 12, 1, 3, 4, 14, 24, 1, 3, 6, 9, 37.0),  # Giannis
        (3, 2, 29, 4, 8, 2, 2, 3, 11, 19, 3, 7, 4, 5, 35.5),  # KD
        
        # Game 3: Celtics vs Nuggets
        (8, 3, 26, 5, 7, 1, 1, 2, 10, 20, 3, 8, 3, 4, 36.0),  # Tatum
        (7, 3, 31, 11, 14, 2, 1, 5, 12, 18, 2, 4, 5, 6, 38.5), # Jokić
    ]
    
    for stat in sample_stats:
        cursor.execute(
            """
            INSERT INTO player_stats 
            (player_id, game_id, points, assists, rebounds, steals, blocks, turnovers,
             field_goals_made, field_goals_attempted, three_pointers_made, 
             three_pointers_attempted, free_throws_made, free_throws_attempted, minutes_played)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            stat
        )
    print(f"Inserted {len(sample_stats)} stat records")
    
    conn.commit()
    cursor.close()
    conn.close()
    print("PostgreSQL seeding complete!\n")

def seed_mongodb():
    """Seed MongoDB with sample events"""
    client = MongoClient(MONGO_URL)
    db = client.basketball_db
    
    print("Seeding MongoDB...")
    
    db.game_events.delete_many({})
    
    # Sample
    events = [
        {
            'game_id': 1,
            'event_type': 'three_pointer',
            'player_id': 2,
            'player_name': 'Stephen Curry',
            'team': 'Warriors',
            'quarter': 1,
            'time_remaining': '10:23',
            'description': 'Stephen Curry makes a deep 3-pointer',
            'timestamp': datetime.utcnow() - timedelta(hours=2, minutes=45)
        },
        {
            'game_id': 1,
            'event_type': 'shot_made',
            'player_id': 1,
            'player_name': 'LeBron James',
            'team': 'Lakers',
            'quarter': 1,
            'time_remaining': '9:45',
            'description': 'LeBron James drives for a powerful dunk',
            'timestamp': datetime.utcnow() - timedelta(hours=2, minutes=44)
        },
        {
            'game_id': 1,
            'event_type': 'assist',
            'player_id': 1,
            'player_name': 'LeBron James',
            'team': 'Lakers',
            'quarter': 2,
            'time_remaining': '5:30',
            'description': 'LeBron assists Anthony Davis on alley-oop',
            'timestamp': datetime.utcnow() - timedelta(hours=2, minutes=20)
        },
        {
            'game_id': 1,
            'event_type': 'steal',
            'player_id': 2,
            'player_name': 'Stephen Curry',
            'team': 'Warriors',
            'quarter': 4,
            'time_remaining': '2:15',
            'description': 'Curry steals and scores on fast break',
            'timestamp': datetime.utcnow() - timedelta(hours=1, minutes=15)
        },
        {
            'game_id': 1,
            'event_type': 'block',
            'player_id': 10,
            'player_name': 'Luka Doncic',
            'team': 'Lakers',
            'quarter': 4,
            'time_remaining': '1:30',
            'description': 'Luka Doncic blocks shot at the rim',
            'timestamp': datetime.utcnow() - timedelta(hours=1, minutes=10)
        }
    ]
    
    result = db.game_events.insert_many(events)
    print(f"Inserted {len(result.inserted_ids)} events")
    
    client.close()
    print("MongoDB seeding complete!\n")

def seed_pinecone():
    """Seed Pinecone with player vectors"""
    try:
        initialize_pinecone()
        
        # Check if index exists, create if not
        if INDEX_NAME not in pinecone.list_indexes():
            create_index()
        
        print("🌱 Seeding Pinecone...")
        
        # Sample player vectors
        players_data = [
            (1, {'avg_points': 28.5, 'avg_assists': 7.2, 'avg_rebounds': 8.1, 
                 'avg_steals': 1.5, 'avg_blocks': 0.8, 'field_goal_pct': 52.5,
                 'three_point_pct': 35.2, 'avg_minutes': 35.5, 'avg_turnovers': 3.2, 
                 'usage_rate': 31.5},
             {'name': 'LeBron James', 'team': 'Lakers', 'position': 'SF'}),
            
            (2, {'avg_points': 32.0, 'avg_assists': 6.0, 'avg_rebounds': 5.0,
                 'avg_steals': 3.0, 'avg_blocks': 0.0, 'field_goal_pct': 55.0,
                 'three_point_pct': 50.0, 'avg_minutes': 38.0, 'avg_turnovers': 2.0,
                 'usage_rate': 32.0},
             {'name': 'Stephen Curry', 'team': 'Warriors', 'position': 'PG'}),
        ]
        
        for player_id, stats, metadata in players_data:
            upsert_player(player_id, stats, metadata)
        
        print(f"Inserted {len(players_data)} player vectors")
        print("Pinecone seeding complete!\n")
    except Exception as e:
        print(f"Pinecone seeding skipped: {e}\n")

# MAIN EXECUTION

if __name__ == "__main__":
    print("="*60)
    print("BASKETBALL PLATFORM - DATABASE SEEDING")
    print("="*60 + "\n")
    
    print("Testing connections...\n")
    pg_ok = test_postgresql()
    mongo_ok = test_mongodb()
    
    if not (pg_ok and mongo_ok):
        print("\nCannot seed - fix database connections first!")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("Starting data seeding...")
    print("="*60 + "\n")
    
    seed_postgresql()
    seed_mongodb()
    seed_pinecone()
    
    print("="*60)
    print("DATABASE SEEDING COMPLETE!")
    print("="*60)
    print("\nYou can now:")
    print("  1. Start backend: uvicorn main:app --reload")
    print("  2. Start frontend: npm start")
    print("  3. Visit: http://localhost:3000")