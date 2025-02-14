from OpenSSL import crypto

def gen():
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 2048)
    cert = crypto.X509()
    cert.get_subject().CN = 'x'
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(365*24*60*60)
    cert.set_issuer(cert.get_subject()) 
    cert.set_pubkey(key)
    cert.sign(key, 'sha256')
    return (key, cert)

def save(key_file, cert_file, key, cert):
    with open(key_file, "wb") as w:
        w.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))
    with open(cert_file, "wb") as w:
        w.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
