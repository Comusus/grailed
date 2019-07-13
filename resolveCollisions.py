# resolveCollisions.py: Methods for resolving duplicate username collisions.

from db import connectDB, createParser
import argparse

def getUsernames():
    """ Get all of the usernames from the Database.

        Returns:
            unique - Hashset of all unique usernames.
            duplicates - Hashmap where key is duplicate and val is a counter

    """
    conn = connectDB()
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
    conn.close()

    return unique, duplicates


def updateName(s, iD, newName):
    """ Update the username column in the row in the Users Table.

        Inputs:
            s - Cursor Class 
            iD - Integer of user ID 
            newName - String of New Name

    """
    query = '''UPDATE users SET username=? WHERE id=?'''
    s.execute(query, (newName, iD))

def resolveUsernameCollisions(dry_run = False):
    """ Resolves all username collisions. 
        If ran in dry_run mode then prints out all changes in alphabetic
        and id order.

        Inputs:
            - dry_run: Boolean for Dry Run Mode
    """
    conn = connectDB()
    c = conn.cursor()
    s = conn.cursor()

    unique, duplicates = getUsernames()

    query = '''SELECT users.id, users.username
               FROM  USERS
               JOIN ( SELECT username, COUNT(username) 
                      FROM users
                      GROUP BY username
                      HAVING COUNT(username) > 1
                    ) as duplicates
               WHERE users.username = duplicates.username
            '''

    for row in c.execute(query):
        counter = duplicates[row[1]]
        if counter > 0:
            # we have seen this duplicate before
            newName = row[1] + str(counter)
            while newName in duplicates or newName in unique:
                # check if the New Name would cause another collisions
                counter += 1
                newName = row[1] + str(counter)

            if dry_run:
                print(row[0], row[1] + " => " + newName)
            else:
                updateName(s, row[0], newName)

            duplicates[row[1]] = counter + 1

        else:
            # we have seen this duplicate for the first time
            if dry_run:
                print(row[0], row[1] + " => " + row[1])
            
            duplicates[row[1]] += 1

    conn.commit() #commit changes

    s.close()
    c.close()
    conn.close()

if __name__ == "__main__":
    # print(createParser())
    # parser = argparse.ArgumentParser(description='Meep.')
    # getUsernames2()
    conn = connectDB()
    s = conn.cursor()

    # resolveUsernameCollisions()
    # findDisallowedUsers()