#Test.py: Unit Testing different test cases for Built Functions.

import sqlite3
import unittest
from shutil import copyfile
from db import connectDB
from resolveCollisions import *


DB_NAME = 'grailed-exercise.sqlite3'
DB_PATH = './database/' + DB_NAME
DB_COPY_PATH = './database/original-grailed-exercise.sqlite3' 

def resetDatabase():
	copyfile(DB_COPY_PATH, DB_PATH)

def getAllowedNames():
	conn = connectDB()
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
			print('meeepapsdpasdpasdpasdpasdp', row[0])
			return False
		else:
			usernames.add(row[0])

	return True

def checkDuplicates():
	""" Returns True if there are no duplicates in the usernames table
	
		Returns: hasDuplicates - Boolean
	"""
	conn = connectDB()
	c = conn.cursor()

	usernames = set([])
	query = ''' SELECT username
				FROM users
			'''

	for row in c.execute(query):
		if row[0] in usernames:
			return False
		else:
			usernames.add(row[0])

	return True



class TestDBMethods(unittest.TestCase):

	def testcheckDuplicates(self):
		resetDatabase()
		self.assertEqual(checkDuplicates(), False)


	def testResolveCollisions(self):
		""" Testing to see if Database resolves collisions """
		resetDatabase()
		resolveUsernameCollisions()

		self.assertTrue(getAllowedNames())


# resolving a collision can create another collision, i.e. Foo1, Foo1, Foo3


# 123456, 123456 --> 123456, 1234561 or 123457



if __name__ == '__main__':
	unittest.main()
	resetDatabase()
	# print(getAllowedNames())

# banned names
# grailed, grailed1,
# 