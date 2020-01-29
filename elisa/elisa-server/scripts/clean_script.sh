#!/bin/bash
echo "Setting default user for DB login -> postgres"
# Has the highest privileges
USER="postgres"
if [[ -z "$1" ]]; then
echo "SQL file not specified!"
exit 1
elif [[ -n "$1" ]]; then
echo "DB file is -> $1"
fi
echo "Accessing postgres DB with user -> $USER"
psql -U $USER -f $1
echo "psql command finished."
read -p 'Would you like to remove django migration files as well? If yes type y/Y -> ' option
if [[ "$option" == "y" ]] || [[ "$option" == "Y" ]]; then
echo "Running python script"
# it is executable
python delete_migration_files.py
fi
echo "Script finished running!"
exit 0