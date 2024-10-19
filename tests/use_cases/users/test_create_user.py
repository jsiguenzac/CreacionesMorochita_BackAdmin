import unittest
import pytest
from unittest.mock import Mock, patch
from repository.user_repo import add_user, UserSchema
from sqlalchemy.orm import Session
from datetime import datetime

class TestAddUserUseCase(unittest.TestCase):
    def setUp(self):
        self.mock_db = Mock(spec=Session)
        self.mock_email_service = Mock()
        
        # Simulación del servicio de envío de correos
        patch('utils.methods.EmailServiceEnv', return_value=self.mock_email_service).start()

    @pytest.mark.asyncio
    async def test_add_new_user(self):
        user = UserSchema(
            name="Joel",
            last_name="Sigüenza",
            email="siguenzajoel10@gmail.com",
            dni="12345678",
            phone="987654321",
            id_rol=1
        )
        
        user_creation = {
            "email": "admin@example.com"
        }
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = None  # No existe el usuario

        # Llamar a la función
        response = await add_user(user, user_creation, self.mock_db)

        # Validar que se haya creado el nuevo usuario
        self.assertEqual(response["state"], 1)
        self.assertEqual(response["data"]["mensaje"], "USUARIO_CREADO")

        # Comprobar que se llamaron a las funciones necesarias
        self.mock_db.add.assert_called_once()
        self.mock_db.commit.assert_called_once()
        self.mock_email_service.send_email.assert_called_once()

    @pytest.mark.asyncio
    async def test_user_already_exists(self):
        user = UserSchema(
            name="Joel",
            last_name="Sigüenza",
            email="siguenzajoel10@gmail.com",
            dni="12345678",
            phone="987654321",
            id_rol=1
        )
        
        user_creation = {
            "email": "admin@example.com"
        }

        # Simular un usuario existente
        existing_user = Mock()
        existing_user.Activo = True
        self.mock_db.query.return_value.filter.return_value.first.return_value = existing_user

        # Llamar a la función
        response = await add_user(user, user_creation, self.mock_db)

        # Validar que no se pueda crear un usuario existente
        self.assertEqual(response["state"], 0)
        self.assertEqual(response["data"]["mensaje"], "USUARIO_YA_EXISTE")

        # Comprobar que se llama a commit y no a add
        self.mock_db.commit.assert_called_once()
        self.mock_db.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_dni_exists(self):
        user = UserSchema(
            name="Joel",
            last_name="Sigüenza",
            email="siguenzajoel10@gmail.com",
            dni="12345678",
            phone="987654321",
            id_rol=1
        )
        
        user_creation = {
            "email": "admin@example.com"
        }

        # Simular que el DNI ya existe
        self.mock_db.query.return_value.filter.return_value.first.return_value = None  # No existe el usuario
        self.mock_db.query.return_value.filter.return_value.count.return_value = 1  # DNI existe

        # Llamar a la función
        response = await add_user(user, user_creation, self.mock_db)

        # Validar que no se pueda crear el usuario debido a que el DNI existe
        self.assertEqual(response["state"], 0)
        self.assertEqual(response["data"]["mensaje"], "DNI_YA_EXISTE")

    def tearDown(self):
        patch.stopall()

if __name__ == "__main__":
    unittest.main()
