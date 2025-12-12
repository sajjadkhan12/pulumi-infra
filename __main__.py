import pulumi
import pulumi_gcp as gcp

# Get configuration values
config = pulumi.Config()
bucket_name = config.require("bucket_name")
location = config.get("location") or "US"
storage_class = config.get("storage_class") or "STANDARD"
uniform_bucket_level_access = config.get_bool("uniform_bucket_level_access") or True

# Create GCP Storage Bucket
bucket = gcp.storage.Bucket(
    "bucket",
    name=bucket_name,
    location=location,
    storage_class=storage_class,
    uniform_bucket_level_access=uniform_bucket_level_access,
)

# Export bucket name and URL
pulumi.export("bucket_name", bucket.name)
pulumi.export("bucket_url", bucket.url)