import urllib.request
import urllib.parse

from django.contrib.auth.hashers import BasePasswordHasher
from django.utils.translation import ugettext_noop as _

SERVICE_BASE_URL = 'http://service.passwords.localhost/'

class ServicePasswordHasher(BasePasswordHasher):

    algorithm = 'service'

    def salt(self):
        """
        Salt is handled by the hashing service - ignore here.
        """
        return ''

    def encode(self, password, salt):
        data = urllib.parse.urlencode({ 'password': password })
        data = data.encode('ascii')
        url = SERVICE_BASE_URL + 'password'
        with urllib.request.urlopen(url, data) as f:
            return self.algorithm + '$' + f.read().decode('utf-8')

    def verify(self, password, encoded):
        algorithm, password_id = encoded.split('$', 1)
        assert algorithm == self.algorithm
        data = urllib.parse.urlencode({ 'password': password })
        data = data.encode('ascii')
        url = SERVICE_BASE_URL + 'password/test/' + urllib.parse.urlencode(password_id)
        with urllib.request.urlopen(url, data) as f:
            return f.getcode() < 400

    def safe_summary(self):
        algorithm, password_id = encoded.split('$', 1)
        assert algorithm == self.algorithm
        return OrderedDict([
            (_('algorithm'), algorithm),
            (_('id'), password_id)
        ])