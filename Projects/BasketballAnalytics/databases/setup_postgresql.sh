echo "Setting up PostgreSQL..."

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "PostgreSQL not installed"
    echo "Install with: brew install postgresql@15"
    exit 1
fi

# Check if PostgreSQL is running
if ! pg_isready &> /dev/null; then
    echo "PostgreSQL not running"
    echo "Starting PostgreSQL..."
    brew services start postgresql@15
    sleep 2
fi

# Create database
echo "Creating database..."
createdb basketball_db 2>/dev/null || echo "   Database already exists"

# Run initialization script
echo "Running schema..."
psql basketball_db < database/postgresql/init.sql

echo "PostgreSQL setup complete!"