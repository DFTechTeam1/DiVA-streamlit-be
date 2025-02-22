from datetime import datetime
from utils.helper import CustomHelper
from sqlmodel import SQLModel, Field
from services.postgres.connection import database_connection

helper = CustomHelper()


class ClientPreview(SQLModel, table=True):
    __tablename__ = "client_preview"
    id: int = Field(primary_key=True)
    created_at: datetime = Field(default=helper.local_time())
    updated_at: datetime = Field(default=None, nullable=True)
    filepath: str = Field(default=None)
    filename: str = Field(default=None)
    nature: bool = Field(default=False)
    artifacts: bool = Field(default=False)
    living_beings: bool = Field(default=False)
    conceptual: bool = Field(default=False)
    art_deco: bool = Field(default=False)
    architectural: bool = Field(default=False)
    artistic: bool = Field(default=False)
    sci_fi: bool = Field(default=False)
    fantasy: bool = Field(default=False)
    afternoon: bool = Field(default=False)
    sunset_sunrise: bool = Field(default=False)
    night: bool = Field(default=False)
    warm: bool = Field(default=False)
    cool: bool = Field(default=False)
    neutral: bool = Field(default=False)
    gold: bool = Field(default=False)
    is_validated: bool = Field(default=False)
    is_trained: bool = Field(default=False)
    ip_address: str = Field(default=None)


async def database_migration():
    engine = database_connection()
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
