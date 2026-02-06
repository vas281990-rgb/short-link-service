"""FastAPI application for URL shortener"""
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from typing import Optional
from app.database import Database
from app.config import BASE_URL, logger

app = FastAPI(
    title="URL Shortener",
    description="Simple URL shortening service",
    version="0.1.0"
)

db = Database()


# Request/Response models
class ShortenRequest(BaseModel):
    url: HttpUrl
    custom_code: Optional[str] = None


class ShortenResponse(BaseModel):
    short_url: str
    original_url: str


class StatsResponse(BaseModel):
    short_code: str
    original_url: str
    clicks: int
    created_at: str


@app.get("/")
def root():
    """Health check endpoint"""
    logger.info("Health check requested")
    return {"status": "ok", "message": "URL Shortener API is running"}


@app.post("/shorten", response_model=ShortenResponse, status_code=status.HTTP_201_CREATED)
def shorten_url(request: ShortenRequest):
    """
    Create shortened URL
    
    - **url**: Original URL to shorten
    - **custom_code**: Optional custom short code
    """
    try:
        short_code = db.create_short_url(
            str(request.url),
            request.custom_code
        )
        
        short_url = f"{BASE_URL}/{short_code}"
        
        logger.info(f"Shortened URL created: {short_url}")
        
        return ShortenResponse(
            short_url=short_url,
            original_url=str(request.url)
        )
    
    except ValueError as e:
        logger.error(f"Error creating short URL: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@app.get("/{short_code}")
def redirect_to_url(short_code: str):
    """
    Redirect to original URL by short code
    
    - **short_code**: The short code to redirect
    """
    original_url = db.get_original_url(short_code)
    
    if not original_url:
        logger.warning(f"Short code not found: {short_code}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found"
        )
    
    db.increment_clicks(short_code)
    logger.info(f"Redirecting {short_code} -> {original_url}")
    
    return RedirectResponse(
        url=original_url,
        status_code=status.HTTP_307_TEMPORARY_REDIRECT
    )


# Bonus endpoints

@app.delete("/{short_code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_url(short_code: str):
    """
    Delete shortened URL (bonus feature)
    
    - **short_code**: The short code to delete
    """
    deleted = db.delete_url(short_code)
    
    if not deleted:
        logger.warning(f"Attempted to delete non-existent code: {short_code}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found"
        )
    
    logger.info(f"Deleted short URL: {short_code}")
    return None


@app.get("/stats/{short_code}", response_model=StatsResponse)
def get_stats(short_code: str):
    """
    Get statistics for shortened URL (bonus feature)
    
    - **short_code**: The short code to get stats for
    """
    stats = db.get_stats(short_code)
    
    if not stats:
        logger.warning(f"Stats requested for non-existent code: {short_code}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found"
        )
    
    logger.info(f"Stats requested for {short_code}")
    
    return StatsResponse(
        short_code=stats['short_code'],
        original_url=stats['original_url'],
        clicks=stats['clicks'],
        created_at=stats['created_at']
    )