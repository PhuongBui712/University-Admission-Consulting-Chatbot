# Transform .env file from KEY="value" to KEY=value
# Make sure running that file at directory has .env file
sed 's/\"//g' .env > .env.tmp