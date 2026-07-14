import requests

from .base import BaseExecutor


class HttpExecutor(BaseExecutor):

    def execute(self, mission):

        payload = mission.get("payload") or {}

        method = payload.get("method", "GET").upper()
        url = payload["url"]

        headers = payload.get("headers", {})
        params = payload.get("params")
        json_body = payload.get("json")
        data = payload.get("data")

        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json_body,
            data=data,
            timeout=60,
        )

        try:
            body = response.json()
        except Exception:
            body = response.text

        return {
            "success": response.ok,
            "status_code": response.status_code,
            "message": response.reason,
            "data": body,
        }
