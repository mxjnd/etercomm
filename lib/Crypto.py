from OpenSSL import crypto

# 1. Genera una chiave privata RSA
private_key = crypto.PKey()
private_key.generate_key(crypto.TYPE_RSA, 2048)

# 2. Crea un certificato X.509
cert = crypto.X509()

# Imposta le informazioni del certificato
subject = cert.get_subject()
subject.CN = "example.com"  # Common Name (dominio o nome dell'organizzazione)
subject.O = "My Organization"
subject.L = "Rome"
subject.ST = "Rome"
subject.C = "IT"

# Imposta la data di inizio e fine validità del certificato
cert.set_notBefore(b'20250215000000Z')  # Formato: YYYYMMDDHHMMSSZ
cert.set_notAfter(b'20260215000000Z')

# Imposta il numero di serie del certificato
cert.set_serial_number(1000)

# Firma il certificato con la chiave privata
cert.set_issuer(subject)  # L'emittente del certificato è lo stesso del soggetto, visto che è autofirmato
cert.set_pubkey(private_key)
cert.sign(private_key, 'sha256')

# 3. Salva la chiave privata in un file
with open("private_key.pem", "wb") as private_key_file:
    private_key_file.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, private_key))

# 4. Salva il certificato in un file
with open("certificate.pem", "wb") as cert_file:
    cert_file.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))

print("Chiave privata e certificato autofirmato generati con successo.")
