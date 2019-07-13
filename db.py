#Utility.py: Helpful Methods that are used many times.

import sqlite3
import argparse

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
	return 2
