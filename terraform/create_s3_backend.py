import boto3

BACKEND_BUCKET = "stocktrading-terraform-backend"
REGION = "eu-central-1"

s3_client = boto3.client("s3", region_name=REGION)
s3_client.create_bucket(
    Bucket="stocktrading-cicd-storage",
    CreateBucketConfiguration={"LocationConstraint": REGION},
)

buckets = s3_client.list_buckets()
buckets = [bucket["Name"] for bucket in buckets["Buckets"]]

if BACKEND_BUCKET in buckets:
    print(f"Bucket {BACKEND_BUCKET} created successfully")
