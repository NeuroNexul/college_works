### Initialize the Database: Open your terminal in the /backend directory (make sure your virtual environment is active). Run these commands:

```bash
# This creates the 'migrations' folder
flask db init

# This creates the first migration file based on your models
flask db migrate -m "Initial migration with all models"

# This applies the migration to create the actual .db file and tables
flask db upgrade
```
