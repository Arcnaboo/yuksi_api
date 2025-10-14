from ..models.subsection_model import SubSection

mock_data = [
    SubSection(
        id=1, title="Hakkımızda", contentType=2,
        showInMenu=True, showInFooter=False,
        content="Biz kimiz?", isActive=True, isDeleted=False
    ),
    SubSection(
        id=2, title="İletişim", contentType=3,
        showInMenu=False, showInFooter=True,
        content="Bize ulaşın.", isActive=True, isDeleted=False
    )
]

def get_all():
    return {"success": True, "data": mock_data}

def get_by_id(id: int):
    for s in mock_data:
        if s.id == id:
            return {"success": True, "data": s}
    return {"success": False, "message": "Not found"}

def create(req):
    new_id = max(s.id for s in mock_data) + 1
    new_item = SubSection(id=new_id, **req.dict(), isActive=True, isDeleted=False)
    mock_data.append(new_item)
    return {"success": True, "data": new_item}

def update(id, req):
    for s in mock_data:
        if s.id == id:
            s.title = req.title
            s.contentType = req.contentType
            s.showInMenu = req.showInMenu
            s.showInFooter = req.showInFooter
            s.content = req.content
            return {"success": True, "data": s}
    return {"success": False, "message": "Not found"}

def delete(id):
    for s in mock_data:
        if s.id == id:
            mock_data.remove(s)
            return {"success": True, "message": f"SubSection {id} deleted"}
    return {"success": False, "message": "Not found"}
