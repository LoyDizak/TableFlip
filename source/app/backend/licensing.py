"""
Модуль системы лицензирования
Проверка лицензий, защита от подмены даты
"""

import os
import json
import base64
import hashlib
import platform
import getpass
from datetime import datetime, timedelta
from pathlib import Path
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa

# @dataclass
# class LicenseInfo:
#     license_id: str
#     issued: datetime
#     expiring: datetime 
#     hwid: str

class LicenseSystem:
    """Система проверки лицензий"""

    def __init__(self, app_name: str, public_key: str):
        self.app_name: str = app_name
        self.public_key: str = public_key

        self.config_dir = self._get_config_dir()
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Файлы для хранения данных о последних запусках
        self.date_check_file_path = self.config_dir / ".lastrun"
        self.backup_date_file_path = self.config_dir / ".backup_run"
        self.boot_counter_file_path = self.config_dir / ".counter"
        self.private_key_file_path = self.config_dir / ".key"

    def _get_config_dir(self) -> Path:
        """Получить директорию для хранения конфигурации"""
        if platform.system() == "Windows":
            base = Path(os.environ.get("APPDATA", ""))
        else:
            base = Path.home() / ".config"
        
        return base / self.app_name
    
    
    def _encrypt_date(self, date_str: str) -> str:
        """Простое шифрование даты для защиты от прямого редактирования"""
        # Используем хеш от даты + соль
        salt = self.app_name.encode()
        data = f"{date_str}|{salt.decode()}".encode()
        return hashlib.sha256(data).hexdigest()


    def _save_last_run_date(self, current_date: datetime) -> None:
        """Сохранить дату последнего запуска"""
        date_str = current_date.isoformat()
        encrypted = self._encrypt_date(date_str)
        
        # Сохраняем в основной файл
        with open(self.date_check_file_path, 'w') as f:
            f.write(f"{date_str}\n{encrypted}")
        
        # Сохраняем резервную копию
        with open(self.backup_date_file_path, 'w') as f:
            f.write(f"{date_str}\n{encrypted}")


    def _load_last_run_date(self) -> datetime:
        """Загрузить дату последнего запуска"""
        try:
            with open(self.date_check_file_path, 'r') as f:
                lines = f.readlines()
                date_str = lines[0].strip()
                saved_hash = lines[1].strip()
                
                # Проверяем целостность
                if self._encrypt_date(date_str) != saved_hash:
                    raise ValueError("Date file tampered")
                
                return datetime.fromisoformat(date_str)
        except:
            # Если не удалось загрузить - возвращаем минимальную дату
            return datetime(2000, 1, 1)


    def _increment_run_counter(self) -> int:
        """Увеличить счетчик запусков"""
        try:
            with open(self.boot_counter_file_path, 'r') as f:
                counter = int(f.read().strip())
        except:
            counter = 0
        
        counter += 1
        
        with open(self.boot_counter_file_path, 'w') as f:
            f.write(str(counter))
        
        return counter


    def _check_date_tampering(self) -> bool:
        """
        Проверка на подмену системной даты
        Returns: is_valid
        """
        current_date = datetime.now()
        last_run_date = self._load_last_run_date()
        
        # Если текущая дата меньше последней известной - подмена
        if current_date < last_run_date - timedelta(days=1):
            return False
        
        # Сохраняем текущую дату
        self._save_last_run_date(current_date)
        self._increment_run_counter()
        
        return True


    def _verify_license_signature(self, license_data: dict, signature: bytes) -> bool:
        """Проверить подпись лицензии"""
        if not self.public_key:
            return True
        
        pem_key = f"-----BEGIN PUBLIC KEY-----\n{self.public_key}\n-----END PUBLIC KEY-----"

        # Загружаем публичный ключ
        public_key = serialization.load_pem_public_key(
            pem_key.encode(),
            backend=default_backend()
        )

        if not isinstance(public_key, rsa.RSAPublicKey):
            raise ValueError("Unsupported public key type")
        
        # Создаем строку данных для проверки
        data_dict = {
            "hwid": license_data["hwid"],  # ← БЕЗ .get()
            "expire": license_data["expire"],
            "issued": license_data["issued"],
            "license_id": license_data["license_id"]
        }
        data_to_verify = json.dumps(data_dict, sort_keys=True).encode()
        
        try:
            public_key.verify(
                signature,
                data_to_verify,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except:
            return False


    # def get_license_info(self, license_key: str) -> dict:
    #     """Получить информацию о лицензии"""
    #     try:
    #         decoded = base64.b64decode(license_key)
    #         license_data = json.loads(decoded.decode())
            
    #         expire_date = datetime.fromisoformat(license_data["expire"])
    #         issued_date = datetime.fromisoformat(license_data["issued"])
            
    #         return {
    #             "license_id": license_data["license_id"],
    #             "issued": issued_date.date(),
    #             "expire": expire_date.date(),
    #             "days_left": (expire_date - datetime.now()).days,
    #             "hwid_bound": bool(license_data.get("hwid"))
    #         }
    #     except:
    #         raise


    def is_license_key_valid(self, license_key: str) -> bool:
        """
        Проверить лицензионный ключ
        Returns: is_valid
        """

        if not self.public_key:
            return True
        
        # 1. Проверка на подмену даты
        if not self._check_date_tampering():
            return False
        
        # 2. Декодируем ключ
        try:
            decoded = base64.b64decode(license_key)
            license_data = json.loads(decoded.decode())
        except:
            return False
        
        # 3. Проверяем подпись
        try:
            signature = base64.b64decode(license_data["signature"])
            if not self._verify_license_signature(license_data, signature):
                return False
        except Exception:
            return False
        
        # 4. Проверяем срок действия
        try:
            expire_date = datetime.fromisoformat(license_data["expire"])
            if datetime.now() > expire_date:
                return False
        except:
            return False
        
        # 5. Проверяем Hardware ID (опционально)
        if license_data.get("hwid"):
            current_hwid = self.get_hardware_id()
            if current_hwid != license_data["hwid"]:
                return False
        
        # Все проверки пройдены
        return True


    def get_hardware_id(self) -> str:
        """Получить уникальный ID компьютера"""
        try:
            # Используем комбинацию hostname + username
            hwid = f"{platform.node()}-{getpass.getuser()}"
        except:
            # Если getpass.getuser() не работает
            hwid = f"{platform.node()}-unknown"
        
        return hashlib.sha256(hwid.encode()).hexdigest()[:16]

    def set_license_key(self, new_key: str):
        # Простая проверка, что это похоже на base64 строку
        if not new_key or len(new_key.strip()) == 0:
            raise ValueError("License key cannot be empty")
        
        # Проверяем, что это валидный base64
        try:
            base64.b64decode(new_key.strip())
        except:
            raise ValueError("License key is not valid base64")
        
        with open(self.private_key_file_path, "w") as file:
            file.write(new_key.strip())


    def get_license_key(self) -> str:
        try:
            with open(self.private_key_file_path, "r") as file:
                return file.read().strip()
        except FileNotFoundError:
            return ""
    
    def is_system_activated(self):
        return self.is_license_key_valid(self.get_license_key())