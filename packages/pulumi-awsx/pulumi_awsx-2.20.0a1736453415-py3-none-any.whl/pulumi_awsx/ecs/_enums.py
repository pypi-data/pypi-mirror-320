# coding=utf-8
# *** WARNING: this file was generated by pulumi-gen-awsx. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

from enum import Enum

__all__ = [
    'TaskDefinitionPortMappingAppProtocol',
]


class TaskDefinitionPortMappingAppProtocol(str, Enum):
    HTTP = "http"
    HTTP2 = "http2"
    GRPC = "grpc"
