# Make sure running this script at the root which has backend directory

#!/bin/sh
exec exec uvicorn app.server:app --host 0.0.0.0 --port 8000