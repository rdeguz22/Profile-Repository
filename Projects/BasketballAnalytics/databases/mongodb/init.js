const { MongoClient } = require("mongodb");

const uri = "mongodb://localhost:27017";
const client = new MongoClient(uri);

async function run() {
  try {
    await client.connect();
    const db = client.db("basketball_db");

    // Game Events Collection
    await db.createCollection("game_events", {
      validator: {
        $jsonSchema: {
          bsonType: "object",
          required: ["game_id", "event_type", "player_name", "quarter", "timestamp"],
          properties: {
            game_id: {
              bsonType: "int",
              description: "Reference to game ID"
            },
            event_type: {
              bsonType: "string",
              enum: ["shot_made", "shot_missed", "three_pointer", "free_throw", 
                     "assist", "rebound", "steal", "block", "foul", "turnover"],
              description: "Type of game event"
            },
            player_id: {
              bsonType: "int",
              description: "Reference to player ID"
            },
            player_name: {
              bsonType: "string",
              description: "Player name"
            },
            team: {
              bsonType: "string",
              description: "Team name"
            },
            quarter: {
              bsonType: "int",
              minimum: 1,
              maximum: 5,
              description: "Quarter number (1-4, 5 for OT)"
            },
            time_remaining: {
              bsonType: "string",
              description: "Time remaining in quarter (MM:SS)"
            },
            description: {
              bsonType: "string",
              description: "Event description"
            },
            timestamp: {
              bsonType: "date",
              description: "When event occurred"
            }
          }
        }
      }
    });

    // Index for querying events by game
    await db.collection("game_events").createIndex({ "game_id": 1 });

    // Index for querying events by timestamp
    await db.collection("game_events").createIndex({ "timestamp": -1 });

    // Index for querying events by player
    await db.collection("game_events").createIndex({ "player_id": 1 });

    // Compound index for game events sorted by time
    await db.collection("game_events").createIndex({ "game_id": 1, "timestamp": 1 });

    console.log("Database setup complete.");
  } finally {
    await client.close();
  }
}

run().catch(console.dir);

// Game Events Collection
db.createCollection("game_events", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["game_id", "event_type", "player_name", "quarter", "timestamp"],
      properties: {
        game_id: {
          bsonType: "int",
          description: "Reference to game ID"
        },
        event_type: {
          bsonType: "string",
          enum: ["shot_made", "shot_missed", "three_pointer", "free_throw", 
                 "assist", "rebound", "steal", "block", "foul", "turnover"],
          description: "Type of game event"
        },
        player_id: {
          bsonType: "int",
          description: "Reference to player ID"
        },
        player_name: {
          bsonType: "string",
          description: "Player name"
        },
        team: {
          bsonType: "string",
          description: "Team name"
        },
        quarter: {
          bsonType: "int",
          minimum: 1,
          maximum: 5,
          description: "Quarter number (1-4, 5 for OT)"
        },
        time_remaining: {
          bsonType: "string",
          description: "Time remaining in quarter (MM:SS)"
        },
        description: {
          bsonType: "string",
          description: "Event description"
        },
        timestamp: {
          bsonType: "date",
          description: "When event occurred"
        }
      }
    }
  }
});

// Index for querying events by game
db.game_events.createIndex({ "game_id": 1 });

// Index for querying events by timestamp
db.game_events.createIndex({ "timestamp": -1 });

// Index for querying events by player
db.game_events.createIndex({ "player_id": 1 });

// Compound index for game events sorted by time
db.game_events.createIndex({ "game_id": 1, "timestamp": 1 });

// Get all events for a game
db.game_events.find({ game_id: 1 }).sort({ timestamp: 1 });

// Get events by quarter
db.game_events.find({ game_id: 1, quarter: 4 }).sort({ timestamp: -1 });

// Get events by player
db.game_events.find({ player_name: "LeBron James" });

// Count events by type
db.game_events.aggregate([
  { $group: { _id: "$event_type", count: { $sum: 1 } } },
  { $sort: { count: -1 } }
]);

// Get latest events
db.game_events.find().sort({ timestamp: -1 }).limit(10);