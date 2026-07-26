from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/", response_class=HTMLResponse)
async def dashboard_page():
    """Serves the main CloudPort dashboard."""
    with open("../dashboard/templates/index.html", "r") as f:
        return HTMLResponse(content=f.read())


