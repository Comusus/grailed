#Utils.py: Helpful Methods that are used many times.

import sqlite3
import argparse
from shutil import copyfile

def connectDB(path):
	""" Create a connection to the .sqlite3 file.
		
		Args:
			- path: String of Path to Database file

		Returns:
			- conn: sqlite3.Connection object
	"""
	return sqlite3.connect(path)


def getPath():
	""" Returns the local path to the Database in
		this file system.

		Returns:
			- DB_PATH: 
	"""

	DB_NAME = 'grailed-exercise.sqlite3'
	DB_PATH = './database/' + DB_NAME # Update if DB name or location changes
	return DB_PATH


def updateName(s, iD, newName):
    """ Update the username column in the row of the userID 
        in the Users Table.

        Args:
            - s: Cursor Object to move through DB 
            - iD: Integer of user ID 
            - newName: String of New Name
    """
    query = ''' UPDATE USERS SET username=? WHERE id=? '''
    s.execute(query, (newName, iD))


def createParser():
	""" Creates an argument parser that can run the functions
	    in dry run mode by adding -dry_run when running script
	"""
	parser = argparse.ArgumentParser(description="Clean Up Usernames")
	parser.add_argument("-dry_run", action='store_true')
	return parser


def checkDuplicatesAllowed(path):
	""" Returns True if there are no duplicates among users
		with non disallowed names

		Args:
			- path: String of Path of the Database

		Returns:
			- hasDuplicates: Boolean True if no Duplicaaes else False 
	"""
	conn = connectDB(path)
	c = conn.cursor()

	query = ''' SELECT users.username
				FROM USERS
				LEFT OUTER JOIN disallowed_usernames
				ON users.username = disallowed_usernames.invalid_username
				WHERE disallowed_usernames.invalid_username IS NULL
				ORDER BY users.username
			'''

	usernames = set([])

	for row in c.execute(query):
		if row[0] in usernames:
			return False
		else:
			usernames.add(row[0])

	return True


def checkDuplicatesAll(path):
	""" Returns True if there are no duplicates in the usernames table.
		
		Args:
			- path: String of Path of the Database

		Returns: 
			- hasDuplicates: Boolean True if no Duplicaaes else False 
	"""
	conn = connectDB(path)
	c = conn.cursor()

	usernames = set([])
	query = ''' SELECT username
				FROM USERS
			'''

	for row in c.execute(query):
		if row[0] in usernames:
			return False
		else:
			usernames.add(row[0])

	return True


def resetDB(copy_path, path):
	""" Overwrites database back to original using a copy
		of the original version.
		
		Args:
			- copy_path: String Path of the Copy
			- path: String Path of the Database

		Returns:
			None
	"""
	copyfile(copy_path, path)


if __name__ == "__main__":
	# running util.py will reset database for quick way to reset
	DB_COPY_PATH = './database/original-grailed-exercise.sqlite3' 
	resetDB(DB_COPY_PATH, getPath())