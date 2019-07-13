# resolveDisallowed.py: Methods to resolve usernames that are disallowed. 

from utils import connectDB, createParser
from resolveCollisions import updateName

def getDisallowedNames(conn):
	""" Returns a set of all illegitimate disallowed usernames.

		Args:
			- conn: sqlite3.Connection object 
	"""
	c = conn.cursor()
	query = ''' SELECT invalid_username
				FROM disallowed_usernames
			'''
	disallowed = set([])
	for row in c.execute(query):
		disallowed.add(row[0])

	return disallowed

def getAllowedNames(conn):
	""" Returns a set of all legitimate allowed usernames.

		Args:
			- conn: sqlite3.Connection object 
	"""
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
		usernames.add(row[0])

	return usernames

def resolveDisallowedUsers(dry_run = False):
	""" Changes usernames matching disallowed words (i.e. grailed, settings)
		into new usernames. 

		Args:
			- dry_run: Boolean for Dry Run Mode
	"""
	conn = connectDB()
	c = conn.cursor()
	s = conn.cursor()

	query = ''' SELECT USERS.id, USERS.username
			    FROM USERS
			    JOIN DISALLOWED_USERNAMES
			    WHERE USERS.username = DISALLOWED_USERNAMES.invalid_username
			    ORDER BY USERS.id
			'''

	disallowed = getDisallowedNames(conn) # prevents new name being disallowed.
	allowed = getAllowedNames(conn) # prevents duplicate new names

	duplicates = {} # hashmap to save time on duplicates

	for row in c.execute(query): 
		# Gets all rows from USERS Table with Disallowed usernames
		iD, name = row[0], row[1]
		if name not in duplicates:
			counter = 1
		else:
			counter = duplicates[name]

		newName = name + str(counter)

		while newName in disallowed or newName in allowed:
			# newName cannot be a duplicate or another disallowed sequence
			counter += 1
			newName = name + str(counter)

		duplicates[name] = counter + 1

		if dry_run:
			print(iD, name + ' => ' + '[' + newName + ']')
		else:
			updateName(s, iD, newName)

	c.close()
	s.close()
	conn.commit()
	conn.close()


if __name__ == "__main__":
	parser = createParser()
	args = parser.parse_args()
	DRY_RUN = True if args.dry_run else False
	resolveDisallowedUsers(DRY_RUN)
