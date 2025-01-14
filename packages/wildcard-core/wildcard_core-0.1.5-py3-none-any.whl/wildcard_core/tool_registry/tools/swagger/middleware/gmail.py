from typing import List, Dict, Any, Callable, Literal, Tuple
import base64
from .base import SwaggerMiddleware

class FromEmailInfo:
    name: str
    email: str

class FromMe:
    email: Literal["me"]

class ToEmailInfo:
    name: str
    email: str

class RecipientInfo:
    To: List[ToEmailInfo]
    Cc: List[ToEmailInfo]
    Bcc: List[ToEmailInfo]

class HandlerGroup:
    """Group of before and after handlers for an operation."""
    def __init__(self, before: List[Callable] = None, after: List[Callable] = None):
        self.before: List[Callable] = before or []
        self.after: List[Callable] = after or []

class WildcardEmailMessage:
    headers: Dict[str, Any]
    body: str

    def __init__(self):
        self.headers = {}
        self.body = ""

    def to_bytes(self) -> bytes:
        string_message = ""
        for header, value in self.headers.items():
            string_message += f"{header}: {value}\n"
        string_message += f'\n' + self.body
        return string_message.encode()

    def set_content(self, content: str):
        self.body = content

    def add_header(self, header: str, value: str):
        self.headers[header] = value

    def to_base64(self) -> str:
        return base64.urlsafe_b64encode(self.to_bytes()).decode()

class GmailMiddleware(SwaggerMiddleware):
    """Middleware for handling Gmail-specific operations."""
    
    def __init__(self):
        # Map operation IDs to their handler groups
        self._operation_handlers: Dict[str, HandlerGroup] = {
            "gmail_users_messages_send": HandlerGroup(before=[self._handle_send_message]),
            "gmail_users_messages_list": HandlerGroup(before=[self._handle_list_messages]),
            "gmail_users_drafts_list": HandlerGroup(before=[self._handle_list_drafts]),
            "gmail_users_drafts_create": HandlerGroup(before=[self._handle_create_draft])
        }

    async def before_execute(self, operationId: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Pre-process Gmail API calls."""
        handler_group = self._operation_handlers.get(operationId)
        if handler_group:
            for handler in handler_group.before:
                kwargs = await handler(kwargs)
        return kwargs
    
    async def after_execute(self, operationId: str, result: Any) -> Any:
        """Post-process Gmail API responses."""
        handler_group = self._operation_handlers.get(operationId)
        if handler_group:
            for handler in handler_group.after:
                result = await handler(result)
        return result

    async def _handle_send_message(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Handle gmail_users_messages_send operation."""
        rfc_message = kwargs.get("RFCMessage")
        from_info = rfc_message.get("From")
        recipients = rfc_message.get("Recipients", RecipientInfo())
        subject = rfc_message.get("Subject")
        message_content = rfc_message.get("Body")
        in_reply_to = rfc_message.get("In-Reply-To")
        references = rfc_message.get("References")

        raw = create_rfc_2822_message(
            from_info=from_info,
            recipients=recipients,
            subject=subject,
            message_content=message_content,
            in_reply_to=in_reply_to,
            references=references
        )

        message = {"raw": raw}

        # Convert the EmailMessage object to a dict and merge it into kwargs
        # This updates the kwargs dictionary with the formatted email message data
        # that will be sent to the Gmail API
        kwargs.update(message)

        del kwargs["RFCMessage"]

        return kwargs

    async def _handle_list_messages(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Handle gmail_users_messages_list operation."""
        # Add any pre-processing for listing messages
        # For example, setting default values, formatting parameters, etc.
        if "maxResults" not in kwargs:
            kwargs["maxResults"] = 10
        return kwargs

    async def _handle_list_drafts(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Handle gmail_users_drafts_list operation."""
        # Add any pre-processing for listing drafts
        if "userId" not in kwargs:
            kwargs["userId"] = "me"
        return kwargs

    async def _handle_create_draft(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Handle gmail_users_drafts_create operation."""
        # Add any pre-processing for creating drafts
        rfc_message = kwargs.get("message").get("RFCMessage")
        from_info = rfc_message.get("From")
        recipients = rfc_message.get("Recipients", RecipientInfo())
        subject = rfc_message.get("Subject")
        message_content = rfc_message.get("Body")
        in_reply_to = rfc_message.get("In-Reply-To")
        references = rfc_message.get("References")

        raw = create_rfc_2822_message(
            from_info=from_info,
            recipients=recipients,
            subject=subject,
            message_content=message_content,
            in_reply_to=in_reply_to,
            references=references
        )
        message = {"message": { "raw": raw }}
        # Convert the EmailMessage object to a dict and merge it into kwargs
        # This updates the kwargs dictionary with the formatted email message data
        # that will be sent to the Gmail API
        kwargs.update(message)

        # del kwargs["RFCMessage"]

        return kwargs

def create_rfc_2822_message(from_info: FromEmailInfo | FromMe, recipients: RecipientInfo, subject: str, message_content: str, in_reply_to: str, references: List[str]) -> Dict[str, Any]:
    """
    Create an RFC 2822 formatted email message.
    """
    def process_to_emails(recipients: RecipientInfo) -> Tuple[str, str, str]:

        recipient_strs = {
            "To": "",
            "Cc": "",
            "Bcc": ""
        }
        
        if recipients is None:
            return "", "", ""
        for recipient_type in ["To", "Cc", "Bcc"]:
            if recipient_type in recipients:
                for recipient in recipients[recipient_type]:
                    recipient = f"{recipient.get('name', '')} <{recipient.get('email', '')}>"
                    recipient_strs[recipient_type] = recipient_strs[recipient_type] + ', ' + recipient if recipient_strs[recipient_type] else recipient
        return recipient_strs["To"], recipient_strs["Cc"], recipient_strs["Bcc"]

    message = WildcardEmailMessage()
    if isinstance(from_info, FromEmailInfo):
        message.add_header('From', f"{from_info.get('name')} <{from_info.get('email')}>")
    elif isinstance(from_info, FromMe):
        message.add_header('From', "me")

    to_str, cc_str, bcc_str = process_to_emails(recipients)
    if to_str:
        message.add_header('To', to_str)
    if cc_str:
        message.add_header('Cc', cc_str)
    if bcc_str:
        message.add_header('Bcc', bcc_str)

    if in_reply_to:
        message.add_header('In-Reply-To', in_reply_to)

    if references:
        message.add_header('References', str.join(" ", references))
    
    message.add_header('Subject', subject)
    message.set_content(message_content)

    return message.to_base64()
