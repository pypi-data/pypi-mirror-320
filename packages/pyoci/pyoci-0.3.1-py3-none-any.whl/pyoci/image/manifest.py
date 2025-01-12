from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Literal

from pyoci.base_types import Annotations
from pyoci.common import Struct, Unset, UNSET
from pyoci.image.descriptor import ContentDescriptor
from pyoci.image.const import MediaType, OciMediaType


class ImageManifest(Struct):
    config: ContentDescriptor
    layers: Sequence[ContentDescriptor]

    if not TYPE_CHECKING:
        schemaVersion: Literal[2] = 2
        mediaType: Literal[OciMediaType.image_manifest] = OciMediaType.image_manifest

    artifactType: MediaType | Unset = UNSET
    subject: ContentDescriptor | Unset = UNSET
    annotations: Annotations | Unset = UNSET
