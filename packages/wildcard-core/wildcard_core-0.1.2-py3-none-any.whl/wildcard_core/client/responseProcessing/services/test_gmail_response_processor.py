import unittest
import json
from wildcard_core.client.responseProcessing.services.GmailResponseProcessor import GmailResponseProcessor

class TestGmailResponseProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = GmailResponseProcessor()
        
        # Sample Gmail message with attachments
        self.sample_message = {
            "id": "12345",
            "threadId": "thread123",
            "payload": {
                "mimeType": "multipart/mixed",
                "parts": [
                    {
                        "mimeType": "text/plain",
                        "body": {
                            "data": "RW1haWwgY29udGVudA==",  # "Email content" in base64
                            "size": 100
                        }
                    },
                    {
                        "mimeType": "application/pdf",
                        "filename": "document.pdf",
                        "body": {
                            "attachmentId": "attachment123",
                            "data": "UERGIGRhdGE=",  # "PDF data" in base64
                            "size": 50000
                        }
                    },
                    {
                        "mimeType": "multipart/alternative",
                        "parts": [
                            {
                                "mimeType": "image/jpeg",
                                "filename": "image.jpg",
                                "body": {
                                    "attachmentId": "attachment456",
                                    "data": "SW1hZ2UgZGF0YQ==",  # "Image data" in base64
                                    "size": 20000
                                }
                            }
                        ]
                    }
                ]
            }
        }
        
        # Sample thread with multiple messages
        self.sample_thread = {
            "id": "thread123",
            "messages": [
                self.sample_message,
                {
                    "id": "67890",
                    "payload": {
                        "mimeType": "multipart/mixed",
                        "parts": [
                            {
                                "mimeType": "application/zip",
                                "filename": "archive.zip",
                                "body": {
                                    "attachmentId": "attachment789",
                                    "data": "WmlwIGRhdGE=",  # "Zip data" in base64
                                    "size": 100000
                                }
                            }
                        ]
                    }
                }
            ]
        }

    def test_process_single_message(self):
        """Test processing a single message with attachments"""
        result = self.processor.process(
            "gmail_users_messages_get",
            json.dumps(self.sample_message)
        )
        
        # Verify attachments were extracted
        self.assertIn("attachments", result.processed_response.data)
        attachments = result.processed_response.data["attachments"]
        self.assertEqual(len(attachments), 2)
        
        # Verify attachment details
        self.assertEqual(attachments[0]["filename"], "document.pdf")
        self.assertEqual(attachments[0]["mime_type"], "application/pdf")
        self.assertEqual(attachments[0]["size"], 50000)
        self.assertEqual(attachments[0]["body"]["data"], "UERGIGRhdGE=")
        
        # Verify nested attachment was found
        self.assertEqual(attachments[1]["filename"], "image.jpg")
        
        # Verify documents contain base64 data
        self.assertEqual(len(result.processed_response.documents), 2)
        self.assertEqual(result.processed_response.documents["document.pdf"], "UERGIGRhdGE=")
        self.assertEqual(result.processed_response.documents["image.jpg"], "SW1hZ2UgZGF0YQ==")
        
        # Verify attachments were removed from response
        remaining_parts = result.response["payload"]["parts"]
        self.assertTrue(all(
            not (part.get("body", {}).get("attachmentId") and part.get("filename"))
            for part in remaining_parts
        ))

    def test_process_thread(self):
        """Test processing a thread with multiple messages containing attachments"""
        result = self.processor.process(
            "gmail_users_threads_get",
            json.dumps(self.sample_thread)
        )
        
        # Verify attachments from all messages were extracted
        self.assertIn("attachments", result.processed_response.data)
        attachments = result.processed_response.data["attachments"]
        print(attachments)
        self.assertEqual(len(attachments), 3)  # Total attachments from all messages
        
        # Verify documents contain base64 data for all attachments
        self.assertEqual(len(result.processed_response.documents), 3)
        self.assertEqual(result.processed_response.documents["document.pdf"], "UERGIGRhdGE=")
        self.assertEqual(result.processed_response.documents["image.jpg"], "SW1hZ2UgZGF0YQ==")
        self.assertEqual(result.processed_response.documents["archive.zip"], "WmlwIGRhdGE=")
        
        # Verify attachments were removed from all messages
        for message in result.response["messages"]:
            if "parts" in message["payload"]:
                parts = message["payload"]["parts"]
                self.assertTrue(all(
                    not (part.get("body", {}).get("attachmentId") and part.get("filename"))
                    for part in parts
                ))

    def test_process_non_gmail_method(self):
        """Test processing a non-Gmail method (should pass through unchanged)"""
        sample_data = {"key": "value"}
        result = self.processor.process(
            "some_other_method",
            json.dumps(sample_data)
        )
        
        # Verify response wasn't modified
        self.assertEqual(result.response, sample_data)
        # Verify empty documents and data structure is present
        self.assertEqual(result.processed_response.documents, {})
        self.assertEqual(result.processed_response.data, {"response": sample_data})

    @unittest.skip  # Skip this test by default
    def test_custom_gmail_response(self):
        """Test processing a custom Gmail API response string.
        To use:
        1. Remove the @unittest.skip decorator
        2. Replace CUSTOM_RESPONSE with your Gmail API response string
        3. Run the test to see the processed output
        """
        CUSTOM_RESPONSE = """
        {
            "id": "custom123",
            "payload": {
                "parts": [
                    {
                        "mimeType": "application/pdf",
                        "filename": "",
                        "body": {
                            "attachmentId": "att123",
                            "data": "dGVzdCBkYXRh",
                            "size": 1000
                        }
                    }
                ]
            }
        }
        """
        
        result = self.processor.process(
            "gmail_users_messages_get",
            CUSTOM_RESPONSE
        )
        
        # Print the full processed result for inspection
        print("\nProcessed Response:")
        print("===================")
        print("Attachments:")
        for attachment in result.processed_response.data.get("attachments", []):
            print(f"\nFilename: {attachment['filename']}")
            print(f"MIME Type: {attachment['mime_type']}")
            print(f"Size: {attachment['size']}")
            if 'attachment_id' in attachment:
                print(f"Attachment ID: {attachment['attachment_id']}")
        
        print("\nDocuments:")
        for filename, data in result.processed_response.documents.items():
            print(f"\n{filename}: {data}")

if __name__ == '__main__':
    unittest.main() 