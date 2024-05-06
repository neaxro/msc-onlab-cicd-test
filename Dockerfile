FROM python:bullseye

ENV MONGODB_CONNECTION_URL="mongodb://localhost:27017"
ENV MONGODB_DATABASE_NAME="msc_onlab"
ENV MONGODB_COLLECTION_USERS="users"
ENV MONGODB_COLLECTION_HOUSEHOLDS="households"
ENV TOKEN_SECRET_KEY="boti_kerge_lesz"
ENV APP_FOLDER_PATH=/api/app

EXPOSE 5000

WORKDIR /api

COPY api/ .

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT [ "python" ]

CMD ["app.py" ]