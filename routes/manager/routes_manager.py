# routes_manager.py
from fastapi import FastAPI
from routes import (
    auth_api as auth,
    rol_api as rol,
    user_api as user,
    permissions_api as permissions,
    products_api as products,
    categoryproduct_api as catprod,
    sales_api as sales
)

class RoutesManager:
    def __init__(self, app: FastAPI):
        self.app = app

    def include_routes(self):
        self.app.include_router(auth.router)
        self.app.include_router(rol.router)
        self.app.include_router(user.router)
        #self.app.include_router(permissions.router)
        self.app.include_router(products.router)
        self.app.include_router(catprod.router)
        self.app.include_router(sales.router)
