import enum
from typing import Optional

from pydantic import BaseModel, SecretStr

from utic_public_types.plugins.setting_types import (
    PluginField,
    PluginSettingsFieldGroup,
    PluginSettingsPresentationStructure,
)

from .models import (
    PluginIOItemCardinality,
    PluginIOTypeDescriptor,
    PluginType,
    UnstructuredPluginSignature,
)
from .taxonomy import (
    ArtifactStructuredness,
    StructuredFormatType,
    UnstructuredFormatType,
)

SOURCE = PluginType(
    name="S3 Source",
    type="source",
    subtype="s3",
    version="0.1.0",
    image_name="platform-plugin-source",
    settings=BaseModel,  # not in this example
    signature=UnstructuredPluginSignature(
        inputs=[],
        outputs=[
            PluginIOTypeDescriptor(
                name="files",
                compatibility_specifier="*",
                cardinality=PluginIOItemCardinality.ZERO_OR_MORE,
            )
        ],
    ),
)
DESTINATION = PluginType(
    name="S3 Destination",
    type="destination",
    subtype="s3",
    version="0.1.0",
    image_name="platform-plugin-destination",
    settings=BaseModel,  # not in this example
    signature=UnstructuredPluginSignature(
        inputs=[
            PluginIOTypeDescriptor(
                name="files",
                compatibility_specifier="*",
                cardinality=PluginIOItemCardinality.ZERO_OR_MORE,
            )
        ],
        outputs=[],
    ),
)
UTIC_DOCUMENT_PARTITIONER = PluginType(
    name="Partitioner",
    type="destination",
    subtype="generic",
    version="0.1.0",
    image_name="platform-plugin-partitioner",
    settings=BaseModel,  # not in this example
    signature=UnstructuredPluginSignature.one_to_one(
        intype=f"/{ArtifactStructuredness.UNSTRUCTURED}/{UnstructuredFormatType.PRINTABLE_DOCUMENT}/*",
        outtype=f"/{ArtifactStructuredness.STRUCTURED}/{StructuredFormatType.TEXT}/json/utic-elements",
    ),
)


class OpenAIEmbeddingModels(str, enum.Enum):
    SMALL = "text-embedding-3-small"
    LARGE = "text-embedding-3-large"
    ADA_002 = "text-embedding-ada-002"


class OpenAIEmbedderSettings(BaseModel):
    model_name: OpenAIEmbeddingModels = PluginField(
        OpenAIEmbeddingModels.LARGE,
        title="Model Name",
        description="The model name to use.",
    )
    api_key: Optional[SecretStr] = PluginField()


class HuggingFaceEmbeddingModels(str, enum.Enum):
    ALL_MINILM_L6_V2 = "sentence-transformers/all-MiniLM-L6-v2"


class HuggingfaceEmbedderSettings(BaseModel):
    model_name: HuggingFaceEmbeddingModels = PluginField(
        HuggingFaceEmbeddingModels.ALL_MINILM_L6_V2
    )
    api_key: Optional[SecretStr] = PluginField()


OPENAI_EMBEDDER_PLUGIN = PluginType(
    type="embedder",
    subtype="openai",
    name="Embedder",
    version="0.1.0",
    image_name="platform-plugin-embedder",
    settings=OpenAIEmbedderSettings,
    presentation_structures={
        # by default, we don't show the api key in our platform but it IS a setting
        "default": PluginSettingsPresentationStructure(
            title="OpenAI Configuration",
            identifier="default",
            groups=[
                PluginSettingsFieldGroup(
                    identifier="only-model-name",
                    members=["model_name"],
                )
            ],
        )
    },
    recipes={},
)
HUGGINGFACE_EMBEDDER_PLUGIN = PluginType(
    type="embedder",
    subtype="huggingface",
    name="Embedder",
    version="0.1.0",
    image_name="platform-plugin-embedder",
    settings=HuggingfaceEmbedderSettings,
    presentation_structures={
        # by default, we don't show the api key in our platform but it IS a setting
        "default": PluginSettingsPresentationStructure(
            title="Huggingface Configuration",
            identifier="default",
            groups=[
                PluginSettingsFieldGroup(
                    identifier="only-model-name",
                    members=["model_name"],
                )
            ],
        )
    },
    recipes={},
)
