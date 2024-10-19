import unittest
import pytest
from unittest.mock import Mock
from repository.user_repo import get_list_users, ParamListUserSchema
from sqlalchemy.orm import Session

class TestGetListUsersUseCase(unittest.TestCase):
    def setUp(self):
        self.mock_db = Mock(spec=Session)

    @pytest.mark.asyncio
    async def test_get_list_users(self):
        # parametros
        body = ParamListUserSchema(
            page=1,
            name="test",
            id_rol=1,
            date_creation=0
        )

        # dataMock
        mock_user = Mock()
        mock_user.IdUsuario = 1
        mock_user.Nombre = "Test"
        mock_user.Apellidos = "User"
        mock_user.DNI = "12345678"
        mock_user.Correo = "test@example.com"
        mock_user.Telefono = "987654321"
        mock_user.Activo = True
        mock_user.Rol.Nombre = "Admin"
        mock_user.IdRol = 1
        mock_user.FechaHoraCreacion.date.return_value.strftime.return_value = "01-01-2020"

        # Mockear la respuesta de la base de datos
        self.mock_db.query.return_value.filter.return_value.count.return_value = 1
        self.mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_user]

        response = await get_list_users(body, self.mock_db)

        self.assertEqual(response["state"], 1)
        self.assertEqual(response["data"]["total"], 1)
        self.assertEqual(len(response["data"]["users"]), 1)
        self.assertEqual(response["data"]["users"][0]["name"], "Test")
        self.assertEqual(response["data"]["users"][0]["last_name"], "User")

        self.mock_db.query.assert_called()
        self.mock_db.query.return_value.filter.assert_called()
        self.mock_db.query.return_value.filter.return_value.count.assert_called()
        self.mock_db.query.return_value.filter.return_value.order_by.assert_called()
        self.mock_db.query.return_value.filter.return_value.offset.assert_called()
        self.mock_db.query.return_value.filter.return_value.limit.assert_called()

if __name__ == "__main__":
    unittest.main()
