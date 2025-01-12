# pycrypto-helper

Cryptographic operations can be challenging, especially when handling different key types and PKCS#11. 
`pycrypto-helper` is a helper library designed to simplify cryptographic operations, including signing, verifying, encrypting, and decrypting data using various key types and PKCS#11 tokens.

## Installation

```bash
sudo python3 -m pip install .
```

## Available Functions

### `crypto_helper.sign(key_desc, data, pin)`

Signs the given data using the specified key.

- `key_desc`: A string describing the key (key file in pem format or pkcs11 uri).
- `data`: The data to be signed.
- `pin`: The pin or passphrase for accessing the key (optional).

### `crypto_helper.verify(key_desc, data, signature, pin)`

Verifies the given signature for the specified data using the key.

- `key_desc`: A string describing the key (key file in pem format or pkcs11 uri).
- `data`: The data whose signature is to be verified.
- `signature`: The signature to be verified.
- `pin`: The pin or passphrase for accessing the key (optional).

### `crypto_helper.cms_sign(key_desc, cert, data, pin)`

Signs using CMS the given data using the specified key and certificate.

- `key_desc`: A string describing the key (key file in pem format or pkcs11 uri).
- `cert`: The certificate file in pem format.
- `data`: The data to be signed.
- `pin`: The pin or passphrase for accessing the key (optional).

### `crypto_helper.cms_verify(cert, data, signature)`

Verifies the given CMS signature for the specified data using the certificate.

- `cert`: The certificate file in pem format.
- `data`: The data to be signed.
- `signature`: the cms signature to be verified in der format.

### `crypto_helper.encrypt(key_desc, ivt, data, pin)`

Encrypts using AES the given data using the specified key.

- `key_desc`: A string describing the key (key file or pkcs11 uri).
- `ìvt`: The initialization vector.
- `data`: The data to be encrypted.
- `pin`: The pin for accessing the key (optional).

### `crypto_helper.decrypt(key_desc, ivt, encrypted_data, pin)`

Decrypts using AES the given encrypted data using the specified key.

- `key_desc`: A string describing the key (key file or pkcs11 uri).
- `ìvt`: The initialization vector.
- `encrypted_data`: The data to be decrypted.
- `pin`: The pin for accessing the key (optional).

## Example usage

```python
from pycrypto_helper import crypto_helper

# using key file
key_desc = "ecdsa_key.pem"
data = b"Hello, world!"
signature = crypto_helper.sign(key_desc, data)
print(signature.hex())
crypto_helper.verify(key_desc, data, signature)

# using pkcs11 token
key_desc = "pkcs11:token=SmartCard-HSM%20%28UserPIN%29;id=%01;object=testkeyECp256"
data = b"Hello, world!"
signature = crypto_helper.sign(key_desc, data, "123456")
print(signature.hex())
crypto_helper.verify(key_desc, data, signature, "123456")
```

