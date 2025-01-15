# Copyright 2023 Scale AI. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__version__ = "0.0.0beta45"

import os
from typing import Sequence

import requests
from llmengine.completion import Completion
from llmengine.data_types import (
    BatchCompletionsJob,
    BatchCompletionsJobStatus,
    BatchCompletionsModelConfig,
    CancelFineTuneResponse,
    ChatCompletionV2Request,
    ChatCompletionV2Response,
    CompletionOutput,
    CompletionStreamOutput,
    CompletionStreamResponse,
    CompletionStreamV1Request,
    CompletionStreamV1Response,
    CompletionSyncResponse,
    CompletionSyncV1Request,
    CompletionSyncV1Response,
    CreateBatchCompletionsModelConfig,
    CreateBatchCompletionsRequest,
    CreateBatchCompletionsRequestContent,
    CreateBatchCompletionsResponse,
    CreateBatchCompletionsV1Request,
    CreateBatchCompletionsV1RequestContent,
    CreateBatchCompletionsV1Response,
    CreateBatchCompletionsV2ModelConfig,
    CreateBatchCompletionsV2Request,
    CreateBatchCompletionsV2RequestContent,
    CreateBatchCompletionsV2Response,
    CreateFineTuneRequest,
    CreateFineTuneResponse,
    DeleteFileResponse,
    DeleteLLMEndpointResponse,
    FilteredChatCompletionV2Request,
    FilteredCompletionV2Request,
    GetFileContentResponse,
    GetFileResponse,
    GetFineTuneResponse,
    GetLLMEndpointResponse,
    ListFilesResponse,
    ListFineTunesResponse,
    ListLLMEndpointsResponse,
    ModelDownloadRequest,
    ModelDownloadResponse,
    UploadFileResponse,
    VLLMEndpointAdditionalArgs,
)
from llmengine.file import File
from llmengine.fine_tuning import FineTune
from llmengine.model import Model

__all__: Sequence[str] = (
    "BatchCompletionsJob",
    "CreateBatchCompletionsV2Response",
    "FilteredCompletionV2Request",
    "FilteredChatCompletionV2Request",
    "BatchCompletionsJobStatus",
    "CompletionSyncV1Request",
    "CompletionSyncV1Response",
    "CompletionStreamV1Request",
    "CompletionStreamV1Response",
    "CancelFineTuneResponse",
    "ChatCompletionV2Request",
    "ChatCompletionV2Response",
    "VLLMEndpointAdditionalArgs",
    "Completion",
    "CompletionOutput",
    "CompletionStreamOutput",
    "CompletionStreamResponse",
    "CompletionSyncResponse",
    "CreateBatchCompletionsModelConfig",
    "CreateBatchCompletionsRequest",
    "CreateBatchCompletionsRequestContent",
    "CreateBatchCompletionsResponse",
    "CreateBatchCompletionsV1Request",
    "CreateBatchCompletionsV1RequestContent",
    "CreateBatchCompletionsV1Response",
    "CreateBatchCompletionsV2Request",
    "CreateBatchCompletionsV2RequestContent",
    "CreateBatchCompletionsV2ModelConfig",
    "BatchCompletionsModelConfig",
    "CreateFineTuneRequest",
    "CreateFineTuneResponse",
    "DeleteFileResponse",
    "DeleteLLMEndpointResponse",
    "ModelDownloadRequest",
    "ModelDownloadResponse",
    "GetFileContentResponse",
    "File",
    "FineTune",
    "GetFileResponse",
    "GetFineTuneResponse",
    "GetLLMEndpointResponse",
    "ListFilesResponse",
    "ListFineTunesResponse",
    "ListLLMEndpointsResponse",
    "Model",
    "UploadFileResponse",
)


def check_version():
    try:
        current_version = __version__
        response = requests.get("https://pypi.org/pypi/scale-llm-engine/json")
        latest_version = response.json()["info"]["version"]

        if current_version != latest_version:
            print(
                f"A newer version ({latest_version}) of 'scale-llm-engine' is available. Please upgrade!"
            )
            print("To upgrade, run: pip install --upgrade scale-llm-engine")
            print(
                "Don't want to see this message? Set the environment variable 'LLM_ENGINE_DISABLE_VERSION_CHECK' to 'true'."
            )
    except requests.RequestException:
        # Handle exceptions related to the request (like timeouts, connection errors, etc.)
        print(
            "Failed to check for the most recent llm-engine package version. Please check your internet connection."
        )
    except Exception:
        print("Something went wrong with checking for the most recent llm-engine package version.")


if not os.environ.get("LLM_ENGINE_DISABLE_VERSION_CHECK"):
    check_version()
