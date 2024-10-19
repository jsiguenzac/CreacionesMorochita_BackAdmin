import unittest
import pytest
from unittest.mock import MagicMock, patch
from repository.auth_repo import generate_token, ModelUser, ModelRol, crypt, exit_json
from sqlalchemy.orm import Session
from schemas.User_Schema import ListUserSchema

class TestGenerateTokenUseCase(unittest.TestCase):
    
    def setUp(self):
        self.mock_db = MagicMock(spec=Session)

    @pytest.mark.asyncio
    async def test_generate_token_user_not_found(self):
        # Simular que el usuario no existe
        self.mock_db.query(ModelUser.Usuario).filter().first.return_value = None

        # Llamar a la función
        response = await generate_token(emailOrDNI="testemail@example.com", password="password123", db=self.mock_db)

        # Validar que se retorne el mensaje esperado
        self.assertEqual(response["state"], 0)
        self.assertEqual(response["data"]["mensaje"], "USUARIO_NO_ENCONTRADO")

    @pytest.mark.asyncio
    async def test_generate_token_incorrect_password(self):
        # Simular usuario existente
        mock_user = MagicMock()
        mock_user.Clave = "hashedpassword"
        self.mock_db.query(ModelUser.Usuario).filter().first.return_value = mock_user

        # Simular que la verificación de contraseña es incorrecta
        with patch("config.security.security.crypt.verify", return_value=False):
            # Llamar a la función
            response = await generate_token(emailOrDNI="testemail@example.com", password="wrongpassword", db=self.mock_db)

            # Validar que se retorne el mensaje esperado
            self.assertEqual(response["state"], 0)
            self.assertEqual(response["data"]["mensaje"], "CLAVE_INCORRECTA")

    @pytest.mark.asyncio
    async def test_generate_token_success(self):
        # Simular usuario existente
        mock_user = MagicMock()
        mock_user.IdUsuario = 1
        mock_user.Nombre = "John"
        mock_user.Apellidos = "Doe"
        mock_user.DNI = "12345678"
        mock_user.Correo = "testemail@example.com"
        mock_user.Telefono = "123456789"
        mock_user.Activo = True
        mock_user.IdRol = 2
        mock_user.Clave = "hashedpassword"

        # Simular rol del usuario
        mock_role = MagicMock()
        mock_role.Nombre = "Admin"

        # Simular la consulta de usuario y rol en la base de datos
        self.mock_db.query(ModelUser.Usuario).filter().first.return_value = mock_user
        self.mock_db.query(ModelRol.Roles).filter().first.return_value = mock_role

        # Simular verificación de contraseña correcta
        with patch("config.security.security.crypt.verify", return_value=True):
            # Llamar a la función
            response = await generate_token(emailOrDNI="testemail@example.com", password="password123", db=self.mock_db)

            # Estructura de datos esperada
            expected_data = {
                "id_user": mock_user.IdUsuario,
                "name": mock_user.Nombre,
                "last_name": mock_user.Apellidos,
                "dni": mock_user.DNI,
                "email": mock_user.Correo,
                "phone": mock_user.Telefono,
                "active": mock_user.Activo,
                "id_rol": mock_user.IdRol,
                "name_rol": mock_role.Nombre
            }

            # Validar la respuesta
            self.assertEqual(response["state"], 1)
            self.assertEqual(response["data"], expected_data)

    @pytest.mark.asyncio
    async def test_generate_token_error_handling(self):
        # Simular una excepción en la consulta a la base de datos
        self.mock_db.query.side_effect = Exception("Database error")

        # Llamar a la función
        response = await generate_token(emailOrDNI="testemail@example.com", password="password123", db=self.mock_db)

        # Validar que se retorne el mensaje de error de conexión
        self.assertEqual(response["state"], 0)
        self.assertEqual(response["data"]["mensaje"], "Error de conexión con la base de datos")

if __name__ == "__main__":
    unittest.main()
