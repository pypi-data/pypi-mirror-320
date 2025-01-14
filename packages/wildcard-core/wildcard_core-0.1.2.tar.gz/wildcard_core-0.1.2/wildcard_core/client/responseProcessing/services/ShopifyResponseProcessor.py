from wildcard_core.client.responseProcessing.IResponseProcessor import IResponseProcessor, ProcessedResponse, ProcessedResponseData
from typing import Any

class ShopifyResponseProcessor(IResponseProcessor):
    async def process(self, tool_name: str, result: Any) -> ProcessedResponse:
        return ProcessedResponse(response=result, processed_response=ProcessedResponseData(data=result, documents={}))