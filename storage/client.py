"""
Storage Client
==============

S3 client for Railway Buckets (Tigris) or any S3-compatible storage.

Priority: env vars > infra/settings.py defaults

Env vars are set automatically when a Railway Bucket is linked to a service,
or can be set manually for any S3-compatible provider.
"""

from os import getenv

import boto3
from botocore import UNSIGNED
from botocore.config import Config

from infra.settings import infra_settings

# Resolve config: env vars override infra_settings defaults
bucket_name: str = getenv("S3_BUCKET", getenv("BUCKET", infra_settings.s3_bucket or ""))
_region: str = getenv("S3_REGION", getenv("REGION", infra_settings.s3_region or ""))
_endpoint: str = getenv("S3_ENDPOINT", getenv("ENDPOINT", infra_settings.s3_endpoint or ""))
_access_key_id: str = getenv("S3_ACCESS_KEY_ID", getenv("ACCESS_KEY_ID", infra_settings.s3_access_key_id or ""))
_secret_access_key: str = getenv("S3_SECRET_ACCESS_KEY", getenv("SECRET_ACCESS_KEY", infra_settings.s3_secret_access_key or ""))

is_configured: bool = bool(bucket_name)
is_authenticated: bool = bool(_access_key_id and _secret_access_key)


def get_s3_client():
    """Create a boto3 S3 client.

    If credentials are present, creates an authenticated client (Railway Bucket, AWS, etc.).
    If no credentials, creates an anonymous client for public bucket access.
    """
    kwargs: dict = {"region_name": _region}

    if is_authenticated:
        kwargs["aws_access_key_id"] = _access_key_id
        kwargs["aws_secret_access_key"] = _secret_access_key
        kwargs["config"] = Config(s3={"addressing_style": "virtual"})
    else:
        kwargs["config"] = Config(signature_version=UNSIGNED)

    if _endpoint:
        kwargs["endpoint_url"] = _endpoint

    return boto3.client("s3", **kwargs)
