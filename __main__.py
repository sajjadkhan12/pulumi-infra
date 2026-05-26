"""An AWS S3 Bucket Pulumi program"""

import pulumi
from pulumi_aws import s3
import json

# Read inputs from Pulumi config
config = pulumi.Config()

# Required fields
bucket_name = config.require("bucket_name")
region = config.require("region")

# Optional fields with defaults
versioning_enabled = config.get_bool("versioning_enabled") or False
encryption = config.get("encryption") or "AES256"
kms_key_id = config.get("kms_key_id")

# Public access block settings
block_public_acls = config.get_bool("block_public_acls")
if block_public_acls is None:
    block_public_acls = True

block_public_policy = config.get_bool("block_public_policy")
if block_public_policy is None:
    block_public_policy = True

ignore_public_acls = config.get_bool("ignore_public_acls")
if ignore_public_acls is None:
    ignore_public_acls = True

restrict_public_buckets = config.get_bool("restrict_public_buckets")
if restrict_public_buckets is None:
    restrict_public_buckets = True

# Lifecycle rules
enable_lifecycle_rules = config.get_bool("enable_lifecycle_rules") or False
# Optional integer values - get_int returns None if not set or invalid
transition_to_ia_days = config.get_int("transition_to_ia_days")
transition_to_glacier_days = config.get_int("transition_to_glacier_days")
expiration_days = config.get_int("expiration_days")

# CORS configuration
enable_cors = config.get_bool("enable_cors") or False
cors_allowed_origins = config.get("cors_allowed_origins") or "*"
cors_allowed_methods = config.get("cors_allowed_methods") or "GET,PUT,POST,DELETE,HEAD"
cors_allowed_headers = config.get("cors_allowed_headers") or "*"
# Optional integer with default
cors_max_age_seconds = config.get_int("cors_max_age_seconds") or 3000

# Website hosting
enable_website_hosting = config.get_bool("enable_website_hosting") or False
index_document = config.get("index_document") or "index.html"
error_document = config.get("error_document") or "error.html"

# Logging
enable_logging = config.get_bool("enable_logging") or False
target_bucket_for_logging = config.get("target_bucket_for_logging")
log_prefix = config.get("log_prefix") or "logs/"

# Tags
tags_str = config.get("tags") or "{}"
try:
    tags_dict = json.loads(tags_str)
    if not isinstance(tags_dict, dict):
        tags_dict = {}
except (json.JSONDecodeError, TypeError):
    tags_dict = {}

# Add default tags
tags_dict.update({
    "ManagedBy": "nexus-idp",
    "Environment": pulumi.get_stack()
})

# Force destroy
force_destroy = config.get_bool("force_destroy") or False

# Build server-side encryption configuration
# Will be used directly in BucketServerSideEncryptionConfiguration

# Build lifecycle rules
lifecycle_rules = []
if enable_lifecycle_rules:
    rule = {}
    transitions = []
    
    if transition_to_ia_days:
        transitions.append({
            "days": transition_to_ia_days,
            "storage_class": "STANDARD_IA"
        })
    
    if transition_to_glacier_days:
        transitions.append({
            "days": transition_to_glacier_days,
            "storage_class": "GLACIER"
        })
    
    if transitions:
        rule["transitions"] = transitions
    
    if expiration_days:
        rule["expiration"] = {
            "days": expiration_days
        }
    
    if rule:
        rule["enabled"] = True
        rule["id"] = "lifecycle-rule"
        lifecycle_rules.append(rule)

# Build CORS configuration
cors_rules = []
if enable_cors:
    cors_rules.append({
        "allowed_origins": [origin.strip() for origin in cors_allowed_origins.split(",")],
        "allowed_methods": [method.strip() for method in cors_allowed_methods.split(",")],
        "allowed_headers": [header.strip() for header in cors_allowed_headers.split(",")],
        "max_age_seconds": cors_max_age_seconds
    })

# Build website configuration
website_configuration = None
if enable_website_hosting:
    website_configuration = {
        "index_document": index_document,
        "error_document": error_document
    }

# Build logging configuration
logging_configuration = None
if enable_logging and target_bucket_for_logging:
    logging_configuration = {
        "target_bucket": target_bucket_for_logging,
        "target_prefix": log_prefix
    }

# Create the S3 Bucket
bucket = s3.Bucket(
    "bucket",
    bucket=bucket_name,
    force_destroy=force_destroy,
    tags=tags_dict
)

# Configure versioning
if versioning_enabled:
    s3.BucketVersioning(
        "bucket-versioning",
        bucket=bucket.id,
        versioning_configuration={
            "status": "Enabled"
        }
    )

# Configure server-side encryption
if encryption:
    # Build the encryption rule as a dictionary
    sse_default = {
        "sse_algorithm": encryption
    }
    
    # Add KMS key ID if using KMS encryption
    if encryption.startswith("aws:kms") and kms_key_id:
        sse_default["kms_master_key_id"] = kms_key_id
    
    # Pulumi AWS v6+ uses 'rules' as a list parameter
    s3.BucketServerSideEncryptionConfiguration(
        "bucket-encryption",
        bucket=bucket.id,
        rules=[{
            "apply_server_side_encryption_by_default": sse_default
        }]
    )

# Configure public access block
s3.BucketPublicAccessBlock(
    "bucket-public-access-block",
    bucket=bucket.id,
    block_public_acls=block_public_acls,
    block_public_policy=block_public_policy,
    ignore_public_acls=ignore_public_acls,
    restrict_public_buckets=restrict_public_buckets
)

# Configure lifecycle rules
if lifecycle_rules:
    s3.BucketLifecycleConfiguration(
        "bucket-lifecycle",
        bucket=bucket.id,
        rules=lifecycle_rules
    )

# Configure CORS
if cors_rules:
    s3.BucketCorsConfiguration(
        "bucket-cors",
        bucket=bucket.id,
        cors_rules=cors_rules
    )

# Configure website hosting
if website_configuration:
    s3.BucketWebsiteConfiguration(
        "bucket-website",
        bucket=bucket.id,
        index_document={
            "suffix": website_configuration["index_document"]
        },
        error_document={
            "key": website_configuration["error_document"]
        }
    )

# Configure logging
if logging_configuration:
    s3.BucketLogging(
        "bucket-logging",
        bucket=bucket.id,
        target_bucket=logging_configuration["target_bucket"],
        target_prefix=logging_configuration["target_prefix"]
    )

# Export outputs
pulumi.export("bucket_name", bucket.id)
pulumi.export("bucket_arn", bucket.arn)
pulumi.export("bucket_domain_name", bucket.bucket_domain_name)
pulumi.export("bucket_regional_domain_name", bucket.bucket_regional_domain_name)

# Export website endpoints if enabled
if enable_website_hosting:
    pulumi.export("website_endpoint", bucket.website_endpoint)
    pulumi.export("website_domain", bucket.website_domain)

