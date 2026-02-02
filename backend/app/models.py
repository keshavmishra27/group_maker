from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


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
