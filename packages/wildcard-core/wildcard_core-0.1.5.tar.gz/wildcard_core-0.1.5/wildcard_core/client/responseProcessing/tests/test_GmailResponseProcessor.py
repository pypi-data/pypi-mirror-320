import unittest
import json
import os
from unittest.mock import patch
from wildcard_core.client.responseProcessing.services.GmailResponseProcessor import GmailResponseProcessor
from wildcard_core.client.responseProcessing.IResponseProcessor import ProcessedResponse
import asyncio

class TestGmailResponseProcessor(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        """
        Initialize the GmailResponseProcessor before each test.
        """
        self.processor = GmailResponseProcessor()
        # Sample UUIDs for testing purposes
        self.sample_uuid = "550e8400-e29b-41d4-a716-446655440000"
        self.sample_uuid_html = "123e4567-e89b-12d3-a456-426614174000"

        # Sample email JSON with content and attachment
        self.email_json = {
            "history_id": "3298",
            "id": "19404ff157703c87",
            "internal_date": "1735250600000",
            "label_ids": ["CATEGORY_PERSONAL", "INBOX"],
            "payload": {
                "body": {
                    "attachment_id": None,
                    "data": None,
                    "size": 0
                },
                "filename": "",
                "headers": [
                    {
                        "name": "Subject",
                        "value": "Test Email with Content and Attachment"
                    }
                ],
                "mime_type": "multipart/mixed",
                "part_id": "",
                "parts": [
                    {
                        "body": {
                            "attachment_id": None,
                            "data": None,
                            "size": 0
                        },
                        "filename": "",
                        "headers": [
                            {
                                "name": "Content-Type",
                                "value": "multipart/alternative; boundary=\"0000000000005732e0062a3384b8\""
                            }
                        ],
                        "mime_type": "multipart/alternative",
                        "part_id": "0",
                        "parts": [
                            {
                                "body": {
                                    "attachment_id": None,
                                    "data": "PGh0bWw+ZGlmZi48L2h0bWw+",
                                    "size": 1500
                                },
                                "filename": "",
                                "headers": [
                                    {
                                        "name": "Content-Type",
                                        "value": "text/html; charset=\"UTF-8\""
                                    },
                                    {
                                        "name": "Content-Transfer-Encoding",
                                        "value": "base64"
                                    }
                                ],
                                "mime_type": "text/html",
                                "part_id": "0.1",
                                "parts": None
                            }
                        ]
                    },
                    {
                        "body": {
                            "attachment_id": "ANGjdJ8iSR93Psikb7fT-PVzgWU...",
                            "data": None,
                            "size": 381360
                        },
                        "filename": "quot1717 - 2024-12-26T160248.507.pdf",
                        "headers": [
                            {
                                "name": "Content-Type",
                                "value": "application/pdf; name=\"quot1717 - 2024-12-26T160248.507.pdf\""
                            },
                            {
                                "name": "Content-Disposition",
                                "value": "attachment; filename=\"quot1717 - 2024-12-26T160248.507.pdf\""
                            },
                            {
                                "name": "Content-Transfer-Encoding",
                                "value": "base64"
                            },
                            {
                                "name": "Content-ID",
                                "value": "<f_m55veiuj0>"
                            },
                            {
                                "name": "X-Attachment-Id",
                                "value": "f_m55veiuj0"
                            }
                        ],
                        "mime_type": "application/pdf",
                        "part_id": "1",
                        "parts": None
                    }
                ]
            },
            "raw": None,
            "size_estimate": 585913,
            "snippet": "See attached quotes. Thank you, Abby Longmore Customer Service Rep | Pratt Industries Wichita | 5700 N Hydraulic Ave Park City, KS | 316-832-3228 Pratt will be closed 1/1/25 for New Years Day On Fri,",
            "thread_id": "193e0d6f6d34ffde"
        }

    @patch('wildcard_core.tool_search.responseProcessing.services.GmailResponseProcessor.uuid.uuid4')
    async def test_prune_content(self, mock_uuid):
        """
        Test that content fields like 'snippet' and 'text/html' parts are pruned and stored as documents.
        """
        # Mock UUIDs as needed
        mock_uuid.return_value = self.sample_uuid

        # Process the email
        processed_response: ProcessedResponse = await self.processor.process("gmail_users_messages_get", json.dumps(self.email_json))

        # Assertions for snippet replacement
        self.assertEqual(processed_response.processed_response.data["snippet"], self.sample_uuid)
        self.assertIn(self.sample_uuid, processed_response.processed_response.documents)
        self.assertEqual(
            processed_response.processed_response.documents[self.sample_uuid],
            self.email_json["snippet"]
        )

        # Assertions for text/html part replacement
        parts = processed_response.processed_response.data["payload"]["parts"]
        self.assertTrue(parts, "No parts found in payload")
        # Assuming first part has parts
        alternative_parts = parts[0].get("parts", [])
        self.assertTrue(alternative_parts, "No alternative parts found")
        text_html_part = next((part for part in alternative_parts if part["part_id"] == "0.1"), None)
        self.assertIsNotNone(text_html_part, "text/html part not found")
        self.assertEqual(text_html_part["body"]["data"], self.sample_uuid_html)
        self.assertIn(self.sample_uuid_html, processed_response.processed_response.documents)
        self.assertEqual(
            processed_response.processed_response.documents[self.sample_uuid_html],
            self.email_json["payload"]["parts"][0]["parts"][0]["body"]["data"]
        )

    @patch('wildcard_core.tool_search.responseProcessing.services.GmailResponseProcessor.uuid.uuid4')
    async def test_handle_attachments(self, mock_uuid):
        """
        Test that attachments are correctly identified and not extracted as documents.
        """
        # Mock UUIDs as needed
        mock_uuid.return_value = self.sample_uuid

        # Process the email
        processed_response: ProcessedResponse = await self.processor.process("gmail_users_messages_get", json.dumps(self.email_json))

        # Retrieve the payload
        payload = processed_response.processed_response.data["payload"]

        # Assertions for attachment presence
        attachments = [part for part in payload["parts"] if part["mime_type"] == "application/pdf"]
        self.assertEqual(len(attachments), 1)
        attachment = attachments[0]
        self.assertIn("attachment_id", attachment["body"])
        self.assertIsNotNone(attachment["body"]["attachment_id"])
        self.assertEqual(attachment["filename"], "quot1717 - 2024-12-26T160248.507.pdf")

        # Ensure attachment is not in documents
        self.assertNotIn(attachment["part_id"], processed_response.processed_response.documents)
        self.assertNotIn(attachment["body"]["attachment_id"], processed_response.processed_response.documents)

    @patch('wildcard_core.tool_search.responseProcessing.services.GmailResponseProcessor.uuid.uuid4')
    async def test_combined_content_and_attachments(self, mock_uuid):
        """
        Test that both content pruning and attachment identification work correctly together.
        """
        # Mock UUIDs as needed
        mock_uuid.side_effect = [
            self.sample_uuid,        # For snippet
            self.sample_uuid_html    # For text/html part
        ]

        # Process the email
        processed_response: ProcessedResponse = await self.processor.process("gmail_users_messages_get", json.dumps(self.email_json))

        # Assertions for snippet replacement
        self.assertEqual(processed_response.processed_response.data["snippet"], self.sample_uuid)
        self.assertIn(self.sample_uuid, processed_response.processed_response.documents)
        self.assertEqual(
            processed_response.processed_response.documents[self.sample_uuid],
            self.email_json["snippet"]
        )

        # Assertions for text/html part replacement
        parts = processed_response.processed_response.data["payload"]["parts"]
        self.assertTrue(parts, "No parts found in payload")
        # Assuming first part has parts
        alternative_parts = parts[0].get("parts", [])
        self.assertTrue(alternative_parts, "No alternative parts found")
        text_html_part = next((part for part in alternative_parts if part["part_id"] == "0.1"), None)
        self.assertIsNotNone(text_html_part, "text/html part not found")
        self.assertEqual(text_html_part["body"]["data"], self.sample_uuid_html)
        self.assertIn(self.sample_uuid_html, processed_response.processed_response.documents)
        self.assertEqual(
            processed_response.processed_response.documents[self.sample_uuid_html],
            self.email_json["payload"]["parts"][0]["parts"][0]["body"]["data"]
        )

        # Assertions for attachment presence
        attachments = [part for part in processed_response.processed_response.data["payload"]["parts"] if part["mime_type"] == "application/pdf"]
        self.assertEqual(len(attachments), 1)
        attachment = attachments[0]
        self.assertIn("attachment_id", attachment["body"])
        self.assertIsNotNone(attachment["body"]["attachment_id"])
        self.assertEqual(attachment["filename"], "quot1717 - 2024-12-26T160248.507.pdf")

        # Ensure attachment is not in documents
        self.assertNotIn(attachment["part_id"], processed_response.processed_response.documents)
        self.assertNotIn(attachment["body"]["attachment_id"], processed_response.processed_response.documents)

    @patch('wildcard_core.tool_search.responseProcessing.services.GmailResponseProcessor.uuid.uuid4')
    async def test_process_large_thread(self, mock_uuid):
        """
        Test processing a large thread using data from testLargeThread.json.
        """
        # Mock UUIDs as needed; assuming multiple UUIDs will be generated
        mock_uuid.side_effect = [f"uuid{i}" for i in range(1, 21)]

        # Determine the path to the testLargeThread.json file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_file_path = os.path.join(current_dir, 'testLargeThread.json')

        # Read the JSON data from testLargeThread.json
        with open(json_file_path, 'r', encoding='utf-8') as f:
            large_thread_data = json.load(f)

        # Assuming 'output' contains the actual data
        # Process the thread
        
        processed_response: ProcessedResponse = await self.processor.process("gmail_users_threads_get", json.dumps(large_thread_data["data"]["output"]))


        # Write processed_documents to a file in order to inspect it later
        with open(os.path.join(current_dir, 'processed_documents.json'), 'w') as f:
            json.dump(processed_response.model_dump(mode='json'), f, indent=4)
        
        # Assertions can vary depending on the structure and content of testLargeThread.json
        # Here, we'll assume that multiple documents are extracted and body contents are pruned

        # 1. Check that documents have been extracted
        self.assertGreater(len(processed_response.processed_response.documents), 0)

        # 2. Check that processed_response contains cleaned data
        self.assertIn("response", processed_response.dict())
        self.assertIn("processed_response", processed_response.dict())
        self.assertIn("documents", processed_response.processed_response.dict())
        self.assertIsInstance(processed_response.processed_response.documents, dict)

        # 3. Additional specific assertions based on testLargeThread.json structure
        # For example, if testLargeThread.json has 5 messages with large bodies:
        # expected_document_keys = ["uuid1", "uuid2", "uuid3", "uuid4", "uuid5"]
        # for key in expected_document_keys:
        #     self.assertIn(key, processed_response.processed_response.documents)
        #     # Verify that the content matches expected values or has been pruned
        #     # Here, we'll just check that the content is a non-empty string
        #     self.assertIsInstance(processed_response.processed_response.documents[key], str)
        #     self.assertTrue(len(processed_response.processed_response.documents[key]) > 0)

    def tearDown(self):
        """
        Clean up after each test method.
        """
        self.processor = None

if __name__ == '__main__':
    unittest.main() 