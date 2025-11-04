echo "BASKETBALL PLATFORM - DATABASE SETUP"

echo "Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo "Python not installed"
    exit 1
fi
echo "Python installed"

if ! command -v psql &> /dev/null; then
    echo "PostgreSQL not installed"
    echo "Install: brew install postgresql@15"
    exit 1
fi
echo "PostgreSQL installed"

if ! command -v mongosh &> /dev/null; then
    echo "MongoDB not installed"
    echo "   Install: brew install mongodb-community"
    exit 1
fi
echo "MongoDB installed"

echo ""

echo "Starting databases..."

if ! pg_isready &> /dev/null; then
    brew services start postgresql@15
    echo "Started PostgreSQL"
    sleep 2
else
    echo "PostgreSQL already running"
fi

if ! pgrep -x mongod &> /dev/null; then
    brew services start mongodb-community
    echo "Started MongoDB"
    sleep 3
else
    echo "MongoDB already running"
fi

echo ""

echo "🏗️  Creating databases..."

createdb basketball_db 2>/dev/null && echo "Created PostgreSQL database" || echo "PostgreSQL database already exists"

echo ""

echo "Initializing schemas..."

if [ -f "database/postgresql/init.sql" ]; then
    psql basketball_db < database/postgresql/init.sql > /dev/null 2>&1
    echo "PostgreSQL schema created"
else
    echo "PostgreSQL init.sql not found"
fi

if [ -f "database/mongodb/init.js" ]; then
    mongosh basketball_db < database/mongodb/init.js > /dev/null 2>&1
    echo "MongoDB collections created"
else
    echo "MongoDB init.js not found"
fi

echo ""

echo "Testing connections..."

cd backend
source venv/bin/activate 2>/dev/null || true

if [ -f "database/test_connections.py" ]; then
    python database/test_connections.py
else
    echo "Test script not found, skipping tests"
fi

echo ""

echo "Do you want to seed sample data? (y/n)"
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    if [ -f "database/seed_all.py" ]; then
        python database/seed_all.py
    else
        echo "Seed script not found"
    fi
else
    echo "Skipping data seeding"
fi

echo ""

echo "SETUP COMPLETE"
echo ""
echo "Next steps:"
echo "  1. cd backend"
echo "  2. uvicorn main:app --reload"
echo "  3. cd ../frontend"
echo "  4. npm start"
echo ""
echo "Visit http://localhost:3000 to use your app"