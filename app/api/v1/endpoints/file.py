import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import Response

from app.api import deps
from app.crud.s3 import StorageService

router = APIRouter()

def get_file_service() -> StorageService:
    """Fileサービスを取得"""
    try:
        return StorageService()
    except ValueError:
        raise HTTPException(
            status_code=500, detail="Failed to initialize TASUKI service. Please check API key configuration."
        )

@router.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    folder: str = Query("uploads", description="Storage folder"),
    storage: StorageService = Depends(get_file_service),
    current_user = Depends(deps.get_current_user)
):
    """ファイルをアップロードする"""
    try:
        # ユニークなファイル名を生成
        file_ext = file.filename.split(".")[-1] if "." in file.filename else ""
        unique_filename = f"{uuid.uuid4()}.{file_ext}" if file_ext else str(uuid.uuid4())
        
        # ストレージパスを構築
        file_path = f"{folder}/{unique_filename}"
        
        # ファイルをアップロード
        url = await storage.upload_file(file, file_path)
        
        return {
            "filename": unique_filename,
            "original_filename": file.filename,
            "content_type": file.content_type,
            "path": file_path,
            "url": url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ファイルアップロードエラー: {str(e)}")

@router.get("")
async def list_files(
    prefix: str = Query("", description="検索するプレフィックス"),
    storage: StorageService = Depends(get_file_service),
    current_user = Depends(deps.get_current_user)
):
    """指定したプレフィックスのファイル一覧を取得する"""
    try:
        files = await storage.list_files(prefix)
        return {"files": files, "count": len(files)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ファイル一覧取得エラー: {str(e)}")

@router.get("/download/{file_path:path}")
async def download_file(
    file_path: str,
    storage: StorageService = Depends(get_file_service),
    current_user = Depends(deps.get_current_user)
):
    """ファイルをダウンロードする"""
    try:
        contents = await storage.download_file(file_path)
        
        # ファイルタイプの推測（実際のプロジェクトではより堅牢な方法を検討）
        content_type = "application/octet-stream"
        if file_path.endswith(".pdf"):
            content_type = "application/pdf"
        elif file_path.endswith((".jpg", ".jpeg")):
            content_type = "image/jpeg"
        elif file_path.endswith(".png"):
            content_type = "image/png"
        
        return Response(
            content=contents,
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={file_path.split('/')[-1]}"
            }
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="ファイルが見つかりません")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ファイルダウンロードエラー: {str(e)}")

@router.delete("/{file_path:path}")
async def delete_file(
    file_path: str,
    storage: StorageService = Depends(get_file_service),
    current_user = Depends(deps.get_current_user)
):
    """ファイルを削除する"""
    try:
        success = await storage.delete_file(file_path)
        if not success:
            raise HTTPException(status_code=404, detail="ファイルの削除に失敗しました")
        return {"status": "success", "message": "ファイルを削除しました"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ファイル削除エラー: {str(e)}")

@router.get("/presigned/{file_path:path}")
async def get_presigned_url(
    file_path: str,
    expiration: int = Query(3600, description="URL有効期限（秒）"),
    storage: StorageService = Depends(get_file_service),
    current_user = Depends(deps.get_current_user)
):
    """署名付きURLを生成する"""
    try:
        url = await storage.generate_presigned_url(file_path, expiration)
        return {"url": url, "expires_in": expiration}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"署名付きURL生成エラー: {str(e)}")