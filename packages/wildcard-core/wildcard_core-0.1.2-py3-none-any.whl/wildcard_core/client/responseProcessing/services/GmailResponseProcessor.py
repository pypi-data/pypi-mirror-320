import json
import uuid
import base64
import logging
import mimetypes
import os
from typing import Any, Dict, List

from wildcard_core.logging.types import WildcardLogger
from wildcard_core.client.responseProcessing.IResponseProcessor import (
    IResponseProcessor,
    ProcessedResponse,
    ProcessedResponseData,
)

class GmailResponseProcessor(IResponseProcessor):
    def __init__(self, logger: WildcardLogger):
        """
        Initialize the GmailResponseProcessor.

        Args:
            size_threshold (int): The character length threshold for extracting body content.
        """
        super().__init__(logger)
        self.size_threshold = 1000
        self.documents: Dict[str, str] = {}
        self.logger = logging.getLogger(self.__class__.__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        if not self.logger.handlers:
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)

    async def process(self, tool_name: str, result: Any) -> ProcessedResponse:
        """
        Process the Gmail API response by extracting large body contents.

        Args:
            tool_name (str): The name of the tool (e.g., 'gmail_users_messages_get').
            result (Any): The raw JSON response from the Gmail API.

        Returns:
            ProcessedResponse: The processed response containing cleaned data and extracted documents.
        """
        try:
            response_dict = result
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode JSON response: {e}")
            raise

        documents: Dict[str, str] = {}

        if tool_name in [
            "gmail_users_drafts_get",
            "gmail_users_messages_get",
            "gmail_users_threads_get",
        ]:
            cleaned_response = self._prune_response(response_dict, documents)
            return ProcessedResponse(
                response=response_dict,
                processed_response=ProcessedResponseData(
                    data=cleaned_response,
                    documents=documents,
                ),
            )
        
        elif tool_name in [
            "gmail_users_messages_attachments_get"
        ]:
            # Get documents
            data = response_dict["data"]
            decoded_data = base64.urlsafe_b64decode(data.encode("utf-8"))
            # Re-encode using standard base64 for consistency
            encoded_content = base64.b64encode(decoded_data).decode("utf-8")
            documents[str(uuid.uuid4())] = encoded_content
            
            # Prune resonse
            response_json_copy = response_dict.copy()
            response_json_copy["data"] = None
            
                        
            return ProcessedResponse(
                response=response_dict,
                processed_response=ProcessedResponseData(
                    data=response_json_copy,
                    documents=documents,
                ),
            )

        return ProcessedResponse(
            response=response_dict,
            processed_response=ProcessedResponseData(
                data=response_dict,
                documents=documents,
            ),
        )

    def _prune_response(self, data: Any, documents: Dict[str, str]) -> Any:
        """
        Recursively traverse the JSON data to extract large elements into documents.

        Args:
            data (Any): The JSON data to process.
            documents (Dict[str, str]): The dictionary to store extracted documents.

        Returns:
            Any: The cleaned JSON data with extracted elements removed.
        """
        if isinstance(data, dict):
            cleaned_dict = {}
            for key, value in data.items():
                if key.lower() == "payload":
                    cleaned_dict[key] = self._process_payload(value, documents)
                else:
                    cleaned_dict[key] = self._prune_response(value, documents)
            return cleaned_dict
        elif isinstance(data, list):
            return [self._prune_response(item, documents) for item in data]
        else:
            return data

    def _process_payload(self, payload: Dict[str, Any], documents: Dict[str, str]) -> Dict[str, Any]:
        """
        Process the payload of a message, extracting large body contents and handling MIME types.

        Args:
            payload (Dict[str, Any]): The payload dictionary of the message.
            documents (Dict[str, str]): The dictionary to store extracted documents.

        Returns:
            Dict[str, Any]: The cleaned payload with large bodies extracted.
        """
        # Process the body of the payload
        body = payload.get("body", {})
        data = body.get("data")
        size = body.get("size", 0)
        filename = payload.get("filename", "")
        mime_type = payload.get("mimeType", "application/octet-stream")  # Default MIME type

        if data and size > self.size_threshold:
            try:
                # Decode the base64url encoded data
                decoded_data = base64.urlsafe_b64decode(data.encode("utf-8"))
                # Re-encode using standard base64 for consistency
                encoded_content = base64.b64encode(decoded_data).decode("utf-8")
            except (base64.binascii.Error, UnicodeDecodeError) as e:
                self.logger.error(f"Base64 decoding failed for filename '{filename}': {e}")
            else:
                # Determine the correct file extension based on MIME type
                extension = mimetypes.guess_extension(mime_type)
                if not extension:
                    self.logger.warning(f"Unknown MIME type '{mime_type}' for filename '{filename}'. Using '.bin' as default extension.")
                    extension = ".bin"

                # Sanitize and ensure filename has the correct extension
                base_filename = os.path.splitext(filename)[0] if filename else str(uuid.uuid4())
                sanitized_filename = self._sanitize_filename(base_filename) + extension

                documents[sanitized_filename] = encoded_content
                self.logger.debug(f"Extracted content for key: {sanitized_filename}")

                # Remove the body content as it's been extracted
                payload["body"] = {
                    "attachment_id": None,
                    "data": None,
                    "size": 0,
                }

        # Recursively process parts if they exist
        parts = payload.get("parts", [])
        if parts:
            processed_parts = []
            for part in parts:
                processed_part = self._process_payload(part, documents)
                processed_parts.append(processed_part)
            payload["parts"] = processed_parts

        return payload

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize the filename by removing or replacing invalid characters.

        Args:
            filename (str): The original filename.

        Returns:
            str: The sanitized filename.
        """
        # Remove any path separators
        filename = os.path.basename(filename)
        # Replace any characters that are not alphanumeric, dots, underscores, or hyphens
        sanitized = ''.join(c for c in filename if c.isalnum() or c in (' ', '.', '_', '-')).rstrip()
        if not sanitized:
            sanitized = str(uuid.uuid4())
        return sanitized

    def get_documents(self) -> Dict[str, str]:
        """
        Retrieve the extracted documents.

        Returns:
            Dict[str, str]: A dictionary of extracted documents with keys as filenames or UUIDs.
        """
        return self.documents