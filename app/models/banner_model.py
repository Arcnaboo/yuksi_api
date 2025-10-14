from pydantic import BaseModel

class BannerReq(BaseModel):
    title: str
    link: str = None    
    description: str = None
    images: list[str] = []

class UpdateBannerReq(BaseModel):
    id: int
    title: str
    link: str = None    
    description: str = None
    images: list[str] = []