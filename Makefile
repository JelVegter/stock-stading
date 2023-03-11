pre-commit:
	terraform fmt

plan-dev:
	terraform plan \
		-var-file=dev.tfvars -out=terraform.out

apply-dev:
	terraform apply terraform.out

plan-apply-dev:
	make init-dev
	make plan-dev
	make apply-dev
