import unittest
import pytest
from unittest.mock import Mock
from repository.user_repo import find_user_by_id
from sqlalchemy.orm import Session

class TestFindUserByIdUseCase(unittest.TestCase):
    def setUp(self):
        self.mock_db = Mock(spec=Session)

    @pytest.mark.asyncio
    async def test_find_active_user(self):
        # Simular un usuario activo
        mock_user = Mock()
        mock_user.IdUsuario = 1
        mock_user.Nombre = "Joel"
        mock_user.Apellidos = "Sigüenza"
        mock_user.DNI = "12345678"
        mock_user.Correo = "siguenzajoel10@gmail.com"
        mock_user.Telefono = "987654321"
        mock_user.Activo = True
        mock_user.Rol.Nombre = "Admin"
        mock_user.IdRol = 1

        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        response = await find_user_by_id(1, self.mock_db)
        print('reeeeesponse', response)
        self.assertEqual(response["state"], 1)
        self.assertEqual(response["data"]["id_user"], mock_user.IdUsuario)

    @pytest.mark.asyncio
    async def test_user_not_found(self):
        # Simular que no se encuentra el usuario
        self.mock_db.query.return_value.filter.return_value.first.return_value = None

        response = await find_user_by_id(1, self.mock_db)

        self.assertEqual(response["state"], 0)
        self.assertEqual(response["data"]["mensaje"], "USUARIO_NO_ENCONTRADO")

    @pytest.mark.asyncio
    async def test_user_inactive(self):
        # Simular un usuario inactivo
        mock_user = Mock()
        mock_user.IdUsuario = 1
        mock_user.Nombre = "Joel"
        mock_user.Apellidos = "Sigüenza"
        mock_user.DNI = "12345678"
        mock_user.Correo = "siguenzajoel10@gmail.com"
        mock_user.Telefono = "987654321"
        mock_user.Activo = False
        mock_user.Rol.Nombre = "Admin"
        mock_user.IdRol = 1

        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        response = await find_user_by_id(1, self.mock_db)

        self.assertEqual(response["state"], 0)
        self.assertEqual(response["data"]["mensaje"], "USUARIO_INACTIVO")

    @pytest.mark.asyncio
    async def test_exception_handling(self):
        # Simular una excepción en la base de datos
        self.mock_db.query.side_effect = Exception("Database error")

        response = await find_user_by_id(1, self.mock_db)

        self.assertEqual(response["state"], 0)
        self.assertEqual(response["data"], "Database error")

if __name__ == "__main__":
    unittest.main()
