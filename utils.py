#Utility.py: Helpful Methods that are used many times.

import sqlite3
import argparse
from shutil import copyfile

DB_NAME = 'grailed-exercise.sqlite3'
DB_PATH = './database/' + DB_NAME

def connectDB():
	""" Create a connection to the .sqlite3 file.

		Returns:
			conn - sqlite3.Connection object

	"""
	DB_NAME = 'grailed-exercise.sqlite3'
	DB_PATH = './database/' + DB_NAME # Update if DB name or location changes
	conn = sqlite3.connect(DB_PATH)
	return conn

def createParser():
	""" Create an argument parser that can run the functions
	    in dry run mode
	"""
	parser = argparse.ArgumentParser(description="Clean Up Usernames")
	parser.add_argument("-dry_run", action='store_true')
	return parser
	# parser.add_argument("-dry_run", action='store_true')


def resetDB():
	DB_NAME = 'grailed-exercise.sqlite3'
	DB_PATH = './database/' + DB_NAME
	DB_COPY_PATH = './database/original-grailed-exercise.sqlite3' 
	copyfile(DB_COPY_PATH, DB_PATH)

if __name__ == "__main__":
	resetDB()