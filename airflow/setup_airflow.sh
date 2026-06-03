#!/bin/bash

# Airflow Setup Script for Restaurant Booking Application
# This script initializes Airflow and prepares it for use with Django

set -e

echo "🍽️  Restaurant Booking - Airflow Setup"
echo "======================================"

# Check if Airflow is installed
if ! command -v airflow &> /dev/null; then
    echo "❌ Airflow is not installed. Please install it first:"
    echo "   pip install apache-airflow"
    exit 1
fi

# Set AIRFLOW_HOME
export AIRFLOW_HOME="${AIRFLOW_HOME:=$HOME/airflow}"
echo "📁 Setting AIRFLOW_HOME to: $AIRFLOW_HOME"

# Create necessary directories
mkdir -p $AIRFLOW_HOME/{dags,logs,plugins,config}
echo "✅ Created Airflow directories"

# Initialize the database
echo ""
echo "🗄️  Initializing Airflow database..."
airflow db init
echo "✅ Database initialized"

# Create default user
echo ""
echo "👤 Creating default admin user..."
airflow users create \
    --role Admin \
    --username admin \
    --email admin@restaurant.com \
    --firstname Restaurant \
    --lastname Admin \
    --password admin123 \
    2>/dev/null || echo "⚠️  User might already exist"
echo "✅ Admin user ready"

# Set Django settings for Airflow
echo ""
echo "⚙️  Configuring Django integration..."
export DJANGO_SETTINGS_MODULE=restaurant_booking.settings
echo "✅ Django settings configured"

# Copy DAGs to Airflow dags folder
if [ -d "airflow/dags" ]; then
    echo ""
    echo "📋 Installing DAGs..."
    cp airflow/dags/*.py $AIRFLOW_HOME/dags/
    echo "✅ DAGs installed"
else
    echo "⚠️  DAGs directory not found at airflow/dags/"
fi

# Create plugins directory for custom operators if needed
mkdir -p $AIRFLOW_HOME/plugins
echo "✅ Plugins directory created"

# Set permissions
chmod -R 755 $AIRFLOW_HOME
echo "✅ Permissions set"

echo ""
echo "======================================"
echo "✅ Setup Complete!"
echo ""
echo "📝 Next steps:"
echo "1. Start the web server:"
echo "   airflow webserver --port 8080"
echo ""
echo "2. In another terminal, start the scheduler:"
echo "   airflow scheduler"
echo ""
echo "3. Access the UI at http://localhost:8080"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "📚 For more information, visit:"
echo "   https://airflow.apache.org/docs/"
echo "======================================"
