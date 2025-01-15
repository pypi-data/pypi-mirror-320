import argparse
import hashlib
import io
import os

import orjson
import requests
from pydantic_settings import BaseSettings
from requests.auth import HTTPBasicAuth

from utic_public_types.plugins.models import PluginType


class EnvSettings(BaseSettings):
    plugin_registry: str | None = None
    plugin_registry_username: str | None = None
    plugin_registry_password: str | None = None


env_settings = EnvSettings()

parser = argparse.ArgumentParser(description="CLI to publish plugin metadata")

# Positional argument for the action
parser.add_argument(
    "cli_action",
    type=str,
    help="Action type (publish|list)",
)

# Positional argument for the plugin path
parser.add_argument(
    "plugin_path",
    type=str,
    help="The full path to the plugin in the format 'myplugin.module.MY_PLUGIN'.",
)

parser.add_argument(
    "--channel",
    type=str,
    default="dev",
    help="The channel to publish to (default: 'dev').",
)

parser.add_argument(
    "--registry",
    type=str,
    default=env_settings.plugin_registry,
    help="The registry to publish to.",
    required=True,
)

parser.add_argument(
    "--registry-username",
    type=str,
    default=env_settings.plugin_registry_username,
    help="The username to use for authentication.",
    required=False,
)

parser.add_argument(
    "--registry-password",
    type=str,
    default=env_settings.plugin_registry_password,
    help="The password to use for authentication.",
    required=False,
)


class OCIRegistry:
    def __init__(self, args):
        self.registry = args.registry.strip("/")
        self.headers = {}
        self.auth = None
        if args.registry_username:
            self.auth = HTTPBasicAuth(args.registry_username, args.registry_password)

    def get_data(self, registry_object_name: str, tag: str) -> dict | None:
        manifest_url = os.path.join(
            self.registry, "v2", registry_object_name, "manifests", tag
        )

        response = requests.get(manifest_url, auth=self.auth)

        if response.status_code == 200:
            metadata_index = response.json()
            index_url = os.path.join(
                self.registry,
                "v2",
                registry_object_name,
                "blobs",
                metadata_index["config"]["digest"],
            )
            response = requests.get(index_url, auth=self.auth)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                response.raise_for_status()
        elif response.status_code == 404:
            return None
        else:
            response.raise_for_status()

    def upload_object(
        self, registry_object_name: str, data: bytes, tags: list[str]
    ) -> None:
        upload_url = os.path.join(
            self.registry, "v2", registry_object_name, "blobs/uploads/"
        )

        response = requests.post(upload_url, auth=self.auth)
        response.raise_for_status()

        # Get the upload location URL
        upload_location = response.headers["Location"]

        # Complete the blob upload with the JSON file
        sha_digest = calculate_sha256(data)
        blob_response = requests.put(
            f"{upload_location}&digest=sha256:{sha_digest}", data=data, auth=self.auth
        )
        blob_response.raise_for_status()

        manifest = {
            "schemaVersion": 2,
            "config": {
                "mediaType": "application/vnd.oci.image.config.v1+json",
                "digest": f"sha256:{sha_digest}",
                "size": len(data),
            },
        }

        headers = {"Content-Type": "application/vnd.oci.image.manifest.v1+json"}

        # Push the manifest to the registry with the specified tag
        for tag in tags:
            manfiest_url = os.path.join(
                self.registry, "v2", registry_object_name, "manifests", tag
            )
            response = requests.put(
                manfiest_url,
                headers=headers,
                data=orjson.dumps(manifest),
                auth=self.auth,
            )
            response.raise_for_status()

    def list_tags(self, registry_object_name: str) -> list[str]:
        list_url = os.path.join(self.registry, "v2", registry_object_name, "tags/list")

        response = requests.get(list_url, auth=self.auth)
        response.raise_for_status()
        return response.json()["tags"]


def calculate_sha256(data: bytes) -> str:
    sha256_hash = hashlib.sha256()
    io_data = io.BytesIO(data)
    for byte_block in iter(lambda: io_data.read(4096), b""):
        sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def get_plugin(plugin_path: str) -> PluginType:
    module_path, _, plugin_name = plugin_path.partition(":")

    module = __import__(module_path)
    plugin = getattr(module, plugin_name)

    assert isinstance(plugin, PluginType)
    return plugin


def get_plugin_registry_name(plugin: PluginType) -> str:
    return f"plugin-metadata-{plugin.type}-{plugin.subtype}"


METADATA_INDEX_KEY = "plugin-metadata"


def update_plugin_index(args):
    plugin = get_plugin(args.plugin_path)
    oci_repo_name = get_plugin_registry_name(plugin)
    registry = OCIRegistry(args)

    metadata = registry.get_data(METADATA_INDEX_KEY, "latest")
    if metadata is not None:
        if oci_repo_name in metadata["plugins"]:
            # already in the index
            return
    else:
        metadata = {"plugins": []}

    metadata["plugins"].append(oci_repo_name)
    raw_metadata = orjson.dumps(metadata)

    registry.upload_object(METADATA_INDEX_KEY, raw_metadata, ["latest"])


def publish_action(args):
    update_plugin_index(args)

    plugin = get_plugin(args.plugin_path)
    oci_repo_name = get_plugin_registry_name(plugin)
    oci_metadata = plugin.model_dump()
    oci_metadata["settings"] = plugin.settings.model_json_schema()
    oci_metadata_json = orjson.dumps(oci_metadata)

    print(f"Publishing {plugin.name} to {args.channel} channel")
    registry = OCIRegistry(args)
    registry.upload_object(
        oci_repo_name, oci_metadata_json, [args.channel, plugin.version]
    )


def list_action(args):
    plugin = get_plugin(args.plugin_path)
    oci_repo_name = get_plugin_registry_name(plugin)

    registry = OCIRegistry(args)
    tags = registry.list_tags(oci_repo_name)
    print("Found tags:")
    for tag in tags:
        print(f" - {tag}")


def version_action(args):
    plugin = get_plugin(args.plugin_path)
    print(plugin.version)


def main():
    args = parser.parse_args()

    if args.cli_action == "publish":
        publish_action(args)
    elif args.cli_action == "list":
        list_action(args)
    elif args.cli_action == "version":
        version_action(args)
    else:
        print("Invalid action")


if __name__ == "__main__":
    main()
