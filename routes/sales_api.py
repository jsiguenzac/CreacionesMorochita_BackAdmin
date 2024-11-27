from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from routes.auth_api import current_user
from repository.sales_repo import *

router = APIRouter(
    prefix="/Sales", 
    tags=["Ventas"], 
    responses={
        404: {
            "message": "No encontrado"
        }
    },
    dependencies=[Depends(current_user)],
)

@router.post("/List", status_code=status.HTTP_200_OK)
async def get_sales(body: ParamListSalesSchema, db: Session = Depends(get_db)):
    try:
        if body.page <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Página no válida")
        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado")
        return await get_list_sales(body, db)
    except Exception as e:
        return exit_json(0, str(e))
    
@router.post("/Add", status_code=status.HTTP_200_OK)
async def add_new_sale(body: ParamAddUpdateSale, current_user: UserSchema = Depends(current_user), db: Session = Depends(get_db)):
    try:
        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado")
        return await add_sale(body, current_user, db)
    except Exception as e:
        return exit_json(0, str(e))

@router.post("/Update", status_code=status.HTTP_200_OK)
async def update_sale_by_id(body: ParamAddUpdateSale, current_user: UserSchema = Depends(current_user), db: Session = Depends(get_db)):
    try:
        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado")
        return await update_sale(body, current_user, db)
    except Exception as e:
        return exit_json(0, str(e))
    
@router.post("/Details/{id_sale}", status_code=status.HTTP_200_OK)
async def get_sale_detail(id_sale: int, db: Session = Depends(get_db)):
    try:
        if id_sale <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de venta no válido")
        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado")
        return await details_sale(id_sale, db)
    except Exception as e:
        return exit_json(0, str(e))

@router.post("/Report", status_code=status.HTTP_200_OK)
async def get_sales_report(body: ParamReportSalesSchema, db: Session = Depends(get_db)):
    try:
        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado")
        return await get_report_sales(body, db)
    except Exception as e:
        return exit_json(0, str(e))

@router.post("/Report/Export", status_code=status.HTTP_200_OK)
async def export_sales_report(body: ParamReportSalesSchema, db: Session = Depends(get_db)):
    try:
        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado")
        result = await export_report_sales(body, db)
        if result.state == 0:
            return result
        
        filename = result.data["name_file"]
        if not filename.endswith(".xlsx"):
            filename += ".xlsx"
        return StreamingResponse(
            result.data["data_export"],
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
            }
        )
    except Exception as e:
        return exit_json(0, str(e))


@router.post("/Boleta/Generate/{id_sale}", status_code=status.HTTP_200_OK)
async def export_sales_report(id_sale: int, db: Session = Depends(get_db)):
    try:
        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado")
        result = await generate_boleta_sale(id_sale, db)
        if result.state == 0:
            return result
        
        filename = result.data["name_file"]
        if not filename.endswith(".pdf"):
            filename += ".pdf"
        return StreamingResponse(
            result.data["data_export"],
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
            }
        )
    except Exception as e:
        return exit_json(0, str(e))
