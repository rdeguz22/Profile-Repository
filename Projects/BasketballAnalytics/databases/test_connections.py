import psycopg2
from pymongo import MongoClient
import sys

def test_postgresql():
    """Test PostgreSQL connection"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="basketball_db",
            user="postgres",
            password="password"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        cursor.close()
        conn.close()
        print("PostgreSQL Connected!")
        print(f"   Version: {version[0][:50]}...")
        return True
    except Exception as e:
        print(f"PostgreSQL Connection Failed: {e}")
        return False

def test_mongodb():
    """Test MongoDB connection"""
    try:
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
        client.server_info()
        db = client.basketball_db
        collections = db.list_collection_names()
        print("MongoDB Connected!")
        print(f"   Collections: {collections if collections else 'None yet'}")
        client.close()
        return True
    except Exception as e:
        print(f"MongoDB Connection Failed: {e}")
        return False

def test_pinecone():
    """Test Pinecone connection (optional)"""
    try:
        import pinecone
        api_key = "your-api-key"
        
        if not api_key or api_key == "your-api-key":
            print("Pinecone: API key not configured (optional)")
            return None
        
        pinecone.init(api_key=api_key, environment="us-west1-gcp")
        indexes = pinecone.list_indexes()
        print("Pinecone Connected!")
        print(f"   Indexes: {indexes}")
        return True
    except Exception as e:
        print(f"Pinecone: {e} (optional)")
        return None

if __name__ == "__main__":
    print("🔍 Testing Database Connections...\n")
    
    pg_ok = test_postgresql()
    mongo_ok = test_mongodb()
    pinecone_ok = test_pinecone()
    
    print("\n" + "="*50)
    print("SUMMARY:")
    print(f"PostgreSQL: {'Connected' if pg_ok else 'Failed'}")
    print(f"MongoDB:    {'Connected' if mongo_ok else 'Failed'}")
    print(f"Pinecone:   {'Connected' if pinecone_ok else 'Not configured (optional)'}")
    print("="*50)
    
    if not (pg_ok and mongo_ok):
        print("\nRequired databases are not connected!")
        print("   Fix the connection issues before proceeding.")
        sys.exit(1)
    else:
        print("\nAll required databases are connected!")
        sys.exit(0)