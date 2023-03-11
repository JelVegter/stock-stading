# Setup
This project uses Poetry for dependency management. To install Poetry, follow the instructions [here](https://python-poetry.org/docs/#installation).

To install the project dependencies, run the following command:
```
poetry install
```
To run scripts in the project, run the following command:
```
poetry run python <script_name>
```
To add a new dependency, run the following command:
```
poetry add <package_name>
```

# Infrastructure
The infrastructure for this project is handled by Terraform. To install Terraform, follow the instructions [here](https://learn.hashicorp.com/tutorials/terraform/install-cli).

The Terraform backend is configured to use an S3 bucket. To create the S3 bucket, ensure the following environment variables are available and run the create_s3_backend.py script:
```
export AWS_ACCESS_KEY_ID=<your_aws_access_key_id>
export AWS_SECRET_ACCESS_KEY=<your_aws_secret_access_key>
poetry run python terraform/create_s3_backend.py
```

To initialize Terraform, change into the terraform/ directory and run the following command:

```
cd terraform/
terraform init
```
