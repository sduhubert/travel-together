import datetime
import enum
from typing import List, Optional, Set

import flask_login
from sqlalchemy import String, DateTime, ForeignKey, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from . import db

class FollowingAssociation(db.Model):
    follower_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    followed_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    
class TripProposalParticipation(db.Model):
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    trip_proposal_id: Mapped[int] = mapped_column(ForeignKey("trip_proposal.id"), primary_key=True)
    is_editor: Mapped[bool] = mapped_column(Boolean, default=False)
    
class TripProposalMessage(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    trip_proposal_id: Mapped[int] = mapped_column(ForeignKey("trip_proposal.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    content: Mapped[str] = mapped_column(String(512))
    timestamp: Mapped[datetime.datetime] = mapped_column(
        # pylint: disable=not-callable
        DateTime(timezone=True), server_default=func.now()
    )

class User(flask_login.UserMixin, db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(128), unique=True)
    name: Mapped[str] = mapped_column(String(64))
    password: Mapped[str] = mapped_column(String(256))
    desc: Mapped[Optional[str]] = mapped_column(String(512))
    trip_proposals: Mapped[Set["TripProposal"]] = relationship("TripProposal", secondary="trip_proposal_participation", back_populates="participants")
    # following: Mapped[List["User"]] = relationship(
    #     secondary=FollowingAssociation.__table__,
    #     primaryjoin=FollowingAssociation.follower_id == id,
    #     secondaryjoin=FollowingAssociation.followed_id == id,
    #     back_populates="followers",
    # )
    # followers: Mapped[List["User"]] = relationship(
    #     secondary=FollowingAssociation.__table__,
    #     primaryjoin=FollowingAssociation.followed_id == id,
    #     secondaryjoin=FollowingAssociation.follower_id == id,
    #     back_populates="following",
    # )
    
class TripProposalStatus(enum.Enum):
    OPEN = 0
    CLOSED = 1
    FINALIZED = 2
    CANCELLED = 3   
    
class TripProposal(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    participants: Mapped[Set["User"]] = relationship("User", secondary="trip_proposal_participation", back_populates="trip_proposals")
    title: Mapped[str] = mapped_column(String(128))
    description: Mapped[str] = mapped_column(String(512))
    origin: Mapped[str] = mapped_column(String(128))
    destinations: Mapped[Set[str]] = mapped_column(String(512))  # Comma-separated list
    start_date: Mapped[datetime.date] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[datetime.date] = mapped_column(DateTime(timezone=True))
    length: Mapped[int] = mapped_column(Integer)  # in days
    max_travelers: Mapped[int] = mapped_column(Integer)
    budget: Mapped[int] = mapped_column(Integer) # in EUR
    activities: Mapped[Set[str]] = mapped_column(String(512))  # Comma-separated list
    status: Mapped["TripProposalStatus"] = mapped_column(Integer)  # Use TripProposalStatus enum values
    timestamp: Mapped[datetime.datetime] = mapped_column(
        # pylint: disable=not-callable
        DateTime(timezone=True), server_default=func.now()
    )
    origin_finalized: Mapped[bool] = mapped_column(Boolean, default=False)
    destinations_finalized: Mapped[bool] = mapped_column(Boolean, default=False)
    dates_finalized: Mapped[bool] = mapped_column(Boolean, default=False)
    budget_finalized: Mapped[bool] = mapped_column(Boolean, default=False)
    activities_finalized: Mapped[bool] = mapped_column(Boolean, default=False)
    status_finalized: Mapped[bool] = mapped_column(Boolean, default=False)
    
class Meetup(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    trip_proposal_id: Mapped[int] = mapped_column(ForeignKey("trip_proposal.id"))
    creator_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    location: Mapped[str] = mapped_column(String(128))
    date_time: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))
    description: Mapped[Optional[str]] = mapped_column(String(512))