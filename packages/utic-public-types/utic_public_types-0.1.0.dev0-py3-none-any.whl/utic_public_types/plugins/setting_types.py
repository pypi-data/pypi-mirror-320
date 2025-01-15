from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, fields
from pydantic_core import PydanticUndefined
from typing_extensions import Unpack


class PluginFieldInfo(fields.FieldInfo):
    @staticmethod
    def from_field(
        default: Any = PydanticUndefined, **kwargs: Unpack[fields._FromFieldInfoInputs]
    ) -> fields.FieldInfo: ...


def PluginField(default: Any = PydanticUndefined, **kwargs) -> Any:
    return PluginFieldInfo.from_field(default=default, **kwargs)


class PluginSettings(BaseModel): ...


class PluginSettingsFieldGroup(BaseModel):
    identifier: str = Field(title="Identifier", examples=["model-connection-details"])
    members: List[str] = Field(
        title="Members",
        default_factory=set,
        examples=[
            [
                "model.host.endpoint",
                "model.host.port",
                "model.host.api_key",
                "some-group",
            ]
        ],
        description="ordered list of plugin-value identifiers, or other group identifiers. "
        "Cycles are invalid.",
    )


class PluginSettingsPresentationStructure(BaseModel):
    """
    Kept simple at this level to allow plugin authors to indicate baseline structure between fields,
    but to underscore that the best layouts and structures between them might now be knowable at authoring time.
    We specifically acknowledge the role that user-facing experimentation should play in determining this.

    It is expected that there exists a layer of functionality elsewhere that "owns" the layout of fields.
    That layer might rely on this model for defaults and hints. However, it definitely relies upon a few properties
    of the settings definitions. Most notably that each field is uniquely identifiable, that the identifiers
    don't change from version to version, and to some extent, that tagging is utilized with a common vocabulary.
    """

    title: str = Field(
        title="Title",
        examples=["Default Configuration", "Only Required"],
        description="the title given to this particular organization of fields.",
    )
    identifier: str = Field(title="Identifier", examples=["default"])
    groups: List[PluginSettingsFieldGroup] = Field(
        title="Groups",
        description="Ordered list of groups of fields. "
        "Should usually have at least one group, but if empty, "
        "the system should interpret this as a single group "
        "with all fields where order doesn't matter.",
        default_factory=list,
    )


class PluginSettingsFieldConstraint(BaseModel):
    """
    Constraints is a structure to provide guidance to UI layer on how it might coerce or validate input.
    Beware that the structure is simplified, and you might be able to express logically impossible things.
    There may be mutually-exclusive options here, so you can treat this as a "sparse" data structure.
    In general, if a field here is empty it means "this is not a participant in the constraint logic"
    and not "constraint that the value must be empty"

    Note that a fixed value can be enforced by setting a list of length 1 in "available_options".

    Primary motivation for modeling this distinctly from fields is to support multiple Recipes.

    These constraints will override/extend default constraints provided by the field definition.
    """

    description: str = Field(
        title="Description",
        description="Help users understand how to create a valid value.",
        examples=["Sometimes referred to as the Vendor or Host of the model."],
    )
    pattern: Optional[str] = Field(
        title="Regular Expression Pattern",
        description="If set, input must match this pattern. "
        "This is not an input-safety mechanism, just UX guidance.",
    )
    available_options: List[str] = Field(
        title="Available Options",
        default_factory=list,
        description="if set, limit user to selecting one of the available options to override defaults.",
    )
    disable_interaction: bool = Field(
        title="Disable",
        default=False,
        description="if true, do not allow this field to be configured",
    )
    ux_hinting_tags: List[str] = Field(
        title="UX Hinting Tags",
        default_factory=list,
        description="Tags that are expected to have meaning to user interface layer "
        "to help render improved controls. Coordinating tags' implications "
        "is not a goal of this specification.",
        examples=[
            ["numeric", "int", "interval=5", "min=5", "max=25"],
            ["color", "hex", "hsb-sliders"],
        ],
    )


class PluginSettingsRecipe(BaseModel):
    title: str = Field(
        title="Title",
        examples=["Cost Optimized", "Accuracy Optimized"],
        description="the title given to this recipe. "
        "Choose a vocabulary that emphasize the difference between recipes",
    )
    identifier: str = Field(
        title="Identifier", examples=["cost-optimized", "accuracy-optimized"]
    )
    constraints: Dict[str, PluginSettingsFieldConstraint] = Field(
        title="Constraints to Apply",
        description="keys refer to fields. Values are the constraints",
        default_factory=dict,
    )
