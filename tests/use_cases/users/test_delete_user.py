import unittest
import pytest
from unittest.mock import Mock
from repository.user_repo import delete_user_by_id, UserSchema
from sqlalchemy.orm import Session
from datetime import datetime

class TestDeleteUserByIdUseCase(unittest.TestCase):
    def setUp(self):
        self.mock_db = Mock(spec=Session)
        self.user_schema = UserSchema(
            id_rol=1, 
            email="admin@example.com",
            name="Admin",
            last_name="Admin",
            dni=12345678
        )

    @pytest.mark.asyncio
    async def test_delete_user_success(self):
        # Simular un usuario activo
        mock_user = Mock()
        mock_user.IdUsuario = 1
        mock_user.Activo = True

        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        response = await delete_user_by_id(1, self.user_schema, self.mock_db)

        self.assertTrue(mock_user.Activo is False)
        self.assertEqual(response["state"], 1)
        self.assertEqual(response["data"]["mensaje"], "USUARIO_ELIMINADO")

    @pytest.mark.asyncio
    async def test_user_not_found(self):
        # Simular que no se encuentra el usuario
        self.mock_db.query.return_value.filter.return_value.first.return_value = None

        response = await delete_user_by_id(1, self.user_schema, self.mock_db)

        self.assertEqual(response["state"], 0)
        self.assertEqual(response["data"]["mensaje"], "USUARIO_NO_ENCONTRADO")

    @pytest.mark.asyncio
    async def test_user_no_permissions(self):
        # Simular un usuario que no tiene permisos
        user_schema_no_permission = UserSchema(id_rol=2, email="user@example.com")  # Rol no administrador
        response = await delete_user_by_id(1, user_schema_no_permission, self.mock_db)

        self.assertEqual(response["state"], 0)
        self.assertEqual(response["data"]["mensaje"], "NO_TIENE_PERMISOS")

    @pytest.mark.asyncio
    async def test_exception_handling(self):
        # Simular una excepción en la base de datos
        self.mock_db.query.side_effect = Exception("Database error")

        response = await delete_user_by_id(1, self.user_schema, self.mock_db)

        self.assertEqual(response["state"], 0)
        self.assertEqual(response["data"], "Database error")

if __name__ == "__main__":
    unittest.main()
