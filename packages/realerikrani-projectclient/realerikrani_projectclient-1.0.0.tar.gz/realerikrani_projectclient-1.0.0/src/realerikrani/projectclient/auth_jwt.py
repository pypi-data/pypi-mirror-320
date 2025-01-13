from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
from requests import PreparedRequest
from requests.auth import AuthBase


@dataclass
class JWTAuth(AuthBase):
    project_id: UUID
    kid: UUID
    private_key: str
    token: str = field(init=False)
    expiration_time: datetime = field(init=False)

    def __post_init__(self) -> None:
        self.expiration_time = self.get_expiration_time()
        self.token = self.create_jwt()

    def create_jwt(self) -> str:
        """Create a new JWT token."""
        return jwt.encode(
            payload={
                "iat": datetime.now(tz=UTC),
                "exp": self.expiration_time,
                "iss": str(self.project_id),
            },
            key=self.private_key,
            algorithm="RS256",
            headers={"kid": str(self.kid)},
        )

    def get_expiration_time(self) -> datetime:
        """Get the expiration time of the current token."""
        return datetime.now(tz=UTC) + timedelta(minutes=5)

    def renew_token(self) -> None:
        """Renew the JWT token if it has expired."""
        if datetime.now(tz=UTC) >= self.expiration_time:
            self.token = self.create_jwt()
            self.expiration_time = self.get_expiration_time()

    def update_credentials(self, project_id: UUID, kid: UUID) -> None:
        """Update project_id and kid, and renew the token."""
        self.project_id = project_id
        self.kid = kid
        self.expiration_time = self.get_expiration_time()  # Reset expiration time
        self.token = self.create_jwt()  # Regenerate the token

    def __call__(self, r: PreparedRequest) -> PreparedRequest:
        """Attach the JWT token to the request."""
        self.renew_token()  # Check and renew the token if necessary
        r.headers["Authorization"] = f"Bearer {self.token}"
        return r
