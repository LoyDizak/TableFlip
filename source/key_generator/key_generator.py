"""
Генератор лицензионных ключей
Используется отдельно от основного приложения для создания лицензий
"""

import os
import json
import base64
import uuid
from datetime import datetime
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa


class KeyGenerator:
    """Генератор лицензионных ключей"""
    
    def __init__(self, private_key_path: str = ""):
        """
        Args:
            private_key_path: путь к файлу с приватным ключом
        """
        self.private_key = None
        self.public_key = None
        
        if private_key_path and os.path.exists(private_key_path):
            self.load_keys(private_key_path)
    
    def generate_rsa_keys(self) -> None:
        """Сгенерировать новую пару RSA ключей"""
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
    
    def save_keys(self, private_key_path: str, public_key_path: str) -> None:
        """Сохранить ключи в файлы"""
        if not self.private_key:
            raise ValueError("No keys to save. Generate keys first.")
        
        # Сохраняем приватный ключ
        with open(private_key_path, 'wb') as f:
            f.write(self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        # Сохраняем публичный ключ
        if self.public_key:
            with open(public_key_path, 'wb') as f:
                f.write(self.public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ))
    
    def load_keys(self, private_key_path: str) -> None:
        """Загрузить ключи из файла"""
        with open(private_key_path, 'rb') as f:
            self.private_key = serialization.load_pem_private_key(
                f.read(),
                password=None,
                backend=default_backend()
            )
        self.public_key = self.private_key.public_key()
    
    def get_public_key_pem(self) -> str:
        """Получить публичный ключ в формате PEM (для встраивания в приложение)"""
        if not self.public_key:
            raise ValueError("No public key available. Generate or load keys first.")
        
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()
    
    def generate_license(
        self,
        expire_date: datetime,
        hwid: str = "",
        license_id: str = ""
    ) -> str:
        """
        Сгенерировать лицензионный ключ
        
        Args:
            expire_date: дата истечения лицензии
            hwid: Hardware ID для привязки (пустая строка = без привязки)
            license_id: уникальный ID лицензии (генерируется автоматически если пустой)
        
        Returns:
            Base64-encoded license key
        """
        if not self.private_key:
            raise ValueError("Private key not loaded. Generate or load keys first.")
        
        # Генерируем ID если не указан
        if not license_id:
            license_id = str(uuid.uuid4())
        
        # Данные лицензии
        license_data = {
            "hwid": hwid,
            "expire": expire_date.isoformat(),
            "issued": datetime.now().isoformat(),
            "license_id": license_id
        }

        if not isinstance(self.private_key, rsa.RSAPrivateKey):
            raise ValueError("Unsupported private key type")
        
        # Создаем подпись
        data_to_sign = json.dumps(license_data, sort_keys=True).encode()
        signature = self.private_key.sign(
            data_to_sign,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        # Добавляем подпись к данным
        license_data["signature"] = base64.b64encode(signature).decode()
        
        # Кодируем все в Base64
        license_json = json.dumps(license_data)
        license_key = base64.b64encode(license_json.encode()).decode()
        
        return license_key