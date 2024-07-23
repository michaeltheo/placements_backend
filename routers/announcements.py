from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException, Query

router = APIRouter(
    prefix='/announcements',
    tags=['Announcements']
)

# I had a problem fetching the announcmenets client side, so we had to fetch via the server.
API_URL = "https://aboard.iee.ihu.gr/api/v2/announcements"


@router.get("/")
async def fetch_announcements(
        page: int = Query(1, ge=1),
        items_per_page: int = Query(10, alias="itemsPerPage"),
        updated_after: Optional[str] = Query(None, alias="updatedAfter"),
        updated_before: Optional[str] = Query(None, alias="updatedBefore"),
        search_text: Optional[str] = Query(None, alias="searchText")
):
    """
    Fetches announcements from the IHU IEE announcement API.

    Parameters:
    - page: The page number (default: 1)
    - items_per_page: Number of items per page (default: 10)
    - updated_after: Filter for announcements updated after this date
    - updated_before: Filter for announcements updated before this date
    - search_text: Search text to filter announcements

    Returns:
    - JSON response from the announcements API
    """
    try:
        url = httpx.URL(API_URL)
        params = {
            "tags[]": "11",
            "perPage": str(items_per_page),
            "page": str(page)
        }

        if updated_after:
            params["updatedAfter"] = updated_after
        if updated_before:
            params["updatedBefore"] = updated_before
        if search_text:
            params["title"] = search_text

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
