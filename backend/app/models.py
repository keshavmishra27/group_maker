from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime, timezone


class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)

    domains = relationship(
        "Domain",
        secondary="member_domains",
        back_populates="members"
    )


class Domain(Base):
    __tablename__ = "domains"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)

    members = relationship(
        "Member",
        secondary="member_domains",
        back_populates="domains"
    )


class MemberDomain(Base):
    __tablename__ = "member_domains"

    member_id = Column(Integer, ForeignKey("members.id"), primary_key=True)
    domain_id = Column(Integer, ForeignKey("domains.id"), primary_key=True)


class AssessmentSession(Base):
    __tablename__ = "assessment_sessions"

    id            = Column(Integer, primary_key=True, index=True)
    student_name  = Column(String, nullable=False)
    domains       = Column(JSON, nullable=False, default=list)  # ["AI", "Web Dev"]
    transcript    = Column(JSON, nullable=False, default=list)  # [{role, content}, ...]
    scores        = Column(JSON, nullable=True)                 # {domain_knowledge, creativity, ...}
    status        = Column(String, default="active")           # "active" | "scored"
    created_at    = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at  = Column(DateTime, nullable=True)
