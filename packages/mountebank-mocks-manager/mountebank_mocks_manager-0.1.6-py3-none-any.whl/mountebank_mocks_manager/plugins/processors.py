import base64
import gzip
import json
import re
import zlib
from copy import deepcopy
from datetime import datetime

import dpath
from dateutil.relativedelta import relativedelta


class CommonProcessor:
    @staticmethod
    def has_proxy_stub(imposter):
        for stub in imposter["stubs"]:
            for response in stub["responses"]:
                if "proxy" in response:
                    return True
        return False

    @staticmethod
    def remove_proxy_stubs(imposter):
        filtered_stubs = list()
        for stub in imposter["stubs"]:
            for response in stub["responses"]:
                if "proxy" not in response:
                    filtered_stubs.append(stub)
        return filtered_stubs

    @classmethod
    def get_recorded_imposters(cls, imposters):
        """Retrieve all stubs that were recorded by proxy imposters"""
        recorded_imposters = dict()
        for name, stubs in imposters.items():
            if cls.has_proxy_stub(stubs):
                recorded_imposters[name] = cls.remove_proxy_stubs(stubs)

        return recorded_imposters

    @staticmethod
    def as_json(body):
        """Try to convert body to json, return original body on error"""
        try:
            return json.loads(body)
        except (ValueError, TypeError):
            return body

    @staticmethod
    def deflate(body, codec):
        """Try to deflate body, return original body on error"""
        try:
            body_bytes = base64.urlsafe_b64decode(body)
            decompressed_body = zlib.decompress(body_bytes)
            return decompressed_body.decode(codec)
        except (TypeError, Exception):
            return body

    @staticmethod
    def decompress(body):
        """Try to decompress body, return original body on error"""
        try:
            body_bytes = base64.urlsafe_b64decode(body)
            decompressed_body = gzip.decompress(body_bytes)
            return decompressed_body.decode("utf-8")
        except (TypeError, Exception):
            return body

    @classmethod
    def decode_body(cls, body: str):
        body = cls.deflate(body, "utf-8")
        body = cls.deflate(body, "cp1252")
        body = cls.decompress(body)
        body = cls.as_json(body)
        return body

    @classmethod
    def process_predicates(cls, stub):
        """Process predicates in recorded mock definition in a more convenient way to use them
        in the future"""
        prepared_stub = deepcopy(stub)
        for predicate in prepared_stub["predicates"]:
            for key, value in predicate.items():
                if isinstance(value, dict) and "body" in value:
                    predicate[key]["body"] = cls.as_json(predicate[key]["body"])
        return prepared_stub

    @classmethod
    def process_responses(cls, stub):
        """Process responses in recorded mock definition in a more convenient way to use them
        in future"""
        prepared_stub = deepcopy(stub)
        for response in prepared_stub["responses"]:
            for key, value in response.items():
                if isinstance(value, dict):
                    if "body" in value:
                        response[key]["body"] = cls.decode_body(response[key]["body"])
        return prepared_stub

    @classmethod
    def process_imposter(cls, stubs):
        processed_stubs = list()

        for stub in stubs:
            processed_stub = deepcopy(stub)
            processed_stub.pop("_links")
            processed_stub = cls.process_predicates(processed_stub)
            processed_stub = cls.process_responses(processed_stub)
            processed_stubs.append(processed_stub)

        return processed_stubs

    @classmethod
    def process(cls, imposters):
        recorded_imposters = cls.get_recorded_imposters(imposters)
        for name, stubs in recorded_imposters.items():
            recorded_imposters[name] = cls.process_imposter(stubs)
        return recorded_imposters


class DatesProcessor:
    _MONTHS = [
        "JAN",
        "FEB",
        "MAR",
        "ARP",
        "MAY",
        "JUN",
        "JUL",
        "AUG",
        "SEP",
        "OCT",
        "NOV",
        "DEC",
    ]

    STR_PATCH_NAME = "MOCKS_PATCH_DATES_REPLACE"
    STR_PATCH_REPLACE = STR_PATCH_NAME + "({days},{fmt})"
    STR_PATCH_PATTERNS = [
        (re.compile(r"20[23]\d-[01]\d-[0123]\d"), "%Y-%m-%d"),
        (re.compile(r"[0-3]\d/[01]\d/20[23]\d"), "%d/%m/%Y"),
        (
            re.compile(rf'(\d\d({"|".join(_MONTHS)})\d\d)'),
            "%d%b%y",
        ),
    ]

    JSON_PATCH_NAME = "MOCKS_PATCH_DATES_JSON_REPLACE"
    JSON_PATCH_REPLACE = JSON_PATCH_NAME + "({days})"
    # match content of departure_date and departureDate keys:
    JSON_PATCH_PATTERN = re.compile(r'(?ims)"departure_?date".*?:.*?(\{.*?\})')

    @classmethod
    def get_future_date(cls, days=90):
        current_date = datetime.utcnow()
        return current_date + relativedelta(days=days)

    @classmethod
    def load_dates_str(cls, body):
        while (pos := body.find(cls.STR_PATCH_NAME)) != -1:
            str_to_replace = body[pos : body.find(")", pos) + 1]
            params = str_to_replace[str_to_replace.find("(") + 1 : -1]
            days, fmt = [i for i in params.split(",")]
            new_date = cls.get_future_date(days=int(days))
            new_date_str = datetime.strftime(new_date, fmt)
            body = body.replace(str_to_replace, new_date_str)
        return body

    @classmethod
    def load_dates_json(cls, body):
        while (pos := body.find(cls.JSON_PATCH_NAME)) != -1:
            str_to_replace = body[pos : body.find(")", pos) + 1]
            params = str_to_replace[str_to_replace.find("(") + 1 : -1]
            days = int(params)
            new_date = cls.get_future_date(days=days)
            new_date_json = json.dumps(
                {
                    "year": new_date.year,
                    "month": new_date.month,
                    "day": new_date.day,
                }
            )
            body = body.replace(str_to_replace, new_date_json)
        return body

    @classmethod
    def load_dates(cls, body):
        body = cls.load_dates_str(body)
        body = cls.load_dates_json(body)
        return body

    @staticmethod
    def get_date_delta(date):
        now = datetime.utcnow().date()
        delta = date - now
        return delta.days

    @classmethod
    def get_str_date_replace(cls, match, fmt):
        date = datetime.strptime(match, fmt).date()
        days = cls.get_date_delta(date)
        replace_str = cls.STR_PATCH_REPLACE.format(days=days, fmt=fmt)
        return replace_str

    @classmethod
    def get_json_date_replace(cls, match):
        params = json.loads(match)
        date = datetime(params["year"], params["month"], params["day"]).date()
        days = cls.get_date_delta(date)
        replace_str = cls.JSON_PATCH_REPLACE.format(days=days)
        return replace_str

    @classmethod
    def replace_dates_str(cls, body):
        for pattern, fmt in cls.STR_PATCH_PATTERNS:
            for match in set(pattern.findall(body)):
                if isinstance(match, tuple):
                    match = match[0]
                replace_str = cls.get_str_date_replace(match, fmt)
                body = body.replace(match, replace_str)
        return body

    @classmethod
    def replace_dates_json(cls, body):
        for match in set(cls.JSON_PATCH_PATTERN.findall(body)):
            if isinstance(match, tuple):
                match = match[0]
            replace_str = cls.get_json_date_replace(match)
            body = body.replace(match, replace_str)
        return body

    @classmethod
    def replace_dates(cls, body):
        body = cls.replace_dates_str(body)
        body = cls.replace_dates_json(body)
        return body


class StubsProcessor:
    @classmethod
    def add_mock_id_predicates(cls, stubs, mock_id):
        processed_stubs = deepcopy(stubs)
        for stub in processed_stubs:
            predicate = {
                "caseSensitive": True,
                "contains": {"headers": {"X-Context": mock_id}},
            }
            stub.setdefault("predicates", []).append(predicate)
        return processed_stubs

    @classmethod
    def mock_id_matches(cls, stub, mock_id):
        if mock_id is None:
            return True
        for predicate in stub.get("predicates", []):
            if mock_id in dpath.values(predicate, "contains/headers/X-Context"):
                return True
        return False

    @classmethod
    def get_stubs_ids_to_remove(cls, old_stubs, mock_id=None):
        return [
            old_stubs.index(stub)
            for stub in old_stubs
            if cls.mock_id_matches(stub, mock_id)
        ]
