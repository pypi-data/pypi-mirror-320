#
#  (C) Copyright 2025
#  Embetrix Embedded Systems Solutions, ayoub.zaki@embetrix.com
#

import os
import re
import pkcs11
from pkcs11 import KeyType, ObjectClass, Mechanism
from pkcs11.util.ec import encode_ec_public_key
from pkcs11.util.rsa import encode_rsa_public_key
from base64 import b64encode, b64decode
from Cryptodome.Hash import SHA256
from Cryptodome.PublicKey import ECC, RSA
from Cryptodome.Signature import DSS, PKCS1_v1_5
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
from urllib.parse import urlparse, parse_qs, unquote
from asn1crypto import cms, pem, x509, algos, core

def load_key_file(file_path, password=None):
    with open(file_path, 'rb') as f:
        key_data = f.read()
        try:
            return RSA.import_key(key_data, passphrase=password)
        except (ValueError, TypeError):
            try:
                return ECC.import_key(key_data, passphrase=password)
            except (ValueError, TypeError):
                return key_data

def load_key(key_desc, pin=None, key_type="private"):
    session = None
    if key_desc.startswith("pkcs11:"):
        pkcs11_dict = parse_pkcs11_uri(key_desc)
        lib_path = os.environ.get('PKCS11_MODULE_PATH', '/usr/lib/x86_64-linux-gnu/opensc-pkcs11.so')
        lib = pkcs11.lib(lib_path)
        token = lib.get_token(token_label=pkcs11_dict['token'])
        session = token.open(user_pin=pin)
        if key_type == "public":
            key = session.get_key(label=pkcs11_dict['object'], object_class=ObjectClass.PUBLIC_KEY)
        elif key_type == "private":
            key = session.get_key(label=pkcs11_dict['object'], object_class=ObjectClass.PRIVATE_KEY)
        elif key_type == "secret":
            key = session.get_key(label=pkcs11_dict['object'], object_class=ObjectClass.SECRET_KEY)
        else:
            raise ValueError("Unsupported key type")
    else:
        key = load_key_file(key_desc, pin)
    return key, session

def get_key_type(key_desc, pin=None):
    try:
        key, session = load_key(key_desc, pin)
        if session:
            if key.key_type == KeyType.RSA:
                key_type = 'RSA'
            elif key.key_type == KeyType.EC:
                key_type = 'EC'
            else:
                raise ValueError("Unsupported key type")
            session.close()
        else:
            if isinstance(key, RSA.RsaKey):
                key_type = 'RSA'
            elif isinstance(key, ECC.EccKey):
                key_type = 'EC'
            else:
                raise ValueError("Unsupported key type")
        return key_type
    except Exception as e:
        print(f"Error determining key type: {e}")
        raise

def load_pem_certificate(file_path):
    try:
        with open(file_path, 'r') as f:
            pem_data = f.read()
        der_data = b64decode(
            pem_data.replace("-----BEGIN CERTIFICATE-----", "")
                    .replace("-----END CERTIFICATE-----", "")
        )
        return x509.Certificate.load(der_data)
    except Exception as e:
        print(f"Error loading PEM certificate: {e}")
        raise

def parse_pkcs11_uri(uri):
    parsed_uri = urlparse(uri)
    if parsed_uri.scheme != 'pkcs11':
        raise ValueError("Invalid PKCS#11 URI scheme")

    path = unquote(parsed_uri.path)
    path_components = path.split(';')

    path_dict = {}
    for component in path_components:
        if '=' in component:
            key, value = component.split('=', 1)
            value = unquote(value)
            path_dict[key] = value

    query_dict = parse_qs(parsed_uri.query)
    pkcs11_dict = {**path_dict, **{k: v[0] for k, v in query_dict.items()}}

    return pkcs11_dict

class ECDSASignature(core.Sequence):
    _fields = [
        ('r', core.Integer),
        ('s', core.Integer),
    ]

def der_to_raw_signature(der_signature, key_size):
    ecdsa_signature = ECDSASignature.load(der_signature)
    r = int(ecdsa_signature['r'].native)
    s = int(ecdsa_signature['s'].native)
    raw_signature = r.to_bytes(key_size // 8, byteorder='big') + s.to_bytes(key_size // 8, byteorder='big')
    return raw_signature

def encode_ecdsa_signature(raw_signature):
    half_len = len(raw_signature) // 2
    r = int.from_bytes(raw_signature[:half_len], 'big')
    s = int.from_bytes(raw_signature[half_len:], 'big')

    return ECDSASignature({'r': r, 's': s}).dump()

def get_oid(key_type, hash_algorithm):
    oid_map = {
        'rsa': {
            'sha256': '1.2.840.113549.1.1.11',
            'sha384': '1.2.840.113549.1.1.12',
            'sha512': '1.2.840.113549.1.1.13',
        },
        'ec': {
            'sha256': '1.2.840.10045.4.3.2',
            'sha384': '1.2.840.10045.4.3.3',
            'sha512': '1.2.840.10045.4.3.4',
        }
    }

    if key_type not in oid_map:
        raise ValueError(f"Unsupported key type: {key_type}")
    if hash_algorithm not in oid_map[key_type]:
        raise ValueError(f"Unsupported hash algorithm: {hash_algorithm}")

    return oid_map[key_type][hash_algorithm]

def sign(key_desc, data, pin=None):
    try:
        sha256 = SHA256.new(data)
        key, session = load_key(key_desc, pin, "private")
        if session:
            if key.key_type == KeyType.RSA:
                mech = Mechanism.RSA_PKCS
            elif key.key_type == KeyType.EC:
                mech = Mechanism.ECDSA
            else:
                raise ValueError("Unsupported key type")
            signature = key.sign(sha256.digest(), mechanism=mech)
            session.close()
        else:
            if isinstance(key, RSA.RsaKey):
                signer = PKCS1_v1_5.new(key)
                signature = signer.sign(sha256)
            elif isinstance(key, ECC.EccKey):
                signer = DSS.new(key, 'fips-186-3')
                signature = signer.sign(sha256)
            else:
                raise ValueError("Unsupported key type")
        return signature
    except Exception as e:
        print(f"Error signing data: {e}")
        raise

def cms_sign(key_desc, certificate, data, pin=None):
    try:
        signature = sign(key_desc, data, pin)
        key_type = get_key_type(key_desc, pin)
        cert = load_pem_certificate(certificate)
        if key_type == 'RSA':
            signature_algorithm = algos.SignedDigestAlgorithm({
                'algorithm': get_oid('rsa', 'sha256'),
                'parameters': None
            })
        elif key_type == 'EC':  
            signature = encode_ecdsa_signature(signature)
            signature_algorithm = algos.SignedDigestAlgorithm({
                'algorithm': get_oid('ec', 'sha256'),
                'parameters': None
            })
        else:
            raise ValueError("Unsupported key type. Only RSA and ECC keys are supported.")
            # Create ContentInfo for detached signature
        encap_content_info = cms.ContentInfo({
            'content_type': 'data'
            # Detached: content not included
        })

        signed_data = cms.SignedData({
            'version': 'v1',
            'digest_algorithms': [cms.DigestAlgorithm({'algorithm': 'sha256'})],
            'encap_content_info': encap_content_info,
            'certificates': [cert],
            'signer_infos': [cms.SignerInfo({
                'version': 'v1',
                'sid': cms.SignerIdentifier({
                    'issuer_and_serial_number': cms.IssuerAndSerialNumber({
                        'issuer': cert.issuer,
                        'serial_number': cert.serial_number
                    })
                }),
                'digest_algorithm': cms.DigestAlgorithm({'algorithm': 'sha256'}),
                'signature_algorithm': signature_algorithm,
                'signature': signature
            })]
        })

        cms_structure = cms.ContentInfo({
            'content_type': 'signed_data',
            'content': signed_data
        })

        der_bytes = cms_structure.dump()
        return der_bytes
    except Exception as e:
        print(f"Error cms signing data: {e}")
        raise

def verify(key_desc, data, signature, pin=None):
    try:
        sha256 = SHA256.new(data)
        key, session = load_key(key_desc, pin, "public")
        if session:
            if key.key_type == KeyType.RSA:
                verifier = PKCS1_v1_5.new(RSA.import_key(encode_rsa_public_key(key)))
            elif key.key_type == KeyType.EC:
                verifier = DSS.new(ECC.import_key(encode_ec_public_key(key)), 'fips-186-3')
            else:
                raise ValueError("Unsupported key type")
            session.close()
        else:
            if isinstance(key, RSA.RsaKey):
                verifier = PKCS1_v1_5.new(key)
            elif isinstance(key, ECC.EccKey):
                verifier = DSS.new(key, 'fips-186-3')
            else:
                raise ValueError("Unsupported key type")
        try:
            verifier.verify(sha256, signature)
            print('The signature is valid.')
        except (ValueError, TypeError):
            print('The signature is not valid.')
    except Exception as e:
        print(f"Error verifying signature: {e}")
        raise

def cms_verify(certificate, data, signature):
    try:
        cms_data = cms.ContentInfo.load(signature)
        cert = load_pem_certificate(certificate)

        if cms_data['content_type'].native != 'signed_data':
            raise ValueError("CMS content is not of type 'signed_data'")

        signed_data = cms_data['content']

        if len(signed_data['signer_infos']) == 0:
            raise ValueError("No signer information found in CMS data")

        signer_info = signed_data['signer_infos'][0]

        if signer_info['digest_algorithm']['algorithm'].native != 'sha256':
            raise ValueError("Only SHA-256 is supported")

        public_key_info = cert.public_key.native

        if cert.public_key.algorithm == 'rsa':
            rsa_key = public_key_info['public_key']
            public_key = RSA.construct((rsa_key['modulus'], rsa_key['public_exponent']))
            key_type = 'RSA'
        elif cert.public_key.algorithm == 'ec':
            curve_parameters = public_key_info['algorithm']['parameters']
            named_curve = curve_parameters if isinstance(curve_parameters, str) else curve_parameters.native

            ec_key = public_key_info['public_key']
            public_key = ECC.construct(
                curve=named_curve,
                point_x=int.from_bytes(ec_key[1:33], 'big'),
                point_y=int.from_bytes(ec_key[33:], 'big'),
            )
            key_type = 'ECC'
        else:
            raise ValueError("Unsupported key type in the certificate")

        sha256 = SHA256.new(data)

        signature = signer_info['signature'].native

        if key_type == 'ECC':
            key_size = public_key.pointQ.size_in_bits()
            signature = der_to_raw_signature(signature, key_size)

        try:
            if key_type == 'RSA':
                PKCS1_v1_5.new(public_key).verify(sha256, signature)
            elif key_type == 'ECC':
                DSS.new(public_key, 'fips-186-3').verify(sha256, signature)
            print("The cms signature is valid.")
        except (ValueError, TypeError):
            print("The cms signature is not valid.")
    except Exception as e:
        print(f"Error verifying cms signature: {e}")
        raise

def encrypt(key_desc, ivt, data, pin=None):
    try:
        key, session = load_key(key_desc, pin, "secret")
        if session:
            encrypted_data = key.encrypt(data, mechanism_param=bytes.fromhex(ivt), mechanism=Mechanism.AES_CBC_PAD)
            session.close()
        else:
            cipher = AES.new(key, AES.MODE_CBC, bytes.fromhex(ivt))
            encrypted_data = b64encode(cipher.encrypt(pad(data, AES.block_size))).decode('utf-8')
        return encrypted_data
    except Exception as e:
        print(f"Error encrypting data: {e}")
        raise

def decrypt(key_desc, ivt, data, pin=None):
    try:
        key, session = load_key(key_desc, pin, "secret")
        if session:
            plaintext = key.decrypt(data, mechanism_param=bytes.fromhex(ivt), mechanism=Mechanism.AES_CBC_PAD)
            session.close()
        else:
            cipher = AES.new(key, AES.MODE_CBC, bytes.fromhex(ivt))
            plaintext = unpad(cipher.decrypt(b64decode(data)), AES.block_size)
        return plaintext
    except Exception as e:
        print(f"Error decrypting data: {e}")
        raise
