#!/bin/bash

while :
do
	python3 post_accumulator.py
	python3 comment_accumulator.py

	echo "Complete, next scrape in 1 hour"

	sleep 1h
done
