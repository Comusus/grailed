# findDisallowedUsers.py: Methods to find users with disallowed usernames

from utils import connectDB, getPath

def findDisallowedUsers(path):
	""" Finds all users with disallowed usernames and print them in
		format: {id} {name}. 

		Args:
			- path: String of Path to Database file

		Returns:
			None
	"""
	conn = connectDB(path)
	c = conn.cursor()
	query = ''' SELECT USERS.id, USERS.username
			    FROM USERS
			    JOIN DISALLOWED_USERNAMES
			    WHERE USERS.username = DISALLOWED_USERNAMES.invalid_username
			    ORDER BY USERS.id 
			'''

	for row in c.execute(query):
		print(row[0], row[1]) # prints id and name

	c.close()
	conn.close()


def returnDisallowedUsers(path):
	""" Returns all users with disallowed usernames as a list.

		Args:
			- path: String of Path to Database file

		Returns:
			- [row]: List of Tuples in form ({id}, {username})
	"""
	conn = connectDB(path)
	c = conn.cursor()
	query = ''' SELECT USERS.id, USERS.username
			    FROM USERS
			    JOIN DISALLOWED_USERNAMES
			    WHERE USERS.username = DISALLOWED_USERNAMES.invalid_username
			    ORDER BY USERS.id 
			'''

	c.execute(query)
	row = c.fetchall() # List of Tuples ({id}, {username})
	c.close()
	conn.close()

	return row
	

if __name__ == "__main__":
	findDisallowedUsers(getPath())