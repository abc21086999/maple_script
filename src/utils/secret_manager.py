import keyring

class SecretManager:
    SERVICE_NAME = "MapleScript"
    STORAGE_PW_KEY = "second_password"

    @classmethod
    def set_storage_password(cls, password: str):
        """
        Securely saves the storage password using Windows Credential Manager.
        """
        if password is not None:
            # If password is empty string, we might want to delete it or save empty. 
            # keyring.set_password usually handles updates fine.
            keyring.set_password(cls.SERVICE_NAME, cls.STORAGE_PW_KEY, password)

    @classmethod
    def get_storage_password(cls) -> str:
        """
        Retrieves the storage password from Windows Credential Manager.
        Returns None if not found.
        """
        return keyring.get_password(cls.SERVICE_NAME, cls.STORAGE_PW_KEY)
