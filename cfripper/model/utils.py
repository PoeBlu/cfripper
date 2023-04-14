"""
Copyright 2018 Skyscanner Ltd

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import json
import logging
import re
from contextlib import suppress

import yaml

from urllib.parse import unquote
from cfn_flip import to_json

logger = logging.getLogger(__file__)


class InvalidURLException(Exception):
    pass


def extract_bucket_name_and_path_from_url(url):
    # Remove query string
    url = unquote(url).split("?")[0]

    bucket_name = None
    path = None

    if match := re.search(r"^https://([^.]+).s3.amazonaws.com(.*?)$", url):
        bucket_name, path = match[1], match[2][1:]

    if match := re.search(
        r"^https://([^.]+).s3-[^\.]+.amazonaws.com(.*?)$", url
    ):
        bucket_name, path = match[1], match[2][1:]

    if match := re.search(r"^https://s3.amazonaws.com/([^\/]+)(.*?)$", url):
        bucket_name, path = match[1], match[2][1:]

    if match := re.search(
        r"^https://s3.[^.]+.amazonaws.com/([^\/]+)(.*?)$", url
    ):
        bucket_name, path = match[1], match[2][1:]

    if match := re.search(
        r"^https://s3-[^.]+.amazonaws.com/([^\/]+)(.*?)$", url
    ):
        bucket_name, path = match[1], match[2][1:]

    if bucket_name is None and path is None:
        raise InvalidURLException(f"Couldn't extract bucket name and path from url: {url}")

    logger.info(f"extract_bucket_name_and_path_from_url. returning for {bucket_name} and {path} for {url}")

    return bucket_name, path


def convert_json_or_yaml_to_dict(file_content):
    with suppress(ValueError):
        return json.loads(file_content)

    try:
        # Convert file_content (assuming that is YAML) to JSON if possible
        file_content = to_json(file_content)
        return json.loads(file_content)
    except yaml.YAMLError:
        logger.exception("Could not convert YAML to JSON template")
    except ValueError:
        logger.exception("Could not parse JSON template")

    return None
