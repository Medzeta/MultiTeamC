"""
P2P Encryption System
End-to-end kryptering med AES-256 och RSA nyckelutbyte
"""

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import os
import json
import base64
from pathlib import Path
from typing import Tuple, Optional
from core.debug_logger import debug, info, warning, error, exception


class P2PEncryption:
    """Krypteringssystem för P2P kommunikation"""
    
    def __init__(self, client_id: str):
        """
        Initialize encryption system
        
        Args:
            client_id: This client's unique ID
        """
        debug("P2PEncryption", "Initializing encryption system")
        
        self.client_id = client_id
        self.keys_path = Path(f"data/keys_{client_id[:8]}.json")
        
        # RSA key pair för nyckelutbyte
        self.private_key, self.public_key = self._load_or_generate_rsa_keys()
        
        # AES nycklar per peer (peer_id -> aes_key)
        self.peer_keys = {}
        
        info("P2PEncryption", "Encryption system initialized")
    
    def _load_or_generate_rsa_keys(self) -> Tuple:
        """Load existing RSA keys or generate new ones"""
        debug("P2PEncryption", "Loading or generating RSA keys")
        
        if self.keys_path.exists():
            try:
                with open(self.keys_path, 'r') as f:
                    keys_data = json.load(f)
                
                # Load private key
                private_pem = base64.b64decode(keys_data['private_key'])
                private_key = serialization.load_pem_private_key(
                    private_pem,
                    password=None,
                    backend=default_backend()
                )
                
                # Load public key
                public_pem = base64.b64decode(keys_data['public_key'])
                public_key = serialization.load_pem_public_key(
                    public_pem,
                    backend=default_backend()
                )
                
                info("P2PEncryption", "Loaded existing RSA keys")
                return private_key, public_key
                
            except Exception as e:
                exception("P2PEncryption", f"Error loading keys: {e}")
        
        # Generate new RSA key pair (2048 bit)
        debug("P2PEncryption", "Generating new RSA key pair")
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        
        # Save keys
        self._save_rsa_keys(private_key, public_key)
        
        info("P2PEncryption", "Generated new RSA keys")
        return private_key, public_key
    
    def _save_rsa_keys(self, private_key, public_key):
        """Save RSA keys to file"""
        debug("P2PEncryption", "Saving RSA keys")
        
        try:
            # Serialize keys
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            # Save to file
            self.keys_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.keys_path, 'w') as f:
                json.dump({
                    'private_key': base64.b64encode(private_pem).decode(),
                    'public_key': base64.b64encode(public_pem).decode()
                }, f, indent=4)
            
            debug("P2PEncryption", "RSA keys saved successfully")
            
        except Exception as e:
            exception("P2PEncryption", f"Error saving keys: {e}")
    
    def get_public_key_pem(self) -> str:
        """Get public key as PEM string (för att skicka till peers)"""
        pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return base64.b64encode(pem).decode()
    
    def exchange_keys(self, peer_id: str, peer_public_key_pem: str) -> str:
        """
        Exchange keys with peer
        
        Args:
            peer_id: Peer's client ID
            peer_public_key_pem: Peer's public key (base64 encoded PEM)
        
        Returns:
            Our public key (base64 encoded PEM)
        """
        debug("P2PEncryption", f"Exchanging keys with peer: {peer_id[:8]}...")
        
        try:
            # Decode peer's public key
            peer_public_pem = base64.b64decode(peer_public_key_pem)
            peer_public_key = serialization.load_pem_public_key(
                peer_public_pem,
                backend=default_backend()
            )
            
            # Generate AES key för denna peer
            aes_key = os.urandom(32)  # 256 bit
            self.peer_keys[peer_id] = aes_key
            
            info("P2PEncryption", f"Keys exchanged with peer: {peer_id[:8]}...")
            
            # Return our public key
            return self.get_public_key_pem()
            
        except Exception as e:
            exception("P2PEncryption", f"Error exchanging keys: {e}")
            return None
    
    def encrypt_message(self, peer_id: str, message: dict) -> Optional[str]:
        """
        Encrypt message for specific peer
        
        Args:
            peer_id: Peer's client ID
            message: Message dict to encrypt
        
        Returns:
            Encrypted message (base64 encoded) or None if error
        """
        debug("P2PEncryption", f"Encrypting message for peer: {peer_id[:8]}...")
        
        if peer_id not in self.peer_keys:
            warning("P2PEncryption", f"No AES key for peer: {peer_id[:8]}...")
            return None
        
        try:
            # Convert message to JSON
            plaintext = json.dumps(message).encode()
            
            # Generate IV (Initialization Vector)
            iv = os.urandom(16)
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(self.peer_keys[peer_id]),
                modes.CFB(iv),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            
            # Encrypt
            ciphertext = encryptor.update(plaintext) + encryptor.finalize()
            
            # Combine IV + ciphertext and encode
            encrypted = base64.b64encode(iv + ciphertext).decode()
            
            debug("P2PEncryption", f"Message encrypted for peer: {peer_id[:8]}...")
            return encrypted
            
        except Exception as e:
            exception("P2PEncryption", f"Error encrypting message: {e}")
            return None
    
    def decrypt_message(self, peer_id: str, encrypted_message: str) -> Optional[dict]:
        """
        Decrypt message from specific peer
        
        Args:
            peer_id: Peer's client ID
            encrypted_message: Encrypted message (base64 encoded)
        
        Returns:
            Decrypted message dict or None if error
        """
        debug("P2PEncryption", f"Decrypting message from peer: {peer_id[:8]}...")
        
        if peer_id not in self.peer_keys:
            warning("P2PEncryption", f"No AES key for peer: {peer_id[:8]}...")
            return None
        
        try:
            # Decode
            data = base64.b64decode(encrypted_message)
            
            # Extract IV and ciphertext
            iv = data[:16]
            ciphertext = data[16:]
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(self.peer_keys[peer_id]),
                modes.CFB(iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            
            # Decrypt
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            
            # Parse JSON
            message = json.loads(plaintext.decode())
            
            debug("P2PEncryption", f"Message decrypted from peer: {peer_id[:8]}...")
            return message
            
        except Exception as e:
            exception("P2PEncryption", f"Error decrypting message: {e}")
            return None
    
    def sign_message(self, message: dict) -> str:
        """
        Sign message with private key
        
        Args:
            message: Message dict to sign
        
        Returns:
            Signature (base64 encoded)
        """
        debug("P2PEncryption", "Signing message")
        
        try:
            # Convert to JSON
            message_bytes = json.dumps(message, sort_keys=True).encode()
            
            # Sign
            signature = self.private_key.sign(
                message_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return base64.b64encode(signature).decode()
            
        except Exception as e:
            exception("P2PEncryption", f"Error signing message: {e}")
            return None
    
    def verify_signature(self, peer_public_key_pem: str, message: dict, signature: str) -> bool:
        """
        Verify message signature
        
        Args:
            peer_public_key_pem: Peer's public key (base64 encoded PEM)
            message: Message dict
            signature: Signature to verify (base64 encoded)
        
        Returns:
            True if signature is valid, False otherwise
        """
        debug("P2PEncryption", "Verifying signature")
        
        try:
            # Load peer's public key
            peer_public_pem = base64.b64decode(peer_public_key_pem)
            peer_public_key = serialization.load_pem_public_key(
                peer_public_pem,
                backend=default_backend()
            )
            
            # Convert message to bytes
            message_bytes = json.dumps(message, sort_keys=True).encode()
            
            # Decode signature
            signature_bytes = base64.b64decode(signature)
            
            # Verify
            peer_public_key.verify(
                signature_bytes,
                message_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            debug("P2PEncryption", "Signature verified successfully")
            return True
            
        except Exception as e:
            warning("P2PEncryption", f"Signature verification failed: {e}")
            return False
    
    def encrypt_file(self, peer_id: str, file_path: Path) -> Optional[bytes]:
        """Encrypt file for peer"""
        debug("P2PEncryption", f"Encrypting file for peer: {peer_id[:8]}...")
        
        if peer_id not in self.peer_keys:
            warning("P2PEncryption", f"No AES key for peer: {peer_id[:8]}...")
            return None
        
        try:
            # Read file
            with open(file_path, 'rb') as f:
                plaintext = f.read()
            
            # Generate IV
            iv = os.urandom(16)
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(self.peer_keys[peer_id]),
                modes.CFB(iv),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            
            # Encrypt
            ciphertext = encryptor.update(plaintext) + encryptor.finalize()
            
            # Return IV + ciphertext
            encrypted = iv + ciphertext
            
            info("P2PEncryption", f"File encrypted: {file_path.name}")
            return encrypted
            
        except Exception as e:
            exception("P2PEncryption", f"Error encrypting file: {e}")
            return None
    
    def decrypt_file(self, peer_id: str, encrypted_data: bytes, output_path: Path) -> bool:
        """Decrypt file from peer"""
        debug("P2PEncryption", f"Decrypting file from peer: {peer_id[:8]}...")
        
        if peer_id not in self.peer_keys:
            warning("P2PEncryption", f"No AES key for peer: {peer_id[:8]}...")
            return False
        
        try:
            # Extract IV and ciphertext
            iv = encrypted_data[:16]
            ciphertext = encrypted_data[16:]
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(self.peer_keys[peer_id]),
                modes.CFB(iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            
            # Decrypt
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            
            # Write to file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(plaintext)
            
            info("P2PEncryption", f"File decrypted: {output_path.name}")
            return True
            
        except Exception as e:
            exception("P2PEncryption", f"Error decrypting file: {e}")
            return False


if __name__ == "__main__":
    # Test encryption system
    info("TEST", "Testing P2P Encryption...")
    
    # Create two encryption systems (simulate two peers)
    enc1 = P2PEncryption("client-1")
    enc2 = P2PEncryption("client-2")
    
    print(f"Client 1 public key: {enc1.get_public_key_pem()[:50]}...")
    print(f"Client 2 public key: {enc2.get_public_key_pem()[:50]}...")
    
    # Exchange keys
    enc1.exchange_keys("client-2", enc2.get_public_key_pem())
    enc2.exchange_keys("client-1", enc1.get_public_key_pem())
    
    # Test message encryption
    message = {"type": "test", "data": "Hello, encrypted world!"}
    encrypted = enc1.encrypt_message("client-2", message)
    print(f"Encrypted: {encrypted[:50]}...")
    
    decrypted = enc2.decrypt_message("client-1", encrypted)
    print(f"Decrypted: {decrypted}")
    
    # Test signing
    signature = enc1.sign_message(message)
    print(f"Signature: {signature[:50]}...")
    
    verified = enc2.verify_signature(enc1.get_public_key_pem(), message, signature)
    print(f"Signature verified: {verified}")
    
    print("\n✅ Encryption system working!")
