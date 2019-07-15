# resolveCollisions.py: Methods for resolving duplicate username collisions.

from utils import connectDB, updateName, createParser, getPath
from resolveDisallowed import getDisallowedNames

def getUsernames(conn):
	""" Get all of the usernames from the Database split into unique
		usernames and duplicate usernames.

		Args:
			- conn: sqlite3.Connection object 

		Returns:
			- unique: Hashset of all unique usernames.
			- duplicates: Hashmap where key is a duplicate and val is a counter
	"""
	c = conn.cursor()

	unique = set([])
	duplicates = {}
	query = ''' SELECT username, COUNT(username)
				FROM USERS
				GROUP BY username
			'''

	for row in c.execute(query):
		username, count = row[0], row[1]
		if count > 1:
			duplicates[username] = 0
		else:
			unique.add(username)

	c.close()
	return unique, duplicates


def resolveUsernameCollisions(path, dry_run = False):
	""" Resolves all username collisions. New usernames are not disallowed
		and are not duplicates of other unique or duplicate usernames.
		If ran in dry_run mode then prints out all changes instead of updating
		the DB.

		Args:
			- path: String of Path to Database file
			- dry_run: Boolean for Dry Run Mode
	"""
	conn = connectDB(path)
	c = conn.cursor()
	s = conn.cursor()

	unique, duplicates = getUsernames(conn)
	disallowed = getDisallowedNames(conn)

	query = ''' SELECT USERS.id, USERS.username
				FROM  USERS
				JOIN ( SELECT username, COUNT(username) 
					   FROM USERS
					   GROUP BY username
					   HAVING COUNT(username) > 1
					 ) as duplicates
				WHERE USERS.username = duplicates.username
				ORDER BY USERS.username
			'''
	# change query to ORDER BY USERS.id for in order

	for row in c.execute(query):
		iD, name = row[0], row[1]
		counter = duplicates[name]
		if counter > 0:
			# we have seen this duplicate before
			newName = name + str(counter)
			while newName in duplicates or newName in unique or newName in disallowed:
				# check if the New Name would cause another collisions
				counter += 1
				newName = name + str(counter)

			if dry_run:
				print(iD, name + " => " + "[" + newName + "]")
			else:
				updateName(s, iD, newName)

			duplicates[name] = counter + 1

		else:
			# we have seen this duplicate for the first time
			if dry_run:
				print(iD, name + " => " + "[" + name + "]")
			
			duplicates[name] += 1

	conn.commit() # commit changes/updates to DB

	s.close()
	c.close()
	conn.close()
	

if __name__ == "__main__":
	parser = createParser()
	args = parser.parse_args()
	DRY_RUN = True if args.dry_run else False
	resolveUsernameCollisions(getPath(), DRY_RUN)
