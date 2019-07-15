#Test.py: Unit Testing different test cases for Built Functions.

import sqlite3
import unittest
from utils import *
import resolveCollisions
import resolveDisallowed
import findDisallowedUsers


DB_PATH = getPath()
DB_COPY_PATH = './database/original-grailed-exercise.sqlite3' 
TOY_DB_PATH = './database/test.sqlite3'


def resetTestDB():
	""" Resets the Test Database by removing all records
		from the USERS and DISALLOWED_USERS tables.
	"""
	conn = sqlite3.connect(TOY_DB_PATH)
	c = conn.cursor()

	clearUsers = ''' DELETE FROM USERS '''
	clearDisallowed = ''' DELETE FROM DISALLOWED_USERNAMES '''
	c.execute(clearUsers)
	c.execute(clearDisallowed)
	conn.commit() # Remove all records from USERS and DISALLOWED_USERS

	c.close()
	conn.close()

class TestDBMethods(unittest.TestCase):
	""" Testing DB functions on the given grails-exercise.sqlite3 file """

	def testcheckDuplicates(self):
		""" Making Sure there are duplicates """
		resetDB(DB_COPY_PATH, getPath()) #getPath() == given local DB path
		self.assertFalse(checkDuplicatesAllowed(getPath()))
		self.assertFalse(checkDuplicatesAll(getPath()))


	def testResolveCollisions(self):
		""" Testing to see if Database resolves collisions """
		resetDB(DB_COPY_PATH, getPath())
		resolveCollisions.resolveUsernameCollisions(getPath())
		self.assertTrue(checkDuplicatesAll(getPath()))


	def testResolveDisallowed(self):
		""" Testing to see if Disallowed usernames are fixed """
		resetDB(DB_COPY_PATH, getPath())
		# 1. check duplicates exist -- row is list of disallowed user tuples
		row = findDisallowedUsers.returnDisallowedUsers(getPath())
		self.assertTrue(len(row) > 0)
		resolveDisallowed.resolveDisallowedUsers(getPath())
		# 2. list of tuples should be empty after resolving disallowed
		row = findDisallowedUsers.returnDisallowedUsers(getPath())
		self.assertEqual(len(row), 0)
		

	def testResolvingBoth(self):
		""" Resolving Duplicates and Disallowed should fix both """
		resetDB(DB_COPY_PATH, getPath())
		resolveDisallowed.resolveDisallowedUsers(getPath())
		resolveCollisions.resolveUsernameCollisions(getPath())
		self.assertTrue(checkDuplicatesAll(getPath()))
		row = findDisallowedUsers.returnDisallowedUsers(getPath())
		self.assertEqual(len(row), 0)

		# both directions should be the same
		resetDB(DB_COPY_PATH, getPath())
		resolveCollisions.resolveUsernameCollisions(getPath())
		resolveDisallowed.resolveDisallowedUsers(getPath())
		self.assertTrue(checkDuplicatesAll(getPath()))
		row = findDisallowedUsers.returnDisallowedUsers(getPath())
		self.assertEqual(len(row), 0)


class resolveCollisionTests(unittest.TestCase):
	""" Testing resolveUsername Collisions on small test cases"""

	def testCollisions1(self):
		""" Foo1, Foo1, Foo3 --> Foo1, Foo2, Foo3"""
		resetTestDB()
		conn = connectDB(TOY_DB_PATH)
		c = conn.cursor()

		# Add To USERS Table
		c.execute(''' INSERT INTO USERS VALUES (1, "foo") ''')
		c.execute(''' INSERT INTO USERS VALUES (2, "foo") ''')
		c.execute(''' INSERT INTO USERS VALUES (3, "foo") ''')

		conn.commit()

		resolveCollisions.resolveUsernameCollisions(TOY_DB_PATH)

		c.execute(''' SELECT * FROM USERS ''')

		rows = c.fetchall()

		self.assertEqual(rows[0], (1, "foo"))
		self.assertEqual(rows[1], (2, "foo1"))
		self.assertEqual(rows[2], (3, "foo2"))

		c.close()
		conn.close()


	def testCollisions2(self):
		""" Foo, Foo, Foo | Banned = [Foo1] --> Foo, Foo2, Foo3 """
		resetTestDB()
		conn = connectDB(TOY_DB_PATH)
		c = conn.cursor()

		# Add To USERS Table
		c.execute(''' INSERT INTO USERS VALUES (1, "foo") ''')
		c.execute(''' INSERT INTO USERS VALUES (2, "foo") ''')
		c.execute(''' INSERT INTO USERS VALUES (3, "foo") ''')
		c.execute(''' INSERT INTO DISALLOWED_USERNAMES 
					  VALUES (1, "foo1", "2018-06-15", "2018-06-15") 
				  ''')

		conn.commit()

		resolveCollisions.resolveUsernameCollisions(TOY_DB_PATH)

		c.execute(''' SELECT * FROM USERS ''')

		rows = c.fetchall()
		self.assertEqual(rows[0], (1, "foo"))
		self.assertEqual(rows[1], (2, "foo2"))
		self.assertEqual(rows[2], (3, "foo3"))

		c.close()
		conn.close()


	def testCollisions3(self):
		""" 12345, 12345, 123451 --> 12345 123452 123451 """
		resetTestDB()
		conn = connectDB(TOY_DB_PATH)
		c = conn.cursor()

		# Add To USERS Table
		c.execute(''' INSERT INTO USERS VALUES (1, "12345") ''')
		c.execute(''' INSERT INTO USERS VALUES (2, "12345") ''')
		c.execute(''' INSERT INTO USERS VALUES (3, "123451") ''')

		conn.commit()

		resolveCollisions.resolveUsernameCollisions(TOY_DB_PATH)

		c.execute(''' SELECT * FROM USERS ''')

		rows = c.fetchall()
		self.assertEqual(rows[0], (1, "12345"))
		self.assertEqual(rows[1], (2, "123452"))
		self.assertEqual(rows[2], (3, "123451"))

		c.close()
		conn.close()

	def testCollisions4(self):
		""" 12345, 12345, 123451 --> 12345 123452 123451 """
		resetTestDB()
		conn = connectDB(TOY_DB_PATH)
		c = conn.cursor()

		# Add To USERS Table
		c.execute(''' INSERT INTO USERS VALUES (1, "12345") ''')
		c.execute(''' INSERT INTO USERS VALUES (2, "1234 5") ''')

		conn.commit()

		resolveCollisions.resolveUsernameCollisions(TOY_DB_PATH)

		c.execute(''' SELECT * FROM USERS ''')

		# Expected No Change since no collision
		rows = c.fetchall()
		self.assertEqual(rows[0], (1, "12345"))
		self.assertEqual(rows[1], (2, "1234 5"))

		c.close()
		conn.close()

	def testCollisions5(self):
		""" Testing more Collisions """
		resetTestDB()
		conn = connectDB(TOY_DB_PATH)
		c = conn.cursor()

		# Add To USERS Table
		c.execute(''' INSERT INTO USERS VALUES (1, "foo1") ''')
		c.execute(''' INSERT INTO USERS VALUES (2, "foo1") ''')
		c.execute(''' INSERT INTO USERS VALUES (3, "foo1") ''')
		c.execute(''' INSERT INTO USERS VALUES (4, "foo11") ''')
		c.execute(''' INSERT INTO USERS VALUES (5, "foo11") ''')
		c.execute(''' INSERT INTO USERS VALUES (6, "foo11") ''')
		c.execute(''' INSERT INTO USERS VALUES (7, "foo") ''')
		c.execute(''' INSERT INTO USERS VALUES (8, "foo") ''')
		c.execute(''' INSERT INTO USERS VALUES (9, "foo") ''')
		conn.commit()

		resolveCollisions.resolveUsernameCollisions(TOY_DB_PATH)

		c.execute(''' SELECT * FROM USERS ''')

		rows = c.fetchall()
		self.assertEqual(rows[0], (1, "foo1"))
		self.assertEqual(rows[1], (2, "foo12"))
		self.assertEqual(rows[2], (3, "foo13"))
		self.assertEqual(rows[3], (4, "foo11"))
		self.assertEqual(rows[4], (5, "foo111"))
		self.assertEqual(rows[5], (6, "foo112"))
		self.assertEqual(rows[6], (7, "foo"))
		self.assertEqual(rows[7], (8, "foo2"))
		self.assertEqual(rows[8], (9, "foo3"))

		c.close()
		conn.close()


class resolveDisallowedUsers(unittest.TestCase):
	""" Unit Tests for Disallowed Users"""

	def testDisallowed1(self):
		""" Banned = [foo] => foo, foo, foo --> foo1, foo2, foor3 """
		resetTestDB()
		conn = connectDB(TOY_DB_PATH)
		c = conn.cursor()

		# Add To USERS Table
		c.execute(''' INSERT INTO USERS VALUES (1, "foo") ''')
		c.execute(''' INSERT INTO USERS VALUES (2, "foo") ''')
		c.execute(''' INSERT INTO USERS VALUES (3, "foo") ''')
		c.execute(''' INSERT INTO DISALLOWED_USERNAMES 
					  VALUES (1, "foo", "2018-06-15", "2018-06-15") 
				  ''')

		conn.commit()

		# Also test findDisallowedUsers using ReturnDiallowedUsers
		self.assertEqual(
			len(findDisallowedUsers.returnDisallowedUsers(TOY_DB_PATH)), 3)

		resolveDisallowed.resolveDisallowedUsers(TOY_DB_PATH)

		c.execute(''' SELECT * FROM USERS ''')

		# Expected No Duplicates
		rows = c.fetchall()
		self.assertEqual(rows[0], (1, "foo1"))
		self.assertEqual(rows[1], (2, "foo2"))
		self.assertEqual(rows[2], (3, "foo3"))

		c.close()
		conn.close()

	def testDisallowed2(self):
		""" Banned = [foo, foo1, foo2] => 
				foo, foo, foo --> foo3, foo4, foor5 """
		resetTestDB()
		conn = connectDB(TOY_DB_PATH)
		c = conn.cursor()

		# Add To USERS Table
		c.execute(''' INSERT INTO USERS VALUES (1, "foo") ''')
		c.execute(''' INSERT INTO USERS VALUES (2, "foo") ''')
		c.execute(''' INSERT INTO USERS VALUES (3, "foo") ''')
		c.execute(''' INSERT INTO DISALLOWED_USERNAMES 
					  VALUES (1, "foo", "2018-06-15", "2018-06-15") 
				  ''')
		c.execute(''' INSERT INTO DISALLOWED_USERNAMES 
					  VALUES (2, "foo1", "2018-06-15", "2018-06-15") 
				  ''')
		c.execute(''' INSERT INTO DISALLOWED_USERNAMES 
					  VALUES (3, "foo2", "2018-06-15", "2018-06-15") 
				  ''')

		conn.commit()

		self.assertEqual(
			len(findDisallowedUsers.returnDisallowedUsers(TOY_DB_PATH)), 3)

		resolveDisallowed.resolveDisallowedUsers(TOY_DB_PATH)

		c.execute(''' SELECT * FROM USERS ''')

		# Expected No additional Disallowed Words
		rows = c.fetchall()
		self.assertEqual(rows[0], (1, "foo3"))
		self.assertEqual(rows[1], (2, "foo4"))
		self.assertEqual(rows[2], (3, "foo5"))

		c.close()
		conn.close()

	def testDisallowed3(self):
		""" Banned = [foo, foo1, foo3] =>
				foo, foo, foo => foo2, foo4, foo5
		""" 
		resetTestDB()
		conn = connectDB(TOY_DB_PATH)
		c = conn.cursor()

		# Add To USERS Table
		c.execute(''' INSERT INTO USERS VALUES (1, "foo") ''')
		c.execute(''' INSERT INTO USERS VALUES (2, "foo") ''')
		c.execute(''' INSERT INTO USERS VALUES (3, "foo") ''')
		c.execute(''' INSERT INTO DISALLOWED_USERNAMES 
					  VALUES (1, "foo", "2018-06-15", "2018-06-15") 
				  ''')
		c.execute(''' INSERT INTO DISALLOWED_USERNAMES 
					  VALUES (2, "foo1", "2018-06-15", "2018-06-15") 
				  ''')
		c.execute(''' INSERT INTO DISALLOWED_USERNAMES 
					  VALUES (3, "foo3", "2018-06-15", "2018-06-15") 
				  ''')

		conn.commit()

		self.assertEqual(
			len(findDisallowedUsers.returnDisallowedUsers(TOY_DB_PATH)), 3)

		resolveDisallowed.resolveDisallowedUsers(TOY_DB_PATH)

		c.execute(''' SELECT * FROM USERS ''')

		# Expected No Change since no collision
		rows = c.fetchall()
		self.assertEqual(rows[0], (1, "foo2"))
		self.assertEqual(rows[1], (2, "foo4"))
		self.assertEqual(rows[2], (3, "foo5"))

		c.close()
		conn.close()

	def testDisallowed4(self):
		""" Banned = [foo, foo2, foo4] =>
				foo, foo2, foo, foo21, foo => foo1, foo22, foo3, foo21, foo5
		""" 
		resetTestDB()
		conn = connectDB(TOY_DB_PATH)
		c = conn.cursor()

		# Add To USERS Table
		c.execute(''' INSERT INTO USERS VALUES (1, "foo") ''')
		c.execute(''' INSERT INTO USERS VALUES (2, "foo2") ''')
		c.execute(''' INSERT INTO USERS VALUES (3, "foo") ''')
		c.execute(''' INSERT INTO USERS VALUES (4, "foo21") ''')
		c.execute(''' INSERT INTO USERS VALUES (5, "foo") ''')
		c.execute(''' INSERT INTO DISALLOWED_USERNAMES 
					  VALUES (1, "foo", "2018-06-15", "2018-06-15") 
				  ''')
		c.execute(''' INSERT INTO DISALLOWED_USERNAMES 
					  VALUES (2, "foo2", "2018-06-15", "2018-06-15") 
				  ''')
		c.execute(''' INSERT INTO DISALLOWED_USERNAMES 
					  VALUES (3, "foo4", "2018-06-15", "2018-06-15") 
				  ''')

		conn.commit()

		self.assertEqual(
			len(findDisallowedUsers.returnDisallowedUsers(TOY_DB_PATH)), 4)

		resolveDisallowed.resolveDisallowedUsers(TOY_DB_PATH)

		c.execute(''' SELECT * FROM USERS ''')

		rows = c.fetchall()
		self.assertEqual(rows[0], (1, "foo1"))
		self.assertEqual(rows[1], (2, "foo22"))
		self.assertEqual(rows[2], (3, "foo3"))
		self.assertEqual(rows[3], (4, "foo21"))
		self.assertEqual(rows[4], (5, "foo5"))


		c.close()
		conn.close()


	def testDisallowed5(self):
		""" Testing on a bigger database """

		resetTestDB()
		conn = connectDB(TOY_DB_PATH)
		c = conn.cursor()

		# Add To USERS Table
		for i in range(1,1001):
			c.execute(''' INSERT INTO USERS VALUES ({}, "foo") '''.format(i))
		c.execute(''' INSERT INTO DISALLOWED_USERNAMES 
				  VALUES (1, "foo", "2018-06-15", "2018-06-15")
				  ''') 

		conn.commit()

		self.assertEqual(
			len(findDisallowedUsers.returnDisallowedUsers(TOY_DB_PATH)), 1000)

		resolveDisallowed.resolveDisallowedUsers(TOY_DB_PATH)

		c.execute(''' SELECT * FROM USERS ''')

		rows = c.fetchall()
		self.assertEqual(rows[0], (1, "foo1"))
		self.assertEqual(rows[999], (1000, "foo1000"))

		c.close()
		conn.close()


if __name__ == '__main__':
	resetDB(DB_COPY_PATH, TOY_DB_PATH) # makes toy db using original structure
	unittest.main() 
	resetDB(DB_COPY_PATH, getPath()) # returns grailed-exercise to normal
