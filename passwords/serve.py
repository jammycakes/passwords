#! /usr/bin/env python

import os
import bcrypt
import hashlib

from datetime import datetime
from flask import Flask, request
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello world!'

GLOBAL_SALT = os.environ['GLOBAL_SALT']
WORK_FACTOR = int(os.environ['WORK_FACTOR'])

# ====== Password hashing ====== #

'''
Passwords are hashed twice, using two separate algorithms.

The first algorithm is a SHA-512 hash of the password, combined with the global
salt. This serves two purposes. First, it gets round bcrypt's upper length limit
of 72 characters; second, it adds a "secret" independent of the database to
prevent brute forcing by anyone who does not already know the secret.

The second algorithm is bcrypt, which does the heavy lifting, while also providing
a password-specific salt.
'''

def __prehash(pwd):
    return hashlib.sha512((pwd + GLOBAL_SALT).encode()).digest()

def __hash_password(pwd):
    salt = bcrypt.gensalt(WORK_FACTOR)
    return bcrypt.hashpw(__prehash(pwd), salt)

def __test_password(pwd, stored):
    encoded_stored = stored.encode()
    return bcrypt.hashpw(__prehash(pwd), encoded_stored) == encoded_stored


# ====== CRUD operations ====== #

def __get_collection():
    client = MongoClient('passwords-db', 27017)
    db = client.passwords
    return db.passwords

def __get_record(id):
    collection = __get_collection()
    return collection.find_one({'_id': id})

def __add_record(record):
    collection = __get_collection()
    return collection.insert_one(record).inserted_id

def __delete_record(id):
    collection = __get_collection()
    collection.delete_one({'_id': id})


# ====== Stores a password ====== #


'''
Stores a password in the database, and returns its ID.
'''
@app.route('/password', methods=['POST'])
def set_password():
    pwd = request.form['password']
    hashed = __hash_password(pwd)
    model = {
        'hash': hashed,
        'date': datetime.utcnow()
    }
    return str(__add_record(model))


# ====== Deletes a password from the database ====== #

'''
Deletes the password with specified ID from the database.
'''
@app.route('/password/<id>', methods=['DELETE'])
def delete_password(id):
    oid = ObjectId(id)
    __delete_record(oid)
    return 'OK'


# ====== Tests a password ====== #

'''
Tests the password with given ID. Returns true if the password is correct, otherwise false.
'''
@app.route('/password/test/<id>', methods=['POST'])
def test_password(id):
    pwd = request.form['password']


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)