# variable
PACKAGE_DIR := package
ZIP_FILE := lambda_function.zip
PYTHON_VERSION := python3.11
REQUIREMENTS_FILE := requirements.txt
LAMBDA_FUNCTION_FILE := lambda_function.py

all: package

package:
$(PACKAGE_DIR):
	mkdir -p $(PACKAGE_DIR)
	pip install -r $(REQUIREMENTS_FILE) -t $(PACKAGE_DIR)

$(ZIP_FILE): $(PACKAGE_DIR)
	cp $(LAMBDA_FUNCTION_FILE) $(PACKAGE_DIR)/
	cd $(PACKAGE_DIR) && zip -r ../$(ZIP_FILE) .
	rm -rf $(PACKAGE_DIR)  


build: $(ZIP_FILE)
	@echo "Package created: $(ZIP_FILE)"

clean:
	rm -rf $(PACKAGE_DIR) $(ZIP_FILE)

# deploy to aws: local test only
deploy: package
	aws lambda update-function-code --function-name YOUR_LAMBDA_FUNCTION_NAME --zip-file fileb://$(ZIP_FILE)

.PHONY: all package clean deploy
