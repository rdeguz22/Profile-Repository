import pinecone
import os
from typing import List, Dict
import numpy as np

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "your-api-key-here")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-west1-gcp")
INDEX_NAME = "basketball-players"

def initialize_pinecone():
    """Initialize Pinecone connection"""
    pinecone.init(
        api_key=PINECONE_API_KEY,
        environment=PINECONE_ENVIRONMENT
    )
    print("✅ Pinecone initialized")

def create_index():
    """Create Pinecone index for player similarity"""
    
    # Check if index exists
    if INDEX_NAME in pinecone.list_indexes():
        print(f"⚠️  Index '{INDEX_NAME}' already exists")
        return
    
    # Create index
    pinecone.create_index(
        name=INDEX_NAME,
        dimension=10,  # Number of features in player vector
        metric='cosine',  # Similarity metric
        pods=1,
        pod_type='p1.x1'
    )
    print(f"✅ Created index '{INDEX_NAME}'")

def get_index():
    """Get Pinecone index"""
    return pinecone.Index(INDEX_NAME)

def create_player_vector(player_stats: Dict) -> List[float]:
    """
    Convert player statistics to vector for similarity search
    
    Features (10 dimensions):
    1. Points per game
    2. Assists per game
    3. Rebounds per game
    4. Steals per game
    5. Blocks per game
    6. Field goal percentage
    7. Three point percentage
    8. Minutes per game
    9. Turnovers per game (negative feature)
    10. Usage (normalized)
    """
    
    vector = [
        player_stats.get('avg_points', 0) / 40.0,
        player_stats.get('avg_assists', 0) / 15.0,
        player_stats.get('avg_rebounds', 0) / 15.0,
        player_stats.get('avg_steals', 0) / 5.0,
        player_stats.get('avg_blocks', 0) / 5.0,
        player_stats.get('field_goal_pct', 0) / 100.0,
        player_stats.get('three_point_pct', 0) / 100.0,
        player_stats.get('avg_minutes', 0) / 48.0,
        1 - (player_stats.get('avg_turnovers', 0) / 10.0),
        player_stats.get('usage_rate', 20) / 40.0
    ]
    
    return vector

def upsert_player(player_id: int, player_stats: Dict, metadata: Dict):
    """Add or update player in Pinecone"""
    index = get_index()
    
    # Create vector from stats
    vector = create_player_vector(player_stats)
    
    # Upsert to Pinecone
    index.upsert(
        vectors=[
            {
                'id': str(player_id),
                'values': vector,
                'metadata': metadata
            }
        ]
    )
    print(f"✅ Upserted player {player_id} to Pinecone")

def find_similar_players(player_id: int, top_k: int = 5) -> List[Dict]:
    """Find similar players"""
    index = get_index()
    
    # Query for similar players
    results = index.query(
        id=str(player_id),
        top_k=top_k + 1,
        include_metadata=True
    )
    
    # Filter out the player itself and return results
    similar_players = [
        {
            'player_id': int(match['id']),
            'similarity_score': match['score'],
            'metadata': match['metadata']
        }
        for match in results['matches']
        if match['id'] != str(player_id)
    ]
    
    return similar_players[:top_k]

def delete_player(player_id: int):
    """Remove player from Pinecone"""
    index = get_index()
    index.delete(ids=[str(player_id)])
    print(f"✅ Deleted player {player_id} from Pinecone")