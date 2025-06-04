import gc
import mimetypes
import uuid
from contextlib import asynccontextmanager

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import Response

from app.api import deps
from app.crud.redis import RedisCacheService
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

def get_redis_service() -> RedisCacheService:
    """Redisキャッシュサービスを取得"""
    try:
        return RedisCacheService()
    except ValueError:
        raise HTTPException(
            status_code=500, detail="Failed to initialize Redis cache service. Please check configuration."
        )
    
@asynccontextmanager
async def managed_image_download(storage: StorageService, file_path: str):
    """メモリ管理付き画像ダウンロード"""
    contents = None
    try:
        contents = await storage.download_file(file_path)
        yield contents
    finally:
        # 明示的なメモリクリーンアップ
        if contents:
            del contents
            # 必要に応じてガベージコレクション
            if gc.get_count()[0] > 700:
                gc.collect()

# 画像をフロントエンドに表示するためのプロキシーエンドポイント
@router.get("/images/{file_path:path}")
async def get_image(
    file_path: str,
    use_cache: bool = Query(True, description="Redisキャッシュを使用するか"),
    storage: StorageService = Depends(get_file_service),
    cache_service: RedisCacheService = Depends(get_redis_service),
    # current_user = Depends(deps.get_current_user)
):
    """メモリ最適化された画像取得（Redisキャッシュ対応）"""
    try:
        # キャッシュから取得を試行
        if use_cache:
            cached_result = await cache_service.get_cached_image(file_path)
            print(f"Cache lookup for {file_path}: {cached_result is not None}")
            if cached_result:
                image_data, content_type = cached_result
                return Response(
                    content=image_data,
                    media_type=content_type,
                    headers={
                        "X-Cache": "HIT",
                        "Cache-Control": "public, max-age=3600"
                    }
                )
        
        # キャッシュにない場合はストレージから取得（メモリ管理付き）
        async with managed_image_download(storage, file_path) as contents:
            if not contents:
                raise HTTPException(status_code=404, detail="画像が見つかりません")

            # MIMEタイプの推測を改善
            content_type, _ = mimetypes.guess_type(file_path)
            if not content_type or not content_type.startswith('image/'):
                # ファイル拡張子による判定
                if file_path.lower().endswith(('.jpg', '.jpeg')):
                    content_type = "image/jpeg"
                elif file_path.lower().endswith('.png'):
                    content_type = "image/png"
                elif file_path.lower().endswith('.gif'):
                    content_type = "image/gif"
                elif file_path.lower().endswith('.webp'):
                    content_type = "image/webp"
                else:
                    content_type = "image/jpeg"  # デフォルト
            
            # 小さい画像のみキャッシュに保存
            if use_cache and len(contents) <= 1024 * 1024 * 5:  # 5MB以下
                print(f"Caching image {file_path} of size {len(contents)} bytes")
                await cache_service.cache_image(file_path, contents, content_type)

            # レスポンスデータをコピー（元のcontentsは解放される）
            response_data = bytes(contents)
            
            return Response(
                content=response_data,
                media_type=content_type,
                headers={
                    "X-Cache": "MISS",
                    "Cache-Control": "public, max-age=3600",
                    "Content-Length": str(len(response_data))
                }
            )
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="画像が見つかりません")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"画像取得エラー: {str(e)}")

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