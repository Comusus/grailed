# grailed

I decided to use Python for this coding challenge and I have about 1.5 - 2 years
of experience using Python in an academic setting. I have about 1 - 1.5 years of
experience with SQL and I have used sqlite before for a project.


## Running the Code
I've used Python 3.6.5 to test my code, but any version of Python 3.x should work.

All of the packages I used are built-in but include:
`sqlite3`, `argparse`, and `shutil`.

You can run the code using the command line:

1. Running Function to Print Users with Disallowed usernames
``` 
	python findDisallowedUsers.py
```

2. Running Function to update Database by resolving Collisions of same usernames
``` 
	python resolveCollisions.py
```

You can also run the optional flag '-dry_run' to print out the changes and
not update the database.

``` 
	python resolveCollisions.py -dry_run
```

3. Running Function to update Database by resolving Disallowed usernames:
``` 
	python resolveDisallowed.py 
	python resolveDisallowed.py -dry_run
```

4. Run the test cases 
``` 
	python test.py
```

Dry run mode currently prints in alphabetic order of username to make the changes
easier to see, but it's possible to change to order of ID in the code by changing
the query to have ORDER BY USERS.id instead of ORDER BY USERS.username.

## File Structure
I put a lot of the common functions into `utils.py` that were especially useful
in the test.py section. 

I decided to write scripts that can be used in the command line while at the
root directory since it seemed like a reasonable way to do this challenge. 
Each python script uses functions from `utils.py` but are otherwise
pretty self contained except resolveCollisions borrows the function to find
Disallowed Usernames. 

The databases folder contains the given database, a copy of that database so
the given database can be restored for testing, and a toy database for unit testing.


## Rationale
There were two main ways I thoguht that could be used to resolve collisions based
on the specifications of the assignment. One way would just to append 1 to the end
of a username until there would be no collision. Looking at the sample database, the
most collisions would be at 6 but even at 6, a username of 'x111111' would be weird,
hard to type in/remember, and could lead to eventual memory problems if there were more collisions since database could have character limit.

The other method would be to start from the back of username to find all the
numerical characters and then cast it into an Integer to increment by 1 and 
concatenate that to the base username withouth the rightmost numerical characters.
This would've made the most compact way to account for duplicates but would've
added extra complexity to the time since we would have to scan all of the
strings.

The way I decided to go with was an intermediate such that all duplicates get a number appended to them and the collisions between the same usernames have a counter. For example,
`'foo','foo','foo' --> 'foo','foo1','foo2'` but `'foo100' and 'foo100' --> 'foo100','foo1001','foo1002'`.
To make this process faster, I included a hashmap for each duplicate with a counter
so we would avoid considering earlier numbers already used to fix duplicates. To be fair
to the users, I also thought of when the user created their account (earlier ID name) so
that cases like `'foo','foo','foo1' --> 'foo', 'foo2','foo1'`. 

To add onto the specifications and scope, (although the disallowed names table would probably
not be updated too much or include words with numbers attached to them), I also considered the case where resolving the collisions could lead to the creation of new usernames that could
be disallowed or further collisions. I also wanted to prevent resolving disallowed names from creating collisions or further disallowed names
since any of these cases could create extra calls or loops to update the Database.
Therefore, I wanted one call of each to be enough to fix the entire database. To do this,
I created methods that would gather the set of disallowed names, set of allowed names, set of duplicates, set of unique names, or whatever information was necessary. 

Therefore, `foo, foo, foo1` with disallowed `foo` would be `foo2, foo3, foo1`.

Also, I assumed that all the usernames in the database would work as pretty URLs (i.e. there were no spaces in the username string).

My overall rationality was that this solution was a temporary solution
to fix all of the , so it would be ran infrequently until the user creation
system was fixed to prevent new users from having non-unique / disallowed usernames.
Therefore, I thought that using more Space complexity would be justified if
it will help and reducing calls to the Database would be better.
