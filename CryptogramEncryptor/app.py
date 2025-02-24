import os
import rsa
from flask import Flask, render_template, request, send_file
from cryptography.fernet import Fernet
from Crypto.Cipher import AES, DES
from Crypto.Util.Padding import pad, unpad
from werkzeug.utils import secure_filename

app = Flask(__name__)

ENCRYPTED_DIR = "encrypted_files"
DECRYPTED_DIR = "decrypted_files"
KEY_DIR = "keys"

os.makedirs(ENCRYPTED_DIR, exist_ok=True)
os.makedirs(DECRYPTED_DIR, exist_ok=True)
os.makedirs(KEY_DIR, exist_ok=True)

def generate_fernet_key():
    return Fernet.generate_key()

def load_key(key_path):
    with open(key_path, "rb") as key_file:
        return key_file.read()

def save_key(key, key_path):
    with open(key_path, "wb") as key_file:
        key_file.write(key)

# AES Key Handling (16 bytes for AES-128)
def generate_aes_key():
    return os.urandom(16)  # AES-128 key size

# DES Key Handling (8 bytes)
def generate_des_key():
    return os.urandom(8)

# RSA Key Handling
def generate_rsa_keys():
    public_key, private_key = rsa.newkeys(1024)
    return public_key, private_key

def encrypt_data(data, key, algorithm):
    """Encrypt data using the specified algorithm."""
    if algorithm == "Fernet":
        f = Fernet(key)
        return f.encrypt(data)

    elif algorithm == "AES":
        cipher = AES.new(key, AES.MODE_CBC)
        encrypted_data = cipher.iv + cipher.encrypt(pad(data, AES.block_size))
        return encrypted_data

    elif algorithm == "DES":
        cipher = DES.new(key, DES.MODE_CBC)
        encrypted_data = cipher.iv + cipher.encrypt(pad(data, DES.block_size))
        return encrypted_data

    elif algorithm == "RSA":
        public_key = rsa.PublicKey.load_pkcs1(key)
        return rsa.encrypt(data, public_key)

    return None

def decrypt_data(data, key, algorithm):
    """Decrypt data using the specified algorithm."""
    if algorithm == "Fernet":
        f = Fernet(key)
        return f.decrypt(data)

    elif algorithm == "AES":
        iv = data[:AES.block_size]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(data[AES.block_size:]), AES.block_size)

    elif algorithm == "DES":
        iv = data[:DES.block_size]
        cipher = DES.new(key, DES.MODE_CBC, iv)
        return unpad(cipher.decrypt(data[DES.block_size:]), DES.block_size)

    elif algorithm == "RSA":
        private_key = rsa.PrivateKey.load_pkcs1(key)
        return rsa.decrypt(data, private_key)

    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_file', methods=['POST'])
def process_file():
    action = request.form['action']
    file_type = request.form['file_type']
    algorithm = request.form['algorithm']
    file = request.files['file']

    if file:
        filename = secure_filename(file.filename)
        file_data = file.read()
        key_path = os.path.join(KEY_DIR, f"{algorithm.lower()}_key.key")

        if not os.path.exists(key_path):
            if algorithm == "Fernet":
                key = generate_fernet_key()
            elif algorithm == "AES":
                key = generate_aes_key()
            elif algorithm == "DES":
                key = generate_des_key()
            elif algorithm == "RSA":
                public_key, private_key = generate_rsa_keys()
                save_key(private_key.save_pkcs1(), os.path.join(KEY_DIR, "rsa_private_key.pem"))
                key = public_key.save_pkcs1()
            save_key(key, key_path)
        else:
            key = load_key(key_path)

        try:
            if action == 'encrypt':
                encrypted_data = encrypt_data(file_data, key, algorithm)
                encrypted_file_path = os.path.join(ENCRYPTED_DIR, f"{filename}.enc")

                with open(encrypted_file_path, "wb") as enc_file:
                    enc_file.write(encrypted_data)

                return send_file(encrypted_file_path, as_attachment=True)

            elif action == 'decrypt':
                if not filename.endswith(".enc"):
                    return "Error: The file is not in encrypted format. Please upload a valid encrypted file."

                decrypted_data = decrypt_data(file_data, key, algorithm)
                decrypted_file_path = os.path.join(DECRYPTED_DIR, filename.replace(".enc", ""))

                with open(decrypted_file_path, "wb") as dec_file:
                    dec_file.write(decrypted_data)

                return send_file(decrypted_file_path, as_attachment=True)

        except Exception as e:
            return f"An error occurred: {e}"

    return "Error: No file uploaded."
if __name__ == '__main__':
    app.run(debug=True)
