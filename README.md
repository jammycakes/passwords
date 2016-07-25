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

Running on your local machine
-----------------------------
Install [Docker Engine](https://docs.docker.com/engine/installation/)
and [Docker Compose](https://docs.docker.com/compose/install/).

On OS X or Windows, edit your hosts file (OS X: `/etc/hosts`; Windows: `c:\Windows\System32\drivers\etc\hosts`)
and add the following line:

    *.passwords.localhost localhost

On Ubuntu, create the file `/etc/NetworkManager/dnsmasq.d/hosts.conf` if it does not already exist,
then add the line:

    address=/passwords.localhost/127.0.0.1/

then restart NetworkManager using `sudo restart network-manager`.

To run the containers:

    docker-compose build
    docker-compose up

You can then access the web application at

    http://web.passwords.localhost/

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

The web application
-------------------

Consuming the password service is illustrated with a very simple Django web application.
The file `web/webapp/security.py` contains a custom password hasher that plugs into the
password hashing service.

Writing adapters/hashers for other platforms (e.g. ASP.NET Identity, Rails, WordPress)
is left as an exercise for the reader.