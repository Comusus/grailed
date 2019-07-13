# resolveCollisions.py: Methods for resolving duplicate username collisions.

from utils import connectDB, createParser

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

def resolveUsernameCollisions(dry_run = False):
    """ Resolves all username collisions. 
        If ran in dry_run mode then prints out all changes in alphabetic
        and id order.

        Args:
            - dry_run: Boolean for Dry Run Mode
    """
    conn = connectDB()
    c = conn.cursor()
    s = conn.cursor()

    unique, duplicates = getUsernames(conn)

    query = ''' SELECT USERS.id, USERS.username
                FROM  USERS
                JOIN ( SELECT username, COUNT(username) 
                       FROM USERS
                       GROUP BY username
                       HAVING COUNT(username) > 1
                     ) as duplicates
                WHERE USERS.username = duplicates.username
            '''

    for row in c.execute(query):
        iD, name = row[0], row[1]
        counter = duplicates[name]
        if counter > 0:
            # we have seen this duplicate before
            newName = name + str(counter)
            while newName in duplicates or newName in unique:
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
    resolveUsernameCollisions(DRY_RUN)
