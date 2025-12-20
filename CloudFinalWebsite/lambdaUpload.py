import json
import os
from datetime import datetime, timezone
import base64

import boto3

s3 = boto3.client("s3")
RAW_DATA_BUCKET = os.environ.get("RAW_DATA_BUCKET")


def _response(status_code: int, body_obj, cors: bool = True):
    headers = {"Content-Type": "application/json"}
    if cors:
        headers.update(
            {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST",
            }
        )
    return {
        "statusCode": status_code,
        "headers": headers,
        "body": json.dumps(body_obj),
    }


def handler(event, context):
    # Handle CORS preflight
    if event.get("httpMethod") == "OPTIONS":
        return _response(200, {"message": "CORS ok"})

    if RAW_DATA_BUCKET is None:
        return _response(500, {"error": "RAW_DATA_BUCKET env var not set"})

    # If you ever switch to binary mode, API Gateway may base64-encode the body
    is_base64 = event.get("isBase64Encoded", False)

    try:
        body_raw = event.get("body") or "{}"
        if is_base64:
            body_raw = base64.b64decode(body_raw).decode("utf-8")
        body = json.loads(body_raw)
    except json.JSONDecodeError:
        return _response(400, {"error": "Invalid JSON body"})

    subject_id = (body.get("subjectId") or "").strip()
    file_name = (body.get("fileName") or "").strip()
    content = body.get("content")

    if not subject_id or not file_name or content is None:
        return _response(
            400,
            {
                "error": "subjectId, fileName, and content are required",
                "received": {
                    "subjectId": subject_id,
                    "fileName": file_name,
                    "hasContent": content is not None,
                },
            },
        )

    now = datetime.now(timezone.utc).isoformat()
    key = f"raw-data/{subject_id}/{now}_{file_name}"

    try:
        s3.put_object(
            Bucket=RAW_DATA_BUCKET,
            Key=key,
            Body=content.encode("utf-8"),
            ContentType="text/csv",
        )
    except Exception as e:
        return _response(500, {"error": f"Failed to write to S3: {e}"})

    return _response(
        200,
        {
            "message": "File stored",
            "s3Bucket": RAW_DATA_BUCKET,
            "s3Key": key,
            "subjectId": subject_id,
            "fileName": file_name,
        },
    )
