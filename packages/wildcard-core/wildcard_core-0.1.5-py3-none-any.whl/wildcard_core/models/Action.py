from enum import Enum
from pydantic import BaseModel
from .api_service import APIService
from typing import Union, List

class Action(BaseModel):
    
    @staticmethod
    def get_random_action_by_api_service(api_service: APIService) -> str:
        """
        Get a random action for a given API service
        TODO: This is a workaround to get OAuth info for a given API service
        """
        actions = Action.from_api_service(api_service)
        return actions[0]
        
    @staticmethod
    def from_string(action_string: str) -> 'ActionType':
        """
        Resolve an Action enum instance from a string identifier.
        e.g. gmail_threads_list
        """
        # Get all enum classes defined within Action
        service_enums = [v for k, v in Action.__dict__.items() 
                        if isinstance(v, type) and issubclass(v, Enum)]
        
        # Try matching against each service's actions
        for service_enum in service_enums:
            try:
                return service_enum(action_string)
            except ValueError:
                continue
            
        raise ValueError(f"Unknown action: {action_string}")

    @staticmethod 
    def from_enum_name(enum_name: str) -> 'ActionType':
        """
        Resolve an Action enum instance from an enum name.
        e.g. Gmail.DRAFTS_LIST
        """
        try:
            service_name, action_name = enum_name.split('.')
            service_enum = getattr(Action, service_name)
            return getattr(service_enum, action_name)
        except (AttributeError, ValueError):
            raise ValueError(f"Invalid enum name format: {enum_name}. Expected format: Service.ACTION_NAME OR the specified enum is not found")
        
    @staticmethod
    def from_api_service(api_service: APIService) -> List[str]:
        """
        Get all actions for a given API service
        """
        actions = []
        for attr in Action.__dict__.values():
            if isinstance(attr, type) and issubclass(attr, Enum):
                actions.extend([action.value for action in attr if action.get_api_service() == api_service])
        return actions
    
    class BraveSearch(str, Enum):
        def get_api_service(self) -> APIService:
            return APIService.BRAVE_SEARCH
        SEARCH = "brave_search_get_web_search_results"
        """Search for information using Brave Search."""
    
    class Airtable(str, Enum):
        def get_api_service(self) -> APIService:
            return APIService.AIRTABLE
        GET_USER_INFO = "airtable_get_user_info"
        """Retrieve information about the user's Airtable account."""
        RECORDS_LIST = "airtable_records_list"
        """Retrieve a list of all records in a table."""
        RECORDS_UPDATE_MULTIPLE = "airtable_records_update_multiple"
        """Update multiple records in a table."""
        RECORDS_REPLACE_MULTIPLE = "airtable_records_replace_multiple"
        """Replace multiple records in a table."""
        RECORDS_CREATE = "airtable_records_create"
        """Create a new record in a table."""
        RECORDS_DELETE_MULTIPLE = "airtable_records_delete_multiple"
        """Delete multiple records from a table."""
        RECORDS_GET = "airtable_records_get"
        """Retrieve a specific record from a table."""
        RECORDS_REPLACE = "airtable_records_replace"
        """Replace a specific record in a table."""
        RECORDS_UPDATE = "airtable_records_update"
        """Update a specific record in a table."""
        RECORDS_DELETE = "airtable_records_delete"
        """Delete a specific record from a table."""
        RECORDS_SYNC_CSV = "airtable_records_sync_csv"
        """Sync data from a CSV file into a table."""
        RECORDS_UPLOAD_ATTACHMENT = "airtable_records_upload_attachment"
        """Upload an attachment to a record."""
        FIELDS_UPDATE = "airtable_fields_update"
        """Update a specific field in a table."""
        FIELDS_CREATE = "airtable_fields_create"
        """Create a new field in a table."""
        COMMENTS_LIST = "airtable_comments_list"
        """Retrieve a list of all comments on a record."""
        COMMENTS_UPDATE = "airtable_comments_update"
        """Update a specific comment on a record."""
        COMMENTS_CREATE = "airtable_comments_create"
        """Create a new comment on a record."""
        COMMENTS_DELETE = "airtable_comments_delete"
        """Delete a comment from a record."""
        TABLES_UPDATE = "airtable_tables_update"
        """Update a specific table in a base."""
        TABLES_CREATE = "airtable_tables_create"
        """Create a new table in a base."""
        BASES_LIST = "airtable_bases_list"
        """Retrieve a list of all bases in the user's Airtable account."""
        BASES_SCHEMA = "airtable_bases_schema"
        """Retrieve the schema of a base."""
        BASES_CREATE = "airtable_bases_create"
        """Create a new base in the user's Airtable account."""
        WEBHOOKS_LIST_PAYLOADS = "airtable_webhooks_list_payloads"
        """Retrieve a list of all webhooks in a base."""
        WEBHOOKS_LIST = "airtable_webhooks_list"
        """Retrieve a list of all webhooks in a base."""
        WEBHOOKS_CREATE = "airtable_webhooks_create"
        """Create a new webhook in a base."""
        WEBHOOKS_DELETE = "airtable_webhooks_delete"
        """Delete a webhook from a base."""
        WEBHOOKS_ENABLE_NOTIFICATIONS = "airtable_webhooks_enable_notifications"
        """Enable notifications for a webhook."""
        WEBHOOKS_REFRESH = "airtable_webhooks_refresh"
        """Refresh a webhook."""
        VIEWS_LIST = "airtable_views_list"
        """Retrieve a list of all views in a base."""
        VIEWS_GET_METADATA = "airtable_views_get"
        """Retrieve a specific view metadatafrom a base."""
        VIEWS_DELETE = "airtable_views_delete"
        """Delete a view from a base."""


    class Gmail(str, Enum):
        def get_api_service(self) -> APIService:
            return APIService.GMAIL
            
        DRAFTS_LIST = "gmail_users_drafts_list"
        """Retrieve a list of all email drafts in the user's Gmail account. This endpoint allows you to access drafts that are saved but not yet sent, providing an overview of unsent messages."""
        DRAFTS_CREATE = "gmail_users_drafts_create"
        """Creates a new email draft in the user's Gmail account. This draft is labeled as 'DRAFT' and can be edited or sent later. It allows users to save a message they are composing without sending it immediately."""
        DRAFTS_SEND = "gmail_users_drafts_send"
        """Sends the existing draft to the specified recipients. This endpoint finalizes the draft and delivers it to the email addresses listed in the 'To', 'Cc', and 'Bcc' fields."""
        DRAFTS_DELETE = "gmail_users_drafts_delete"
        """Permanently deletes the specified draft from the user's Gmail account. This action cannot be undone."""
        DRAFTS_GET = "gmail_users_drafts_get"
        """Retrieves the details of a specific email draft by its ID. This includes information such as the draft's subject, recipients, and content."""
        DRAFTS_UPDATE = "gmail_users_drafts_update"
        """Updates the content of an existing email draft. This endpoint replaces the current draft content with new information, allowing for modifications before sending."""

        HISTORY_LIST = "gmail_users_history_list"
        """Retrieve a chronological list of changes made to the user's Gmail account. This includes modifications to messages, labels, and other mailbox activities, providing a history of actions."""

        LABELS_LIST = "gmail_users_labels_list"
        """Retrieve a list of all labels associated with the user's Gmail account. Labels help organize emails and can be used to categorize messages for easier management."""
        LABELS_CREATE = "gmail_users_labels_create"
        """Create a new label in the user's Gmail account. Labels are used to categorize and organize emails, making it easier to manage and find messages."""
        LABELS_DELETE = "gmail_users_labels_delete"
        """Permanently delete a specific label from the user's Gmail account. This action removes the label from all messages and threads it was applied to."""
        LABELS_GET = "gmail_users_labels_get"
        """Retrieve the details of a specific label by its ID. This includes information such as the label's name and its associated settings."""
        LABELS_PATCH = "gmail_users_labels_patch"
        """Partially update the specified label. This method supports patch semantics."""
        LABELS_UPDATE = "gmail_users_labels_update"
        """Updates the specified label. This method replaces the current label settings with the new values provided."""

        MESSAGES_LIST = "gmail_users_messages_list"
        """Retrieve a list of messages in the user's mailbox. This endpoint allows you to access all messages, including those in the trash, providing a comprehensive view of the user's email history."""
        MESSAGES_INSERT = "gmail_users_messages_insert"
        """Imports a message into only this user's mailbox, with standard email delivery scanning and classification similar to receiving via SMTP. This method doesn't perform SPF checks, so it might not work for some spam messages, such as those attempting to perform domain spoofing. This method does not send a message."""
        MESSAGES_BATCH_DELETE = "gmail_users_messages_batchDelete"
        """Deletes many messages by message ID. Provides no guarantees that messages were not already deleted or even existed at all."""
        MESSAGES_BATCH_MODIFY = "gmail_users_messages_batchModify"
        """Modifies the labels on the specified messages."""
        MESSAGES_IMPORT = "gmail_users_messages_import"
        """Directly inserts a message into only this user's mailbox similar to `IMAP APPEND`, bypassing most scanning and classification. Does not send a message."""
        MESSAGES_SEND = "gmail_users_messages_send"
        """Sends the specified message to the recipients in the `To`, `Cc`, and `Bcc` headers. For example usage, see [Sending email](https://developers.google.com/gmail/api/guides/sending)."""
        MESSAGES_DELETE = "gmail_users_messages_delete"
        """Immediately and permanently deletes the specified message. This operation cannot be undone."""
        MESSAGES_GET = "gmail_users_messages_get"
        """Gets the specified message."""
        MESSAGES_MODIFY = "gmail_users_messages_modify"
        """Modifies the labels on the specified message."""
        MESSAGES_TRASH = "gmail_users_messages_trash"
        """Moves the specified message to the trash."""
        MESSAGES_UNTRASH = "gmail_users_messages_untrash"
        """Removes the specified message from the trash."""
        MESSAGES_ATTACHMENTS_GET = "gmail_users_messages_attachments_get"
        """Gets the specified message attachment."""

        GET_PROFILE = "gmail_users_getProfile"
        """Gets the current user's Gmail profile."""

        SETTINGS_GET_AUTO_FORWARDING = "gmail_users_settings_getAutoForwarding"
        """Gets the auto-forwarding setting for the specified account."""
        SETTINGS_UPDATE_AUTO_FORWARDING = "gmail_users_settings_updateAutoForwarding"
        """Updates the auto-forwarding setting for the specified account."""

        SETTINGS_GET_VACATION = "gmail_users_settings_getVacation"
        """Retrieve the current vacation responder settings for a Gmail account.
        The vacation responder automatically replies to incoming emails with a specified
        message when enabled."""
        SETTINGS_UPDATE_VACATION = "gmail_users_settings_updateVacation"
        """Update the vacation responder settings for a Gmail account. This
        includes setting the message, start and end dates, and whether the responder
        is active."""

        STOP = "gmail_users_stop"
        """Stop receiving push notifications for the given user mailbox."""

        THREADS_LIST = "gmail_users_threads_list"
        """Lists the threads in the user's mailbox."""
        THREADS_DELETE = "gmail_users_threads_delete"
        """Immediately and permanently deletes the specified thread. Any message that belongs to the thread is also deleted. This operation cannot be undone. Prefer `threads.trash` instead."""
        THREADS_GET = "gmail_users_threads_get"
        """Gets the specified thread."""
        THREADS_MODIFY = "gmail_users_threads_modify"
        """Modifies the labels on the specified thread. This applies to all messages in the thread."""
        THREADS_TRASH = "gmail_users_threads_trash"
        """Moves the specified thread to the trash. Any message that belongs to the thread is also moved to the trash."""
        THREADS_UNTRASH = "gmail_users_threads_untrash"
        """Removes the specified thread from the trash. Any message that belongs to the thread is also removed from the trash."""

        WATCH = "gmail_users_watch"
        """Set up or update push notification watch for the given user mailbox."""
        
    class Shopify(str, Enum):
        def get_api_service(self) -> APIService:
            return APIService.SHOPIFY
        
        GET_PRODUCTS = "shopify_product_get"
        """Retrieve a list of all products in the user's Shopify account."""
        UPDATE_PRODUCT = "shopify_product_update"
        """Update a specific product in the user's Shopify account."""

ActionType = Union[Action.Airtable, Action.Gmail]

