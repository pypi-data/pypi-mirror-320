from collections.abc import Sequence
from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, Field


NON_POLICY_FIELDS = ["status", "progress", "authenticated", "albums"]


class AuthenticationResult(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    MFA_REQUIRED = "mfa_required"


class PolicyConfigs(BaseModel):
    # Connection options
    username: str = Field(min_length=1)
    domain: Literal["com", "cn"] = "com"

    # Download options
    directory: str = Field(min_length=1)
    download_via_browser: bool = False
    folder_structure: str = "{:%Y/%m/%d}"
    size: Sequence[Literal["original", "medium", "thumb", "adjusted", "alternative"]] = ["original"]
    live_photo_size: Literal["original", "medium", "thumb"] = "original"
    force_size: bool = False
    align_raw: Literal["original", "alternative", "as-is"] = "original"
    keep_unicode_in_filenames: bool = False
    set_exif_datetime: bool = False
    live_photo_mov_filename_policy: Literal["original", "suffix"] = "suffix"
    file_match_policy: Literal[
        "name-size-dedup-with-suffix", "name-id7"
    ] = "name-size-dedup-with-suffix"
    xmp_sidecar: bool = False
    use_os_locale: bool = False

    # Filter options
    album: str = "All Photos"
    library: Literal["Personal Library", "Shared Library"] = "Personal Library"
    recent: Annotated[int, Field(ge=0)] | None = None
    until_found: Annotated[int, Field(ge=0)] | None = None
    skip_videos: bool = False
    skip_live_photos: bool = False
    file_suffixes: list[str] | None = []
    match_pattern: str | None = None
    created_after: str | None = None
    created_before: str | None = None
    added_after: str | None = None
    added_before: str | None = None

    # Delete options
    auto_delete: bool = False
    delete_after_download: bool = False

    # icloudpd-ui options
    dry_run: bool = False
    interval: str | None = None
    log_level: Literal["debug", "info", "error"] = "info"

    # Integration options
    remove_local_copy: bool = False
    upload_to_aws_s3: bool = False
