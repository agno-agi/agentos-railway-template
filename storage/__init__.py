"""
Storage Module
==============

S3-compatible object storage for Railway Buckets.
"""

from storage.client import bucket_name, get_s3_client, is_authenticated, is_configured
from storage.tools import S3Tools, VIRTUAL_BUCKETS

__all__ = [
    "bucket_name",
    "get_s3_client",
    "is_authenticated",
    "is_configured",
    "S3Tools",
    "VIRTUAL_BUCKETS",
]
