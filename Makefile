packages:
	pip install -r api/requirements.txt

build_test:
	docker build -t local-testing:latest .

build:
	docker build -t msc-onlab-backend:latest .

venv:
	# Start virtual environment
	. api/.venv/bin/activate

test: venv
	pytest

up:
	# Start virtual environment
	. api/.venv/bin/activate

	# Export all needed variables
	export FLASK_ENV="development"
	export MONGODB_CONNECTION_URL="mongodb://localhost:27017"
	export MONGODB_DATABASE_NAME="msc_onlab"
	export MONGODB_COLLECTION_USERS="users"
	export MONGODB_COLLECTION_HOUSEHOLDS="households"
	export TOKEN_SECRET_KEY="boti_kerge_lesz"
	export APP_FOLDER_PATH="api/app"

	# Run application
	python3 api/app.py

dup:
	# Run container
	docker run -d \
		-p 5000:5000 \
		--name msc_onlab \
		-e FLASK_ENV="development" \
		-e MONGODB_CONNECTION_URL="mongodb://192.168.1.68:27017" \
		local-testing

ddown:
	docker stop msc_onlab && docker rm msc_onlab
