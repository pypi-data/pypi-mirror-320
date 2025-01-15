from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from .settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.login_url)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
