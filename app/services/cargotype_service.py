from typing import Any, Dict, List, Optional, Tuple

# TODO : cagri : Implement actual database operations and error handling

async def get_all_cargotypes() -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
    # Implementation for fetching all cargo types from the database
    return [
        {"id": 1, "name": "Small Package", "price": 5.0, "description": "Up to 1kg"},
        {"id": 2, "name": "Medium Package", "price": 10.0, "description": "1kg to 5kg"},
        {"id": 3, "name": "Large Package", "price": 20.0, "description": "5kg to 20kg"},
    ], None

async def add_cargotype(name: str, price: float, description: str = None) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    # Implementation for adding a new cargo type to the database
    return {"id": 4, "name": name, "price": price, "description": description}, None

async def update_cargotype(cargotype_id: int, name: str, price: float, description: str = None) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    # Implementation for updating an existing cargo type in the database
    return {"id": cargotype_id, "name": name, "price": price, "description": description}, None   

async def get_cargotype(cargotype_id: int) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    # Implementation for fetching a specific cargo type by ID from the database
    return {"id": cargotype_id, "name": "Sample Cargo", "price": 15.0, "description": "Sample Description"}, None 

async def delete_cargotype(cargotype_id: int) -> Tuple[Optional[bool], Optional[str]]:
    # Implementation for deleting a specific cargo type by ID from the database
    return True, None
