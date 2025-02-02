import os
from flask import Flask, render_template, request, send_file
from cryptography.fernet import Fernet
from werkzeug.utils import secure_filename

app = Flask(__name__)

ENCRYPTED_DIR = "encrypted_files"
DECRYPTED_DIR = "decrypted_files"

os.makedirs(ENCRYPTED_DIR, exist_ok=True)
os.makedirs(DECRYPTED_DIR, exist_ok=True)

def generate_key():
    return Fernet.generate_key()

def load_key(key_path):
    with open(key_path, "rb") as key_file:
        return key_file.read()

def save_key(key, key_path):
    with open(key_path, "wb") as key_file:
        key_file.write(key)

def encrypt_data(data, key):
    f = Fernet(key)
    return f.encrypt(data)

def decrypt_data(data, key):
    f = Fernet(key)
    return f.decrypt(data)
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/process_file', methods=['POST'])
def process_file():
    action = request.form['action']
    file_type = request.form['file_type']
    file = request.files['file']

    if file:
        filename = secure_filename(file.filename)
        file_data = file.read()
        key_path = "secret.key"
        if not os.path.exists(key_path):
            key = generate_key()
            save_key(key, key_path)
        else:
            key = load_key(key_path)
        try:
            if action == 'encrypt':
                encrypted_data = encrypt_data(file_data, key)
                encrypted_file_path = os.path.join(ENCRYPTED_DIR, f"{filename}.enc")
                with open(encrypted_file_path, "wb") as enc_file:
                    enc_file.write(encrypted_data)
                return send_file(encrypted_file_path, as_attachment=True)
            elif action == 'decrypt':
                if not filename.endswith(".enc"):
                    return "Error: The file is not in encrypted format. Please upload a valid encrypted file."
                decrypted_data = decrypt_data(file_data, key)
                decrypted_file_path = os.path.join(DECRYPTED_DIR, filename.replace(".enc", ""))
                with open(decrypted_file_path, "wb") as dec_file:
                    dec_file.write(decrypted_data)
                return send_file(decrypted_file_path, as_attachment=True)
        except Exception as e:
            return f"An error occurred: {e}"
if __name__ == '__main__':
    app.run(debug=True)
