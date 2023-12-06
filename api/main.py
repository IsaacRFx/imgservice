from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from flask_cors import CORS
from decouple import config
import boto3
import psycopg2
import uuid

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
socket = SocketIO(app, cors_allowed_origins="*")

def get_db_connection():
    conn = psycopg2.connect(
        host=config("SQL_HOST"),
        database=config("SQL_DATABASE"),
        user=config("SQL_USER"),
        password=config("SQL_PASSWORD"),
    )
    return conn

def generate_file_name(filename):
    return uuid.uuid4().hex + "." + filename.split(".")[-1]

@app.route("/api/files/", methods=["POST"])
def upload_image():
    try:
        file = request.files["imageFile"]
        socketId = request.form.get("socketId")
        filename = file.filename
        filename = generate_file_name(filename)
        s3 = boto3.client("s3")
        s3.upload_fileobj(
            file,
            config("S3_BUCKET_NAME"),
            filename,
            ExtraArgs={
                "ACL": "public-read",
                "ContentType": file.content_type,
                "Metadata": {"socketId": socketId, "modified": "0"},
            },
        )
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            f"INSERT INTO ImageFiles (filename, socketId) VALUES ('{filename}', '{socketId}')"
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Image has been uploaded successfully"})
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"})

@app.route("/api/files/webhook/", methods=["POST"])
def webhook_notify_upload():
    object_key = request.json["object_key"]
    s3_resource = boto3.client("s3")
    bucket = config("S3_BUCKET_NAME")
    response = s3_resource.get_object(Bucket=bucket, Key=object_key)
    ResponseMetadata = response["ResponseMetadata"]
    url = f"https://{bucket}.s3.amazonaws.com/{object_key}"
    conn = get_db_connection()
    cur = conn.cursor()
    parsed_object_key=object_key.split('-')[0]
    cur.execute(f"UPDATE ImageFiles SET url = '{url}' WHERE filename LIKE '{parsed_object_key}%'")
    conn.commit()
    cur.close()
    conn.close()
    socketId = ResponseMetadata.get("HTTPHeaders").get("x-amz-meta-socketid")
    socket.emit(
        "image_uploaded",
        {"object_key": object_key, "message": "Image has been uploaded successfully", "url":url},
        to=socketId,
    )
    return jsonify({"message": "Socket message sent"})

if __name__ == "__main__":
    socket.run(app, host="0.0.0.0", port=5001, debug=True, allow_unsafe_werkzeug=True)