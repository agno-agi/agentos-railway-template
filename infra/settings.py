from pathlib import Path

from agno.infra.settings import InfraSettings

#
# Infrastructure settings for Railway deployment.
# These values can also be overridden using environment variables.
# Import them into your project using `from infra.settings import infra_settings`
#
infra_settings = InfraSettings(
    infra_name="agentos-railway",
    infra_root=Path(__file__).parent.parent.resolve(),
    # S3 Storage
    # Default: Agno's public sample bucket (works without credentials)
    # To use your own bucket:
    #   1. Create a bucket in Railway Dashboard (or any S3-compatible provider)
    #   2. Set the values below
    s3_bucket="agno-scout-public",
    s3_region="us-east-1",
)
