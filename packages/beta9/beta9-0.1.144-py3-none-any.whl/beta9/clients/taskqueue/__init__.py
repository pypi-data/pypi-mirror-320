# Generated by the protocol buffer compiler.  DO NOT EDIT!
# sources: taskqueue.proto
# plugin: python-betterproto
# This file has been @generated

from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    AsyncIterator,
    Dict,
    Iterator,
    Optional,
)

import betterproto
import grpc
from betterproto.grpcstub.grpcio_client import SyncServiceStub
from betterproto.grpcstub.grpclib_server import ServiceBase


if TYPE_CHECKING:
    import grpclib.server
    from betterproto.grpcstub.grpclib_client import MetadataLike
    from grpclib.metadata import Deadline


@dataclass(eq=False, repr=False)
class TaskQueuePutRequest(betterproto.Message):
    stub_id: str = betterproto.string_field(1)
    payload: bytes = betterproto.bytes_field(2)


@dataclass(eq=False, repr=False)
class TaskQueuePutResponse(betterproto.Message):
    ok: bool = betterproto.bool_field(1)
    task_id: str = betterproto.string_field(2)


@dataclass(eq=False, repr=False)
class TaskQueuePopRequest(betterproto.Message):
    stub_id: str = betterproto.string_field(1)
    container_id: str = betterproto.string_field(2)


@dataclass(eq=False, repr=False)
class TaskQueuePopResponse(betterproto.Message):
    ok: bool = betterproto.bool_field(1)
    task_msg: bytes = betterproto.bytes_field(2)


@dataclass(eq=False, repr=False)
class TaskQueueLengthRequest(betterproto.Message):
    stub_id: str = betterproto.string_field(1)


@dataclass(eq=False, repr=False)
class TaskQueueLengthResponse(betterproto.Message):
    ok: bool = betterproto.bool_field(1)
    length: int = betterproto.int64_field(2)


@dataclass(eq=False, repr=False)
class TaskQueueCompleteRequest(betterproto.Message):
    task_id: str = betterproto.string_field(1)
    stub_id: str = betterproto.string_field(2)
    task_duration: float = betterproto.float_field(3)
    task_status: str = betterproto.string_field(4)
    container_id: str = betterproto.string_field(5)
    container_hostname: str = betterproto.string_field(6)
    keep_warm_seconds: float = betterproto.float_field(7)


@dataclass(eq=False, repr=False)
class TaskQueueCompleteResponse(betterproto.Message):
    ok: bool = betterproto.bool_field(1)
    message: str = betterproto.string_field(2)


@dataclass(eq=False, repr=False)
class TaskQueueMonitorRequest(betterproto.Message):
    task_id: str = betterproto.string_field(1)
    stub_id: str = betterproto.string_field(2)
    container_id: str = betterproto.string_field(3)


@dataclass(eq=False, repr=False)
class TaskQueueMonitorResponse(betterproto.Message):
    ok: bool = betterproto.bool_field(1)
    cancelled: bool = betterproto.bool_field(2)
    complete: bool = betterproto.bool_field(3)
    timed_out: bool = betterproto.bool_field(4)


@dataclass(eq=False, repr=False)
class StartTaskQueueServeRequest(betterproto.Message):
    stub_id: str = betterproto.string_field(1)
    timeout: int = betterproto.int32_field(2)


@dataclass(eq=False, repr=False)
class StartTaskQueueServeResponse(betterproto.Message):
    output: str = betterproto.string_field(1)
    done: bool = betterproto.bool_field(2)
    exit_code: int = betterproto.int32_field(3)


@dataclass(eq=False, repr=False)
class StopTaskQueueServeRequest(betterproto.Message):
    stub_id: str = betterproto.string_field(1)


@dataclass(eq=False, repr=False)
class StopTaskQueueServeResponse(betterproto.Message):
    ok: bool = betterproto.bool_field(1)


@dataclass(eq=False, repr=False)
class TaskQueueServeKeepAliveRequest(betterproto.Message):
    stub_id: str = betterproto.string_field(1)
    timeout: int = betterproto.int32_field(2)


@dataclass(eq=False, repr=False)
class TaskQueueServeKeepAliveResponse(betterproto.Message):
    ok: bool = betterproto.bool_field(1)


class TaskQueueServiceStub(SyncServiceStub):
    def task_queue_put(
        self, task_queue_put_request: "TaskQueuePutRequest"
    ) -> "TaskQueuePutResponse":
        return self._unary_unary(
            "/taskqueue.TaskQueueService/TaskQueuePut",
            TaskQueuePutRequest,
            TaskQueuePutResponse,
        )(task_queue_put_request)

    def task_queue_pop(
        self, task_queue_pop_request: "TaskQueuePopRequest"
    ) -> "TaskQueuePopResponse":
        return self._unary_unary(
            "/taskqueue.TaskQueueService/TaskQueuePop",
            TaskQueuePopRequest,
            TaskQueuePopResponse,
        )(task_queue_pop_request)

    def task_queue_monitor(
        self, task_queue_monitor_request: "TaskQueueMonitorRequest"
    ) -> Iterator["TaskQueueMonitorResponse"]:
        for response in self._unary_stream(
            "/taskqueue.TaskQueueService/TaskQueueMonitor",
            TaskQueueMonitorRequest,
            TaskQueueMonitorResponse,
        )(task_queue_monitor_request):
            yield response

    def task_queue_complete(
        self, task_queue_complete_request: "TaskQueueCompleteRequest"
    ) -> "TaskQueueCompleteResponse":
        return self._unary_unary(
            "/taskqueue.TaskQueueService/TaskQueueComplete",
            TaskQueueCompleteRequest,
            TaskQueueCompleteResponse,
        )(task_queue_complete_request)

    def task_queue_length(
        self, task_queue_length_request: "TaskQueueLengthRequest"
    ) -> "TaskQueueLengthResponse":
        return self._unary_unary(
            "/taskqueue.TaskQueueService/TaskQueueLength",
            TaskQueueLengthRequest,
            TaskQueueLengthResponse,
        )(task_queue_length_request)

    def start_task_queue_serve(
        self, start_task_queue_serve_request: "StartTaskQueueServeRequest"
    ) -> Iterator["StartTaskQueueServeResponse"]:
        for response in self._unary_stream(
            "/taskqueue.TaskQueueService/StartTaskQueueServe",
            StartTaskQueueServeRequest,
            StartTaskQueueServeResponse,
        )(start_task_queue_serve_request):
            yield response

    def stop_task_queue_serve(
        self, stop_task_queue_serve_request: "StopTaskQueueServeRequest"
    ) -> "StopTaskQueueServeResponse":
        return self._unary_unary(
            "/taskqueue.TaskQueueService/StopTaskQueueServe",
            StopTaskQueueServeRequest,
            StopTaskQueueServeResponse,
        )(stop_task_queue_serve_request)

    def task_queue_serve_keep_alive(
        self, task_queue_serve_keep_alive_request: "TaskQueueServeKeepAliveRequest"
    ) -> "TaskQueueServeKeepAliveResponse":
        return self._unary_unary(
            "/taskqueue.TaskQueueService/TaskQueueServeKeepAlive",
            TaskQueueServeKeepAliveRequest,
            TaskQueueServeKeepAliveResponse,
        )(task_queue_serve_keep_alive_request)
