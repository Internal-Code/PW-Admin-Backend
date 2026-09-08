from litestar import Controller, MediaType, Response, get
from litestar.response import File
from utils import get_project_root

class CommonController(Controller):
    @get("/", media_type=MediaType.HTML, summary="Root.")
    async def restricted_page(self) -> File:
        RESTRICTED_PAGE = get_project_root() / "static" / "page" / "restricted.html"
        return File(
            path=RESTRICTED_PAGE,
            media_type=MediaType.HTML,
            content_disposition_type="inline",
        )
