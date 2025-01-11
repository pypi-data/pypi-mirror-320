# Generated by the protocol buffer compiler.  DO NOT EDIT!
# sources: volume.proto
# plugin: python-betterproto
# This file has been @generated

from dataclasses import dataclass
from datetime import datetime
from typing import (
    TYPE_CHECKING,
    AsyncIterable,
    AsyncIterator,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Union,
)

import betterproto
import grpc
from betterproto.grpcstub.grpcio_client import SyncServiceStub
from betterproto.grpcstub.grpclib_server import ServiceBase


if TYPE_CHECKING:
    import grpclib.server
    from betterproto.grpcstub.grpclib_client import MetadataLike
    from grpclib.metadata import Deadline


class PresignedUrlMethod(betterproto.Enum):
    GetObject = 0
    PutObject = 1
    HeadObject = 2
    UploadPart = 3


@dataclass(eq=False, repr=False)
class VolumeInstance(betterproto.Message):
    id: str = betterproto.string_field(1)
    name: str = betterproto.string_field(2)
    size: int = betterproto.uint64_field(3)
    created_at: datetime = betterproto.message_field(4)
    updated_at: datetime = betterproto.message_field(5)
    workspace_id: str = betterproto.string_field(6)
    workspace_name: str = betterproto.string_field(7)


@dataclass(eq=False, repr=False)
class GetOrCreateVolumeRequest(betterproto.Message):
    name: str = betterproto.string_field(1)


@dataclass(eq=False, repr=False)
class GetOrCreateVolumeResponse(betterproto.Message):
    ok: bool = betterproto.bool_field(1)
    err_msg: str = betterproto.string_field(2)
    volume: "VolumeInstance" = betterproto.message_field(3)


@dataclass(eq=False, repr=False)
class DeleteVolumeRequest(betterproto.Message):
    name: str = betterproto.string_field(1)


@dataclass(eq=False, repr=False)
class DeleteVolumeResponse(betterproto.Message):
    ok: bool = betterproto.bool_field(1)
    err_msg: str = betterproto.string_field(2)


@dataclass(eq=False, repr=False)
class PathInfo(betterproto.Message):
    path: str = betterproto.string_field(1)
    size: int = betterproto.uint64_field(2)
    mod_time: datetime = betterproto.message_field(3)
    is_dir: bool = betterproto.bool_field(4)


@dataclass(eq=False, repr=False)
class ListPathRequest(betterproto.Message):
    path: str = betterproto.string_field(1)


@dataclass(eq=False, repr=False)
class ListPathResponse(betterproto.Message):
    ok: bool = betterproto.bool_field(1)
    err_msg: str = betterproto.string_field(2)
    path_infos: List["PathInfo"] = betterproto.message_field(3)


@dataclass(eq=False, repr=False)
class DeletePathRequest(betterproto.Message):
    path: str = betterproto.string_field(1)


@dataclass(eq=False, repr=False)
class DeletePathResponse(betterproto.Message):
    ok: bool = betterproto.bool_field(1)
    err_msg: str = betterproto.string_field(2)
    deleted: List[str] = betterproto.string_field(3)


@dataclass(eq=False, repr=False)
class CopyPathRequest(betterproto.Message):
    path: str = betterproto.string_field(1)
    content: bytes = betterproto.bytes_field(2)


@dataclass(eq=False, repr=False)
class CopyPathResponse(betterproto.Message):
    ok: bool = betterproto.bool_field(1)
    object_id: str = betterproto.string_field(2)
    err_msg: str = betterproto.string_field(3)


@dataclass(eq=False, repr=False)
class ListVolumesRequest(betterproto.Message):
    pass


@dataclass(eq=False, repr=False)
class ListVolumesResponse(betterproto.Message):
    ok: bool = betterproto.bool_field(1)
    err_msg: str = betterproto.string_field(2)
    volumes: List["VolumeInstance"] = betterproto.message_field(3)


@dataclass(eq=False, repr=False)
class MovePathRequest(betterproto.Message):
    original_path: str = betterproto.string_field(1)
    new_path: str = betterproto.string_field(2)


@dataclass(eq=False, repr=False)
class MovePathResponse(betterproto.Message):
    ok: bool = betterproto.bool_field(1)
    err_msg: str = betterproto.string_field(2)
    new_path: str = betterproto.string_field(3)


@dataclass(eq=False, repr=False)
class StatPathRequest(betterproto.Message):
    path: str = betterproto.string_field(1)


@dataclass(eq=False, repr=False)
class StatPathResponse(betterproto.Message):
    ok: bool = betterproto.bool_field(1)
    err_msg: str = betterproto.string_field(2)
    path_info: "PathInfo" = betterproto.message_field(3)


@dataclass(eq=False, repr=False)
class PresignedUrlParams(betterproto.Message):
    upload_id: str = betterproto.string_field(1)
    part_number: int = betterproto.uint32_field(2)
    content_length: int = betterproto.uint64_field(3)
    content_type: str = betterproto.string_field(4)


@dataclass(eq=False, repr=False)
class GetFileServiceInfoRequest(betterproto.Message):
    pass


@dataclass(eq=False, repr=False)
class GetFileServiceInfoResponse(betterproto.Message):
    ok: bool = betterproto.bool_field(1)
    err_msg: str = betterproto.string_field(2)
    enabled: bool = betterproto.bool_field(3)
    command_version: int = betterproto.uint32_field(4)


@dataclass(eq=False, repr=False)
class CreatePresignedUrlRequest(betterproto.Message):
    volume_name: str = betterproto.string_field(1)
    volume_path: str = betterproto.string_field(2)
    expires: int = betterproto.uint32_field(3)
    method: "PresignedUrlMethod" = betterproto.enum_field(4)
    params: "PresignedUrlParams" = betterproto.message_field(5)


@dataclass(eq=False, repr=False)
class CreatePresignedUrlResponse(betterproto.Message):
    ok: bool = betterproto.bool_field(1)
    err_msg: str = betterproto.string_field(2)
    url: str = betterproto.string_field(3)


@dataclass(eq=False, repr=False)
class CreateMultipartUploadRequest(betterproto.Message):
    volume_name: str = betterproto.string_field(1)
    volume_path: str = betterproto.string_field(2)
    chunk_size: int = betterproto.uint64_field(3)
    file_size: int = betterproto.uint64_field(4)


@dataclass(eq=False, repr=False)
class FileUploadPart(betterproto.Message):
    number: int = betterproto.uint32_field(1)
    start: int = betterproto.uint64_field(2)
    end: int = betterproto.uint64_field(3)
    url: str = betterproto.string_field(4)


@dataclass(eq=False, repr=False)
class CreateMultipartUploadResponse(betterproto.Message):
    ok: bool = betterproto.bool_field(1)
    err_msg: str = betterproto.string_field(2)
    upload_id: str = betterproto.string_field(3)
    file_upload_parts: List["FileUploadPart"] = betterproto.message_field(4)


@dataclass(eq=False, repr=False)
class CompletedPart(betterproto.Message):
    number: int = betterproto.uint32_field(1)
    etag: str = betterproto.string_field(2)


@dataclass(eq=False, repr=False)
class CompleteMultipartUploadRequest(betterproto.Message):
    upload_id: str = betterproto.string_field(1)
    volume_name: str = betterproto.string_field(2)
    volume_path: str = betterproto.string_field(3)
    completed_parts: List["CompletedPart"] = betterproto.message_field(4)


@dataclass(eq=False, repr=False)
class CompleteMultipartUploadResponse(betterproto.Message):
    ok: bool = betterproto.bool_field(1)
    err_msg: str = betterproto.string_field(2)


@dataclass(eq=False, repr=False)
class AbortMultipartUploadRequest(betterproto.Message):
    upload_id: str = betterproto.string_field(1)
    volume_name: str = betterproto.string_field(2)
    volume_path: str = betterproto.string_field(3)


@dataclass(eq=False, repr=False)
class AbortMultipartUploadResponse(betterproto.Message):
    ok: bool = betterproto.bool_field(1)
    err_msg: str = betterproto.string_field(2)


class VolumeServiceStub(SyncServiceStub):
    def get_or_create_volume(
        self, get_or_create_volume_request: "GetOrCreateVolumeRequest"
    ) -> "GetOrCreateVolumeResponse":
        return self._unary_unary(
            "/volume.VolumeService/GetOrCreateVolume",
            GetOrCreateVolumeRequest,
            GetOrCreateVolumeResponse,
        )(get_or_create_volume_request)

    def delete_volume(
        self, delete_volume_request: "DeleteVolumeRequest"
    ) -> "DeleteVolumeResponse":
        return self._unary_unary(
            "/volume.VolumeService/DeleteVolume",
            DeleteVolumeRequest,
            DeleteVolumeResponse,
        )(delete_volume_request)

    def list_volumes(
        self, list_volumes_request: "ListVolumesRequest"
    ) -> "ListVolumesResponse":
        return self._unary_unary(
            "/volume.VolumeService/ListVolumes",
            ListVolumesRequest,
            ListVolumesResponse,
        )(list_volumes_request)

    def list_path(self, list_path_request: "ListPathRequest") -> "ListPathResponse":
        return self._unary_unary(
            "/volume.VolumeService/ListPath",
            ListPathRequest,
            ListPathResponse,
        )(list_path_request)

    def delete_path(
        self, delete_path_request: "DeletePathRequest"
    ) -> "DeletePathResponse":
        return self._unary_unary(
            "/volume.VolumeService/DeletePath",
            DeletePathRequest,
            DeletePathResponse,
        )(delete_path_request)

    def copy_path_stream(
        self, copy_path_request_iterator: Iterable["CopyPathRequest"]
    ) -> "CopyPathResponse":
        return (
            self._stream_unary(
                "/volume.VolumeService/CopyPathStream",
                CopyPathRequest,
                CopyPathResponse,
            )
            .future(copy_path_request_iterator)
            .result()
        )

    def move_path(self, move_path_request: "MovePathRequest") -> "MovePathResponse":
        return self._unary_unary(
            "/volume.VolumeService/MovePath",
            MovePathRequest,
            MovePathResponse,
        )(move_path_request)

    def stat_path(self, stat_path_request: "StatPathRequest") -> "StatPathResponse":
        return self._unary_unary(
            "/volume.VolumeService/StatPath",
            StatPathRequest,
            StatPathResponse,
        )(stat_path_request)

    def get_file_service_info(
        self, get_file_service_info_request: "GetFileServiceInfoRequest"
    ) -> "GetFileServiceInfoResponse":
        return self._unary_unary(
            "/volume.VolumeService/GetFileServiceInfo",
            GetFileServiceInfoRequest,
            GetFileServiceInfoResponse,
        )(get_file_service_info_request)

    def create_presigned_url(
        self, create_presigned_url_request: "CreatePresignedUrlRequest"
    ) -> "CreatePresignedUrlResponse":
        return self._unary_unary(
            "/volume.VolumeService/CreatePresignedURL",
            CreatePresignedUrlRequest,
            CreatePresignedUrlResponse,
        )(create_presigned_url_request)

    def create_multipart_upload(
        self, create_multipart_upload_request: "CreateMultipartUploadRequest"
    ) -> "CreateMultipartUploadResponse":
        return self._unary_unary(
            "/volume.VolumeService/CreateMultipartUpload",
            CreateMultipartUploadRequest,
            CreateMultipartUploadResponse,
        )(create_multipart_upload_request)

    def complete_multipart_upload(
        self, complete_multipart_upload_request: "CompleteMultipartUploadRequest"
    ) -> "CompleteMultipartUploadResponse":
        return self._unary_unary(
            "/volume.VolumeService/CompleteMultipartUpload",
            CompleteMultipartUploadRequest,
            CompleteMultipartUploadResponse,
        )(complete_multipart_upload_request)

    def abort_multipart_upload(
        self, abort_multipart_upload_request: "AbortMultipartUploadRequest"
    ) -> "AbortMultipartUploadResponse":
        return self._unary_unary(
            "/volume.VolumeService/AbortMultipartUpload",
            AbortMultipartUploadRequest,
            AbortMultipartUploadResponse,
        )(abort_multipart_upload_request)
