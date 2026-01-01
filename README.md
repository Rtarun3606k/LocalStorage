
#### Go to `authModule` directory

```bash
cd authModule
```
#### Install the dependencies

```bash
pip install -r requirements.txt
```
#### Generate Kerberos Master Key 

```bash
python3 - <<EOF
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
EOF
```

Paste the key in `encryption/enc.py`
`_KERBEROS_MASTER_KEY = b"PASTE_KEY_HERE"`
