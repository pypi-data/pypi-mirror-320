from __future__ import annotations

import email
import imaplib
import os
import re
from datetime import datetime
from threading import Lock, Thread
from time import sleep
from typing import Callable, Dict, List, Optional, Union

from arkaine.toolbox.email import EmailSender
from arkaine.tools import Tool
from arkaine.utils.interval import Interval


class EmailMessage:
    """Represents a received email message."""

    def __init__(
        self,
        subject: str,
        sender: str,
        body: str,
        received_at: datetime,
        message_id: str,
    ):
        self.subject = subject
        self.sender = sender
        self.body = body
        self.received_at = received_at
        self.message_id = message_id

    def __str__(self):
        return f"From: {self.sender}\nSubject: {self.subject}\nDate: {self.received_at}"

    @staticmethod
    def from_message(msg: email.message.Message) -> EmailMessage:
        """Create EmailMessage from email.message.Message object."""
        subject = msg.get("subject", "")
        sender = msg.get("from", "")
        received_at = email.utils.parsedate_to_datetime(msg.get("date"))
        message_id = msg.get("message-id", "")

        # Extract body (handle both plain text and HTML)
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() in ["text/plain", "text/html"]:
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = msg.get_payload(decode=True).decode()

        return EmailMessage(
            subject=subject,
            sender=sender,
            body=body,
            received_at=received_at,
            message_id=message_id,
        )


class Inbox:
    """
    Monitors incoming emails and triggers tools when matching emails are found.

    Basic usage:
    ```python
    # Create monitor checking every 5 minutes
    inbox = Inbox(
        username="user@example.com",
        password="pass",
        service="gmail",
        check_every="5:minutes"
    )

    # Add filter and associated tools
    inbox.add_filter(
        EmailFilter(subject_pattern="Important:.*"),
        tools=[notification_tool]
    )

    # Start monitoring
    inbox.start()

    # Add another filter while running
    inbox.add_filter(
        EmailFilter(sender_pattern="boss@company.com"),
        tools=[urgent_tool]
    )

    # Stop monitoring
    inbox.stop()
    ```
    """

    # Common IMAP servers
    COMMON_IMAP_SERVERS = {
        "gmail": "imap.gmail.com",
        "outlook": "outlook.office365.com",
        "yahoo": "imap.mail.yahoo.com",
        "aol": "imap.aol.com",
        "icloud": "imap.mail.me.com",
    }

    def __init__(
        self,
        tools: List[Tool],
        filters: List[Callable[[EmailMessage], bool]],
        username: Optional[Union[str, dict]] = None,
        password: Optional[Union[str, dict]] = None,
        service: Optional[str] = None,
        imap_host: Optional[str] = None,
        check_every: Union[str, Interval] = "5:minutes",
        env_prefix: str = "EMAIL",
    ):
        self.username = self._load_credential(
            username, f"{env_prefix}_USERNAME"
        )
        self.password = self._load_credential(
            password, f"{env_prefix}_PASSWORD"
        )

        # Set up IMAP host
        if imap_host:
            self.imap_host = imap_host
        elif service:
            if service not in self.COMMON_IMAP_SERVERS:
                raise ValueError(f"Unknown email service: {service}")
            self.imap_host = self.COMMON_IMAP_SERVERS[service]
        else:
            self.imap_host = os.getenv(f"{env_prefix}_IMAP_HOST")
            if not self.imap_host:
                raise ValueError("IMAP host not provided")

        # Set up interval
        if isinstance(check_every, str):
            self.interval = Interval(datetime.now(), recur_every=check_every)
        else:
            self.interval = check_every

        self.__tools: List[Tool] = tools
        self.__filters: Dict[EmailFilter, List[Tool]] = {}

        self.seen_messages: set = set()

        self.__running = False
        self.__lock = Lock()
        self.__thread = Thread(target=self.__run)
        self.__thread.daemon = True
        self.__thread.start()

    def _load_credential(
        self,
        value: Optional[Union[str, dict]],
        env_var: str,
        required: bool = True,
    ) -> Optional[str]:
        """Load a credential from various sources."""
        if isinstance(value, str):
            return value
        if isinstance(value, dict) and "env" in value:
            value = os.getenv(value["env"])
        else:
            value = os.getenv(env_var)

        if required and not value:
            raise ValueError(
                f"Required credential not provided: direct value, "
                f"dict with 'env', or environment variable {env_var}"
            )
        return value

    def add_tool(self, tool: Tool):
        """Add a tool to the inbox."""
        with self.__lock:
            self.tools.append(tool)

    def add_filter(
        self, email_filter: EmailFilter, tools: Union[Tool, List[Tool]]
    ):
        """Add a new filter and associated tools."""
        if isinstance(tools, Tool):
            tools = [tools]
        with self.__lock:
            self.filters[email_filter] = tools

    def start(self):
        """Start monitoring emails."""
        with self.__lock:
            self.__running = True

    def stop(self):
        """Stop monitoring emails."""
        with self.__lock:
            self.__running = False

    def __check_emails(self):
        """Check for new emails and process them."""
        try:
            with imaplib.IMAP4_SSL(self.imap_host) as imap:
                imap.login(self.username, self.password)
                imap.select("INBOX")

                # Search for all emails from the last check
                _, message_numbers = imap.search(None, "ALL")

                for num in message_numbers[0].split():
                    # Fetch message data
                    _, msg_data = imap.fetch(num, "(RFC822)")
                    email_body = msg_data[0][1]
                    msg = email.message_from_bytes(email_body)

                    # Create EmailMessage object
                    message = EmailMessage.from_message(msg)

                    # Skip if we've seen this message before
                    if message.message_id in self.seen_messages:
                        continue

                    self.seen_messages.add(message.message_id)

                    # Check against filters and trigger tools
                    for email_filter, tools in self.filters.items():
                        if email_filter.matches(message):
                            for tool in tools:
                                tool.async_call(message)

        except Exception as e:
            print(f"Error checking emails: {str(e)}")

    def __run(self):
        """Main monitoring loop."""
        while True:
            with self.__lock:
                if not self.__running:
                    sleep(1.0)
                    continue

                if self.interval.trigger_at <= datetime.now():
                    self.__check_emails()
                    self.interval.trigger()

            sleep(1.0)
