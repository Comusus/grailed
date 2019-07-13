# findDisallowedUsers.py: Methods to find users with disallowed usernames

from db import connectDB

def findDisallowedUsers():
	""" Finds all users with disallowed usernames and print them in
		format: {id} {name}. 

		Returns:
			None
	"""
	conn = connectDB()
	c = conn.cursor()
	query = ''' SELECT USERS.id, USERS.username
			    FROM USERS
			    JOIN DISALLOWED_USERNAMES
			    WHERE users.username = disallowed_usernames.invalid_username
			    ORDER BY users.id 
			'''

	for row in c.execute(query):
		print(row[0], row[1])

	c.close()
	conn.close()

if __name__ == "__main__":
	findDisallowedUsers()