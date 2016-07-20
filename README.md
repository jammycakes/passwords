Password hashing as a microservice.
===================================
This approach to password hashing provides us with some additional security benefits.
By storing passwords in a separate database, it means that getting hold of the user
database is not sufficient for an attacker to brute force the user's credentials.

Additionally, because most of the hard work in password storage and verification is in
the hash algorithm, we can easily scale this part of the process out by adding more
containers if signups get really busy.

This project defines two docker images: the password microservice, and a sample
web application designed to hook into it.

The microservice API
--------------------
The password API defines three endpoints:

### POST /password

Stores a password in the database. Should be passed in as a form field called `password`.

 * Returns the password ID. This should be stored in the user database.

### DELETE /password/\<id\>

Deletes a password from the password database.

 * Returns 200 OK.

### POST /password/test/\<id\>

Tests a password with the specified ID against the database.
The password should be passed in as a form field called `password`.

 * Returns "true" with a status 200 OK if the password was correct.
 * Returns "false" with a status 403 Forbidden if the password was incorrect
   or not found.

Environment variables
---------------------

### PASSWORD_SECRET

This is a secret added to the password to make brute forcing all but impossible to attackers.
In production systems, it should ideally be stored in a secret store such as Hashicorp Vault.

### KEY_SECRET

This is a second secret, which is added to the password ID to make it all but impossible for
an attacker to match up passwords with user accounts. Again, in production systems, it should
ideally be stored in a secret store.

### WORK_FACTOR

The work factor used by the bcrypt algorithm. A factor of about 12 means that hashing takes
roughly a quarter of a second.

To run:
=======

Make sure you have Docker and Docker Compose installed.

Type: `docker-compose up` to start up the app.