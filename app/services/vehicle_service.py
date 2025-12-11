import json
from typing import List
from uuid import UUID

from app.models.vehicles_models import VehicleFeatureRequest, VehicleRequest, VehicleTypeRequest, VehicleFeatureResponse, VehicleResponse, VehicleTypeResponse

from typing import List
from fastapi import HTTPException, status
import app.utils.database_async as db
from app.models.vehicles_models import VehicleResponse

async def _get_vehicle_features(vehicle_id: str):
    try:
        query = """
            SELECT vf.feature
            FROM vehicle_features_map vfm
            JOIN vehicle_features vf ON vf.feature = vfm.feature_name
            WHERE vfm.vehicle_id = $1
        """
    
        rows = await db.fetch_all(query, vehicle_id)
        return [r["feature"] for r in rows]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"_get_vehicle_features: {e}")

async def get_all_vehicles(
    size: int,
    offset: int,
    vehicle_type: str | None = None,
    vehicle_features: list[str] | None = None,
) -> List[VehicleResponse]:
    try:
        params = [size, offset]
        where_clauses = []

        # vehicle_type filtresi
        if vehicle_type:
            where_clauses.append(f"v.vehicle_type = ${len(params) + 1}")
            params.append(vehicle_type)

        # vehicle_features listesi filtresi (AND mantığı)
        if vehicle_features and len(vehicle_features) > 0:
            # Her feature için EXISTS ekle
            for feature in vehicle_features:
                where_clauses.append(f"""
                    EXISTS (
                        SELECT 1
                        FROM vehicle_features_map vfm
                        WHERE vfm.vehicle_id = v.id;,i
                        AND vfm.feature_name = ${len(params) + 1}
                    )
                """)
                params.append(feature)

        where_sql = ""
        if where_clauses:
            where_sql = "WHERE " + " AND ".join(where_clauses)

        query = f"""
            SELECT
                v.id,
                v.year,
                v.model,
                v.plate,
                v.driver_id,
                v.make,
                vt.type AS vehicle_type
            FROM vehicles v
            LEFT JOIN vehicle_types vt ON vt.type = v.vehicle_type
            {where_sql}
            ORDER BY v.created_at DESC
            LIMIT $1 OFFSET $2
        """

        rows = await db.fetch_all(query, *params)

        vehicles: List[VehicleResponse] = []

        for r in rows:
            features = await _get_vehicle_features(str(r["id"]))

            vehicles.append(VehicleResponse(
                id=str(r["id"]),
                year=r["year"],
                model=r["model"],
                make=r["make"],
                plate=r["plate"],
                driver_id=str(r["driver_id"]),
                type=r["vehicle_type"],
                features=features
            ))

        return vehicles

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"get_all_vehicles: {e}")


async def create_vehicle(req: VehicleRequest, driver_id: str) -> VehicleResponse:
    try:
        driver = await db.fetch_one(
            "SELECT id FROM drivers WHERE id = $1",
            driver_id
        )
        if not driver:
            raise HTTPException(
                status_code=404,
                detail="Driver not found"
            )

        type_row = await db.fetch_one(
            "SELECT type FROM vehicle_types WHERE type = $1",
            req.type
        )
        if not type_row:
            raise HTTPException(
                status_code=400,
                detail="Vehicle type not found"
            )
        type_value = type_row["type"]

        # Feature doğrulama
        if req.features:
            feature_rows = await db.fetch_all(
                "SELECT feature FROM vehicle_features WHERE feature = ANY($1)",
                req.features
            )
            valid_features = {r["feature"] for r in feature_rows}
            invalid = [f for f in req.features if f not in valid_features]

            if invalid:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid features: {invalid}"
                )
        else:
            valid_features = set()

        # Insert vehicle
        query = """
            INSERT INTO vehicles (year, model, make, plate, driver_id, vehicle_type)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id, year, model, make, plate, driver_id, vehicle_type
        """

        row = await db.fetch_one(
            query,
            req.year, req.model, req.make,
            req.plate, driver_id, type_value
        )

        vehicle_id = str(row["id"])

        # Insert map table
        if valid_features:
            insert_map = """
                INSERT INTO vehicle_features_map (vehicle_id, feature_name)
                VALUES ($1, $2)
            """
            for feature in valid_features:
                await db.execute(insert_map, vehicle_id, feature)

        features = await _get_vehicle_features(vehicle_id)

        return VehicleResponse(
            id=vehicle_id,
            year=row["year"],
            model=row["model"],
            make=row["make"],
            plate=row["plate"],
            driver_id=str(row["driver_id"]),
            type=row["vehicle_type"],
            features=features
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"create_vehicle: {e}")

async def get_vehicle(vehicle_id: str) -> VehicleResponse:
    try:
        query = """
            SELECT id, year, model, make, plate, vehicle_type, driver_id
            FROM vehicles
            WHERE id = $1
        """

        r = await db.fetch_one(query, vehicle_id)
        if not r:
            raise HTTPException(404, "Vehicle not found")

        features = await _get_vehicle_features(vehicle_id)

        return VehicleResponse(
            id=str(r["id"]),
            year=r["year"],
            model=r["model"],
            make=r["make"],
            plate=r["plate"],
            driver_id=str(r["driver_id"]),
            type=r["vehicle_type"],
            features=features
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"get_vehicle: {e}")


async def update_vehicle(vehicle_id: str, req: VehicleRequest, driver_id: str) -> VehicleResponse:
    try:
        driver = await db.fetch_one(
            "SELECT id FROM drivers WHERE id = $1",
            driver_id
        )
        if not driver:
            raise HTTPException(404, "Driver not found")

        type_row = await db.fetch_one(
            "SELECT type FROM vehicle_types WHERE type = $1",
            req.type
        )
        if not type_row:
            raise HTTPException(400, "Vehicle type not found")

        type_value = type_row["type"]

        # Feature validation
        if req.features:
            rows = await db.fetch_all(
                "SELECT feature FROM vehicle_features WHERE feature = ANY($1)",
                req.features
            )
            valid = {r["feature"] for r in rows}
            invalid = [f for f in req.features if f not in valid]

            if invalid:
                raise HTTPException(400, f"Invalid features: {invalid}")
        else:
            valid = set()

        # Update vehicle
        query = """
            UPDATE vehicles
            SET year = $1,
                model = $2,
                make = $3,
                plate = $4,
                driver_id = $5,
                vehicle_type = $6
            WHERE id = $7
            RETURNING id, year, model, make, plate, driver_id, vehicle_type
        """

        row = await db.fetch_one(
            query,
            req.year, req.model, req.make,
            req.plate, driver_id,
            type_value, vehicle_id
        )

        if not row:
            raise HTTPException(404, "Vehicle not found")

        # Reset feature map
        await db.execute(
            "DELETE FROM vehicle_features_map WHERE vehicle_id = $1",
            vehicle_id
        )

        # Insert updated features
        if valid:
            insert_map = """
                INSERT INTO vehicle_features_map (vehicle_id, feature_name)
                VALUES ($1, $2)
            """
            for feature in valid:
                await db.execute(insert_map, vehicle_id, feature)

        features = await _get_vehicle_features(vehicle_id)

        return VehicleResponse(
            id=str(row["id"]),
            year=row["year"],
            model=row["model"],
            make=row["make"],
            plate=row["plate"],
            driver_id=str(row["driver_id"]),
            type=row["vehicle_type"],
            features=features
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"update_vehicle: {e}")

async def get_vehicle_types() -> List[VehicleTypeResponse]:
    try:
        query = """
            SELECT id, type, description, created_at
            FROM vehicle_types
            ORDER BY created_at DESC
        """

        rows = await db.fetch_all(query)

        return [
            VehicleTypeResponse(
                id=str(r["id"]),
                type=r["type"],
                description=r["description"],
                created_at=r["created_at"].isoformat()
            )
            for r in rows
        ]
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"get_vehicle_types: {e}")

async def post_vehicle_type(req: VehicleTypeRequest) -> VehicleTypeResponse:
    try:
        exists = await db.fetch_one(
            "SELECT id FROM vehicle_types WHERE type = $1",
            req.type
        )

        if exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vehicle type already exists"
            )

        query = """
            INSERT INTO vehicle_types (type, description)
            VALUES ($1, $2)
            RETURNING id, type, description, created_at
        """

        row = await db.fetch_one(query, req.type, req.description)

        return VehicleTypeResponse(
            id=str(row["id"]),
            type=row["type"],
            description=row["description"],
            created_at=row["created_at"].isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"post_vehicle_type: {e}")

async def delete_vehicle_type(type: str) -> bool:
    try:
        exists = await db.fetch_one(
            "SELECT id FROM vehicle_types WHERE type = $1",
            type
        )

        if not exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle type not found"
            )

        await db.execute(
            "DELETE FROM vehicle_types WHERE type = $1",
            type
        )

        return True

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"delete_vehicle_type: {e}")

async def get_vehicle_features() -> List[VehicleFeatureResponse]:
    try:
        query = """
            SELECT id, feature, description, created_at
            FROM vehicle_features
            ORDER BY created_at DESC
        """

        rows = await db.fetch_all(query)

        return [
            VehicleFeatureResponse(
                id=str(r["id"]),
                feature=r["feature"],
                description=r["description"],
                created_at=r["created_at"].isoformat()
            )
            for r in rows
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"get_vehicle_features: {e}")

async def post_vehicle_feature(req: VehicleFeatureRequest) -> VehicleFeatureResponse:
    try:
        exists = await db.fetch_one(
            "SELECT id FROM vehicle_features WHERE feature = $1",
            req.feature
        )

        if exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vehicle feature already exists"
            )

        query = """
            INSERT INTO vehicle_features (feature, description)
            VALUES ($1, $2)
            RETURNING id, feature, description, created_at
        """

        row = await db.fetch_one(query, req.feature, req.description)

        return VehicleFeatureResponse(
            id=str(row["id"]),
            feature=row["feature"],
            description=row["description"],
            created_at=row["created_at"].isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"post_vehicle_feature: {e}")

async def delete_vehicle_feature(feature: str) -> bool:
    try:
        exists = await db.fetch_one(
            "SELECT id FROM vehicle_features WHERE feature = $1",
            feature
        )

        if not exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle feature not found"
            )

        await db.execute(
            "DELETE FROM vehicle_features WHERE feature = $1",
            feature
        )

        return True

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"delete_vehicle_feature: {e}")
