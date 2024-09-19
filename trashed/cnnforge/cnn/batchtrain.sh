#!/bin/bash

while true; do
	for dir in ../data/ready/*; do
		mv $dir ../data/ready/batchx	# batch currently being executed
		./traincnn.py
		echo "-- $dir DONE --"
		mv ../data/ready/batchx $dir
	done
	echo "-- GLOBAL EPOCH COMPLETE --"
done
