import sys
from typing import Optional
from datetime import datetime
from pathlib import Path
from sqlmodel import SQLModel, Field, Relationship

sys.path.append(str(Path(__file__).resolve().parents[2]))
from utils.helper import local_time
from services.postgre.connection import database_connection


class ImageMetadata(SQLModel, table=True):
    __tablename__ = 'image_metadata'
    id: Optional[int] = Field(primary_key=True)
    created_at: datetime = Field(default=local_time())
    filename: Optional[str] = Field(default=None)
    checksum: Optional[str] = Field(default=None)

    uploaded_img: list['UploadedImage'] = Relationship(back_populates='image_md5')


class UploadedImage(SQLModel, table=True):
    __tablename__ = 'uploaded_image'
    id: Optional[int] = Field(primary_key=True)
    created_at: datetime = Field(default=local_time())
    upload_id: Optional[int] = Field(default=None, foreign_key='image_metadata.id')
    checksum: Optional[str] = Field(default=None)
    threshold: Optional[float] = Field(default=None)
    total_page: Optional[int] = Field(default=None)
    is_image_saved: bool = Field(default=False)

    image_md5: Optional[ImageMetadata] = Relationship(back_populates='uploaded_img')


async def database_migration():
    engine = database_connection()
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
