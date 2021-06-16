#!/usr/bin/sh


# INSTALL ENVIRONMENT
source conf/app-profile.sh
python3 -m venv .venv3
source .venv3/bin/activate
pip install $PIP_OPTIONS --upgrade pip pypandoc
pip install $PIP_OPTIONS -e .[dev]


# MOVE CSV FILES TO THE HISTO DIRECTORY
YEAR=`date +%Y`
MONTH=`date +%m`
DAY=`date +%d`

RATINGS_DIR="ratings"
SEARCHS_DIR="user_actions"

for file in $DATA/*;
do
	if [ "${file##*/}" == "ratings.csv" ]
	then
		mkdir -p $HISTO/$RATINGS_DIR/$YEAR/$MONTH/$DAY
		mv "$file" "$HISTO/$RATINGS_DIR/$YEAR/$MONTH/$DAY";
	elif [ "${file##*/}" == "user_actions.csv" ]
	then
		mkdir -p $HISTO/$SEARCHS_DIR/$YEAR/$MONTH/$DAY
		mv "$file" "$HISTO/$SEARCHS_DIR/$YEAR/$MONTH/$DAY";
	fi
done


# TRAIN THE MODELS
python $REPO/$PACKAGE_DIR/pipeline/train_pipeline.py
