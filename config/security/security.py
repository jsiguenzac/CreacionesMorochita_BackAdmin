from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer

ALGORITHM = "HS256"
SECRET_KEY = """
    c0d1g0s3cr3t0_S1gü3nz@96vRLffyEtEJhhLMW6jWNrCwdKPT4HsXtGB3J0xI1i
    fUrpqKqkkokUVWaRz7FAtsavAG6YOEgsGKQHtIOTyDcIj6hUFKZAqHZyIzqwi
    eJaIg1KrRa4K6c5OJmuqZ4YnINL6WhP9HmKVkEtdEzvQ43oJ8wsZPf6ytxhiU
    kUy3H9iioXlWHObsVfyHgczr6nJBG2E02XVf4FhRjrMUCS15ryyOOypvdBtG9
    Ai7QeIdnfdsNbKiuAl9FH4EjWLTiEaG14c39zG1ruuFieMJqmekIwYjZvvmIR
    EjaDXQ9uyPo1bkOqgCbbKgxokA4YREXneR3APKoEwtffV8kVYO1Fhe0r0v8nb
    W2VnWvgRVi2oXIcJQUgLy3eOlZJOly0CJWrnzLygJRaWt3eiYOcULaUr1CKMV
    JtK9WZKPpSZhF3Luuk53gCQsIGCYSOR5Q5t54eHZzhxHviMJF2pYFEc0fOBHZ
    8Vkotu84CVeCaQezkFzoSDTHqdw55edvtbskM0R0CH1T4Z2Z9Z9Z9Z9Z9Z9Z9
"""
crypt = CryptContext(schemes=["bcrypt"], deprecated="auto")
ACCESS_TOKEN_EXPIRE_DEFAULT = 1
ACCESS_TOKEN_EXPIRE_WITH_REMIND = 15
AUDIENCE = "https://www.facebook.com/roxanadelpilar.mendo" # Identifica a quien va dirigido el token
ISSUER = "https://www.facebook.com/roxanadelpilar.mendo" # Identifica quien emite el token

oauth2 = OAuth2PasswordBearer(tokenUrl="/Login/Authenticate")