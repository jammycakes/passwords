#! /usr/bin/env python

import os
import bcrypt
import hashlib
import uuid

from datetime import datetime
from flask import Flask, request
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello world!'

PASSWORD_SECRET = os.environ['PASSWORD_SECRET']
KEY_SECRET = os.environ['KEY_SECRET']
WORK_FACTOR = int(os.environ['WORK_FACTOR'])

# ====== Password hashing ====== #

def __prehash(pwd):
    '''
    Passwords are hashed twice, using two separate algorithms.

    The first algorithm is a SHA-512 hash of the password, combined with the
    password hashing secret. This serves two purposes. First, it gets round
    bcrypt's upper length limit of 72 characters; second, it adds a "secret"
    independent of the database to prevent brute forcing by anyone who does
    not already know the secret.

    The second algorithm is bcrypt, which does the heavy lifting, while also
    providing a password-specific salt.

    This method calculates the prehash, i.e. only the SHA-512.
    '''
    return hashlib.sha512((pwd + PASSWORD_SECRET).encode()).digest()

def __hash_password(pwd):
    salt = bcrypt.gensalt(WORK_FACTOR)
    return bcrypt.hashpw(__prehash(pwd), salt)

def __test_password(pwd, stored):
    return bcrypt.hashpw(__prehash(pwd), stored) == stored


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

def __hash_id(id):
    id_with_key = (id + KEY_SECRET).encode('utf-8')
    hash = hashlib.sha256(id_with_key)
    return hash.hexdigest()


@app.route('/password', methods=['POST'])
def set_password():
    '''
    Stores a password in the database, and returns its ID.

    To invoke this method, issue an HTTP POST request, passing in the password
    as an HTTP form field called "pasword".

    The method will return a GUID by which the password can be identified.
    This GUID should then be saved in the "password" field in your users table.
    '''
    pwd = request.form['password']
    hashed = __hash_password(pwd)
    id = str(uuid.uuid4())
    id_hashed = __hash_id(id)
    model = {
        '_id': __hash_id(id),
        'hash': hashed,
        'date': datetime.utcnow()
    }
    __add_record(model)
    return id


# ====== Deletes a password from the database ====== #

@app.route('/password/<id>', methods=['DELETE'])
def delete_password(id):
    '''
    Deletes the password with specified ID from the database.

    To invoke this method, issue an HTTP DELETE request, passing in the GUID
    returned from the "set_password" method above in the URL in place of the
    "<id>" placeholder.

    This method will return 200 OK.
    '''
    oid = __hash_id(id)
    __delete_record(oid)
    return 'OK'


# ====== Tests a password ====== #

@app.route('/password/test/<id>', methods=['POST'])
def test_password(id):
    '''
    Tests the password with given ID.

    To invoke this method, issue an HTTP POST request, passing in the GUID
    returned from the "set_password" method above in the URL in place of the
    "<id>" placeholder. The candidate password being tested should be passed
    in as a form field called "password", as with the set_password method.

    Returns true/200 OK if the password is correct, otherwise false/403 Forbidden.
    '''
    oid = __hash_id(id)
    pwd = request.form['password']
    rec = __get_record(oid)
    if not rec:
        return 'false', 403
    is_correct = __test_password(pwd, rec['hash'])
    if is_correct:
        return 'true'
    else:
        return 'false', 403


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)