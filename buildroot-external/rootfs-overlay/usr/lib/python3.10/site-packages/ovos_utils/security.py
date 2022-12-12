import platform
import pexpect
from socket import gethostname
from os.path import exists, join
from os import makedirs
import os
import random
import string
from ovos_utils.log import LOG

try:
    # pycryptodomex
    from Cryptodome.Cipher import AES
except ImportError:
    # pycrypto + pycryptodome
    try:
        from Crypto.Cipher import AES
    except:
        AES = None
try:
    from OpenSSL import crypto
except ImportError:
    crypto = None


def create_self_signed_cert(cert_dir, name="jarbas"):
    """
    If name.crt and name.key don't exist in cert_dir, create a new
    self-signed cert and key pair and write them into that directory.
    """
    if crypto is None:
        LOG.error("run pip install pyopenssl")
        raise ImportError
    CERT_FILE = name + ".crt"
    KEY_FILE = name + ".key"
    cert_path = join(cert_dir, CERT_FILE)
    key_path = join(cert_dir, KEY_FILE)

    if not exists(join(cert_dir, CERT_FILE)) \
            or not exists(join(cert_dir, KEY_FILE)):
        # create a key pair
        k = crypto.PKey()
        k.generate_key(crypto.TYPE_RSA, 1024)

        # create a self-signed cert
        cert = crypto.X509()
        cert.get_subject().C = "PT"
        cert.get_subject().ST = "Europe"
        cert.get_subject().L = "Mountains"
        cert.get_subject().O = "Jarbas AI"
        cert.get_subject().OU = "Powered by Mycroft-Core"
        cert.get_subject().CN = gethostname()
        cert.set_serial_number(random.randint(0, 2000))
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(k)
        # TODO don't use sha1
        cert.sign(k, 'sha1')
        if not exists(cert_dir):
            makedirs(cert_dir)
        open(cert_path, "wt").write(
            crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
        open(join(cert_dir, KEY_FILE), "wt").write(
            crypto.dump_privatekey(crypto.FILETYPE_PEM, k))

    return cert_path, key_path


def random_key(key_lenght=16):
    """Generate a random string of letters and digits """
    valid_chars = string.ascii_letters + string.digits
    return ''.join(random.choice(valid_chars) for i in range(key_lenght))


def encrypt(key, text, nonce=None):
    if AES is None:
        LOG.error("run pip install pycryptodomex")
        raise ImportError
    if not isinstance(text, bytes):
        text = bytes(text, encoding="utf-8")
    if not isinstance(key, bytes):
        key = bytes(key, encoding="utf-8")
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(text)
    return ciphertext, tag, cipher.nonce


def decrypt(key, ciphertext, tag, nonce):
    if AES is None:
        LOG.error("run pip install pycryptodomex")
        raise ImportError
    if not isinstance(key, bytes):
        key = bytes(key, encoding="utf-8")
    cipher = AES.new(key, AES.MODE_GCM, nonce)
    try:
        data = cipher.decrypt_and_verify(ciphertext, tag)
        text = data.decode(encoding="utf-8")
        return text
    except Exception as e:
        LOG.error("decryption failed, invalid key?")
        raise


def sudo_exec(cmdline, passwd="root"):
    osname = platform.system()
    if osname == 'Linux':
        prompt = r'\[sudo\] password for %s: ' % os.environ['USER']
    elif osname == 'Darwin':
        prompt = 'Password:'
    else:
        raise SystemError("Unsupported platform")

    child = pexpect.spawn(cmdline)
    idx = child.expect([prompt, pexpect.EOF], 3)
    if idx == 0:  # if prompted for the sudo password
        LOG.debug('sudo password was asked.')
        child.sendline(passwd)
        child.expect(pexpect.EOF)
    return child.before
