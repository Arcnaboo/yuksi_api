from pydantic import BaseModel

class BannerReq(BaseModel):
    title: str
    image_url: str
    priority: int = 0
    active: bool = True

class UpdateBannerReq(BaseModel):
    id: str
    title: str
    image_url: str
    priority: int = 0
    active: bool = True