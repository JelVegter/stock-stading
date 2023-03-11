pre-commit:
	terraform fmt

init:
	cd terraform && terraform init
	
plan:
	cd terraform && terraform plan \
		-var-file=dev.tfvars -out=terraform.out

apply:
	cd terraform && terraform apply terraform.out

plan-apply:
	make init
	make plan
	make apply
