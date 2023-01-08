from typing import Optional
import requests
import json


class RestAPI:
    def __init__(self):
        self.base_url = ""
        self.endpoints = {}

    def fetch_response(
        self,
        endpoint: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
    ):
        return requests.get(
            self.base_url + self.endpoints[endpoint],
            headers=headers,
            params=params,
            verify=False,
        )

    def fetch_status_code(
        self,
        endpoint: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
    ):
        return self.fetch_response(endpoint, headers=headers, params=params).status_code

    def fetch_response_text(
        self,
        endpoint: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
    ):
        return self.fetch_response(endpoint, headers=headers, params=params).text

    def fetch_response_json(
        self,
        endpoint: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
    ):
        return json.loads(
            self.fetch_response(endpoint, headers=headers, params=params).text
        )
