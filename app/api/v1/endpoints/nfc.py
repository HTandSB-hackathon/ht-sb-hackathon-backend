
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.crud.character import get_character_by_id, get_character_nfc_uuid_by_nfc_uuid
from app.crud.relationship import get_relationships_by_user_id_and_character_id, insert_relationship
from app.models.user import Users
from app.schemas.nfc import NfcRequest
from app.schemas.relationship import RelationshipResponse

router = APIRouter()


@router.post("/characters/nfc", response_model=RelationshipResponse)
async def read_character_relationship_by_nfc_uuid(
    inputs: NfcRequest,
    db: Session = Depends(deps.get_db),
    current_user: Users = Depends(deps.get_current_user),
) -> RelationshipResponse:
    """
    Get character relationship by NFC UUID.
    """
    character_nfc = await get_character_nfc_uuid_by_nfc_uuid(db, nfc_uuid=inputs.nfc_uuid)
    if not character_nfc:
        raise HTTPException(status_code=404, detail="NFC UUID not found")


    character = get_character_by_id(db, character_id=character_nfc.id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found for this NFC UUID")

    relationship = get_relationships_by_user_id_and_character_id(
        db, user_id=current_user.id, character_id=character.id
    )

    if not relationship:
        relationship = insert_relationship(db, 
            user_id=current_user.id,
            character_id=character.id
        )

    if not relationship:
        raise HTTPException(status_code=500, detail="Could not get or create relationship")

    return relationship
