from ninja import Schema
from datetime import datetime, date

class VersionSchema(Schema):
    id: int
    name: str
    detail: str
    app_name: str
    slug: str
    release_date: date
    is_published: bool
    created: datetime
    updated: datetime

class VersionIn(Schema):
    name: str
    detail: str
    app_name: str
    # release_date: 