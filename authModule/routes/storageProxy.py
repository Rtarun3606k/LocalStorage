import requests
from flask import Blueprint, request, Response
from utils.tokenManagement import validate_service_ticket

storageProxy_bp = Blueprint("storageProxy", __name__)

GO_STORAGE_BASE = "http://localhost:8080"
SERVICE_NAME = "storage"


@storageProxy_bp.route("/upload", methods=["POST"])
def proxy_upload():
    ticket = request.headers.get("X-Service-Ticket")
    if not validate_service_ticket(ticket, SERVICE_NAME):
        return {"error": "Unauthorized"}, 401

    resp = requests.post(
        f"{GO_STORAGE_BASE}/api/v1/video/upload",
        files=request.files
    )

    return Response(resp.content, resp.status_code)


@storageProxy_bp.route("/video/<video_id>/index.m3u8")
def proxy_stream(video_id):
    ticket = request.headers.get("X-Service-Ticket")
    if not validate_service_ticket(ticket, SERVICE_NAME):
        return {"error": "Unauthorized"}, 401

    resp = requests.get(
        f"{GO_STORAGE_BASE}/api/v1/video/{video_id}/index.m3u8",
        stream=True
    )

    return Response(
        resp.iter_content(chunk_size=8192),
        content_type="application/vnd.apple.mpegurl"
    )


@storageProxy_bp.route("/image/<image_id>")
def proxy_image(image_id):
    ticket = request.headers.get("X-Service-Ticket")
    if not validate_service_ticket(ticket, SERVICE_NAME):
        return {"error": "Unauthorized"}, 401

    resp = requests.get(
        f"{GO_STORAGE_BASE}/api/v1/image/{image_id}",
        stream=True
    )

    return Response(resp.content, resp.status_code)
