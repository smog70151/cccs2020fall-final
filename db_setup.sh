rm -rf migrations
python3 dbModel.py db init
python3 dbModel.py db migrate
python3 dbModel.py db upgrade
