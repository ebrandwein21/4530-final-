import json
import os
from datetime import datetime, timezone

import boto3

s3 = boto3.client("s3")
INPUT_BUCKET = os.environ.get("INPUT_BUCKET")


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
    # Handle CORS preflight if API Gateway forwards OPTIONS here
    if event.get("httpMethod") == "OPTIONS":
        return _response(200, {"message": "CORS ok"})

    if INPUT_BUCKET is None:
        return _response(500, {"error": "INPUT_BUCKET env var not set"})

    try:
        body_str = event.get("body") or "{}"
        body = json.loads(body_str)
    except json.JSONDecodeError:
        return _response(400, {"error": "Invalid JSON body"})

    role = (body.get("role") or "").strip().lower()
    subject_id = (body.get("subjectId") or "").strip()
    range_sel = (body.get("range") or "").strip()
    note = body.get("note") or ""

    if not role or not subject_id:
        return _response(
          400,
          {"error": "role and subjectId are required", "received": body}
        )

    now = datetime.now(timezone.utc).isoformat()
    key = f"inputs/{role}/{subject_id}/{now}.json"

    obj = {
        "role": role,
        "subjectId": subject_id,
        "range": range_sel,
        "note": note,
        "timestamp": now,
    }

    try:
        s3.put_object(
            Bucket=INPUT_BUCKET,
            Key=key,
            Body=json.dumps(obj).encode("utf-8"),
            ContentType="application/json",
        )
    except Exception as e:
        return _response(500, {"error": f"Failed to write to S3: {e}"})

    return _response(
        200,
        {
            "message": "Inputs stored",
            "s3Bucket": INPUT_BUCKET,
            "s3Key": key,
            "data": obj,
        },
    )
