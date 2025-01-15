from typing import Any, Dict, List
from dataclasses import dataclass, field
from datetime import timedelta


@dataclass
class CORS_config:
    name: str
    origins: List[str] = field(default_factory=lambda: ["*"])
    methods: List[str] = field(default_factory=lambda: ["GET", "OPTIONS"])
    allow_headers: List[str] = field(default_factory=lambda: ["Content-Type"])
    expose_headers: List[str] = field(default_factory=list)
    supports_credentials: bool = False
    max_age: timedelta = field(default_factory=lambda: timedelta(minutes=30))
    vary_header: bool = True
    automatic_options: bool = True
    send_wildcard: bool = False
    always_send: bool = True
    header_values: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        self.header_values.setdefault("X-XSS-Protection", "1; mode=block")
        self.header_values.setdefault("X-Frame-Options", "SAMEORIGIN")
        self.header_values.setdefault("X-Content-Type-Options", "nosniff")
        self.header_values.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "origins": self.origins,
            "methods": self.methods,
            "allow_headers": self.allow_headers,
            "expose_headers": self.expose_headers,
            "supports_credentials": self.supports_credentials,
            "max_age": self.max_age.total_seconds(),
            "vary_header": self.vary_header,
            "automatic_options": self.automatic_options,
            "send_wildcard": self.send_wildcard,
            "always_send": self.always_send
        }