# AWS S3 Bucket Plugin

This plugin provisions an AWS S3 bucket with comprehensive configuration options.

## Features

- **Bucket Configuration**: Globally unique bucket name, region selection
- **Versioning**: Enable object versioning for data protection
- **Encryption**: Support for AES256, AWS KMS, and DSSE-KMS encryption
- **Public Access Control**: Comprehensive public access block settings
- **Lifecycle Management**: Automatic transitions to IA/Glacier and object expiration
- **CORS Configuration**: Cross-origin resource sharing setup
- **Static Website Hosting**: Configure bucket for website hosting
- **Access Logging**: Server access logging configuration
- **Tags**: Custom tags for resource management

## Required Fields

- `bucket_name`: Globally unique bucket name (3-63 characters)
- `region`: AWS region where bucket will be created

## Optional Fields

All other fields have sensible defaults and can be configured based on your requirements.

## Usage

1. Zip this directory: `zip -r aws-s3-bucket.zip .`
2. Upload via the IDP plugin management interface
3. Configure the bucket using the form fields
4. Provision the bucket

## Requirements

- AWS credentials configured (via IDP credentials management)
- Appropriate IAM permissions for S3 bucket creation

## Icon

Replace `assets/icon.png` with an AWS S3 icon (PNG format, recommended 128x128 or 256x256 pixels).

