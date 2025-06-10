from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/characters/nfc/{nfc_uuid}", response_model=schemas.RelationshipResponse)
async def read_character_relationship_by_nfc_uuid(
    *,
    db: Session = Depends(deps.get_db),
    nfc_uuid: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get character relationship by NFC UUID.
    """
    character_nfc = await crud.character.get_character_nfc_uuid_by_nfc_uuid_async(db, nfc_uuid=nfc_uuid)
    if not character_nfc:
        raise HTTPException(status_code=404, detail="NFC UUID not found")

    character = await crud.character.get_character_by_id_async(db, id=character_nfc.character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found for this NFC UUID")

    relationship = await crud.relationship.get_by_user_and_character(
        db, user_id=current_user.id, character_id=character.id
    )

    if not relationship:
        relationship_in = schemas.RelationshipCreate(
            user_id=current_user.id,
            character_id=character.id,
            trust_level_id = 1 # Default to trust level 1
        )
        relationship = await crud.relationship.create(db, obj_in=relationship_in)
        await db.refresh(relationship)


    if not relationship:
        raise HTTPException(status_code=500, detail="Could not get or create relationship")

    return relationship
