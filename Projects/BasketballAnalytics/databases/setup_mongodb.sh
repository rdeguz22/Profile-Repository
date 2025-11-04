echo "Setting up MongoDB..."

# Check if MongoDB is installed
if ! command -v mongosh &> /dev/null; then
    echo "MongoDB not installed"
    echo "Install with: brew install mongodb-community"
    exit 1
fi

# Check if MongoDB is running
if ! pgrep -x mongod &> /dev/null; then
    echo "MongoDB not running"
    echo " Starting MongoDB..."
    brew services start mongodb-community
    sleep 3
fi

# Run initialization script
echo "Creating collections..."
mongosh < database/mongodb/init.js

echo "MongoDB setup complete!"