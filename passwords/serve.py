#! /usr/bin/env python

import os
import bcrypt
import hashlib

from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello world!'

GLOBAL_SALT = os.environ['GLOBAL_SALT']
WORK_FACTOR = int(os.environ['WORK_FACTOR'])

def __prehash(pwd):
    return hashlib.sha512(GLOBAL_SALT + pwd).digest()

def __hash_password(pwd):
    salt = bcrypt.gensalt(WORK_FACTOR)
    return bcrypt.hashpw(__prehash(pwd), salt)

def __test_password(pwd, stored):
    return bcrypt.hashpw(__prehash(pwd), stored) == stored


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)