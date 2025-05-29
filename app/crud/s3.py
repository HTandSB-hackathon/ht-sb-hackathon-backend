from typing import Any, Dict, List, Optional

import aioboto3
from botocore.exceptions import ClientError
from fastapi import UploadFile

from app.core.config import settings


class StorageService:
    """S3/MinIO互換のストレージサービス
    
    開発環境ではMinIO、本番環境ではAWS S3を利用するためのサービス。
    aioboto3を使用して非同期処理に対応しています。
    """
    
    def __init__(self):
        self.session = aioboto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.S3_REGION
        )
        self.bucket_name = settings.STORAGE_BUCKET_NAME
        self.endpoint_url =  None if settings.ENVIRONMENT == "production" else settings.S3_ENDPOINT_URL
    
    async def upload_file(self, 
                         file: UploadFile, 
                         path: str, 
                         content_type: Optional[str] = None) -> str:
        """ファイルをアップロードし、URLを返す
        
        Args:
            file: アップロードされるファイル
            path: 保存先のパス (例: "users/avatars/user123.jpg")
            content_type: ファイルのMIMEタイプ (Noneの場合はファイルから自動判定)
            
        Returns:
            str: アップロードされたファイルのURL
        """
        async with self.session.client('s3', endpoint_url=self.endpoint_url) as s3:
            content_type = content_type or file.content_type
            contents = await file.read()
            
            # S3にアップロード
            await s3.put_object(
                Bucket=self.bucket_name,
                Key=path,
                Body=contents,
                ContentType=content_type
            )
            
            # ファイルのURLを生成
            if self.endpoint_url:
                # MinIOの場合
                url = f"{self.endpoint_url}/{self.bucket_name}/{path}"
            else:
                # AWS S3の場合
                url = f"https://{self.bucket_name}.s3.amazonaws.com/{path}"
                
            return url
    
    async def download_file(self, path: str) -> bytes:
        """ファイルをダウンロードする
        
        Args:
            path: ファイルのパス
            
        Returns:
            bytes: ファイルの内容
            
        Raises:
            ClientError: ファイルが見つからない、またはアクセスできない場合
        """
        async with self.session.client('s3', endpoint_url=self.endpoint_url) as s3:
            try:
                response = await s3.get_object(Bucket=self.bucket_name, Key=path)
                async with response['Body'] as stream:
                    return await stream.read()
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code')
                if error_code == 'NoSuchKey':
                    raise FileNotFoundError(f"File not found: {path}")
                raise
    
    async def delete_file(self, path: str) -> bool:
        """ファイルを削除する
        
        Args:
            path: 削除するファイルのパス
            
        Returns:
            bool: 削除が成功したかどうか
        """
        try:
            async with self.session.client('s3', endpoint_url=self.endpoint_url) as s3:
                await s3.delete_object(Bucket=self.bucket_name, Key=path)
                return True
        except Exception as e:
            print(f"File deletion error: {e}")
            return False
    
    async def list_files(self, prefix: str = "") -> List[Dict[str, Any]]:
        """指定したプレフィックス以下のファイル一覧を取得
        
        Args:
            prefix: 検索するプレフィックス (例: "users/avatars/")
            
        Returns:
            List[Dict[str, Any]]: ファイル情報のリスト
        """
        async with self.session.client('s3', endpoint_url=self.endpoint_url) as s3:
            response = await s3.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
            if 'Contents' not in response:
                return []
                
            result = []
            for item in response["Contents"]:
                if self.endpoint_url:
                    # MinIOの場合
                    url = f"{self.endpoint_url}/{self.bucket_name}/{item['Key']}"
                else:
                    # AWS S3の場合
                    url = f"https://{self.bucket_name}.s3.amazonaws.com/{item['Key']}"
                    
                result.append({
                    "key": item["Key"],
                    "size": item["Size"],
                    "last_modified": item["LastModified"],
                    "url": url
                })
            return result
            
    async def generate_presigned_url(self, path: str, expiration: int = 3600) -> str:
        """署名付きURLを生成する
        
        Args:
            path: ファイルのパス
            expiration: URL有効期限（秒）
            
        Returns:
            str: 署名付きURL
        """
        async with self.session.client('s3', endpoint_url=self.endpoint_url) as s3:
            try:
                url = await s3.generate_presigned_url(
                    ClientMethod='get_object',
                    Params={
                        'Bucket': self.bucket_name,
                        'Key': path
                    },
                    ExpiresIn=expiration
                )
                return url
            except Exception as e:
                print(f"Failed to generate presigned URL: {e}")
                raise