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
    birthday: Mapped[datetime.date] = mapped_column(DateTime(timezone=True))
    #sex: Mapped[Optional["TripSexPreference"]] = mapped_column(Integer) # Use SexPreference enum values
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
    APPROVAL_REQUIRED = 1
    CLOSED = 2
    FINALIZED = 3
    CANCELLED = 4

class TripSexPreference(enum.Enum):
    FEMALE = 0
    MALE = 1
    
class TripProposal(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    creator: Mapped["User"] = relationship("User")
    participants: Mapped[Set["User"]] = relationship("User", secondary="trip_proposal_participation", back_populates="trip_proposals")
    title: Mapped[str] = mapped_column(String(128))
    description: Mapped[str] = mapped_column(String(512))
    response_to_id: Mapped[int] = mapped_column(Integer)
    origin: Mapped[str] = mapped_column(String(128))
    destinations: Mapped[str] = mapped_column(String(512))  # Comma-separated list
    start_date: Mapped[datetime.date] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[datetime.date] = mapped_column(DateTime(timezone=True))
    budget: Mapped[Optional[int]] = mapped_column(Integer) # in EUR
    max_travelers: Mapped[Optional[int]] = mapped_column(Integer)
    sex_preference: Mapped[Optional["TripSexPreference"]] = mapped_column(Integer) # Use SexPreference enum values
    activities: Mapped[Optional[str]] = mapped_column(String(512))  # Comma-separated list
    min_age: Mapped[Optional[int]] = mapped_column(Integer)
    max_age: Mapped[Optional[int]] = mapped_column(Integer)
    status: Mapped["TripProposalStatus"] = mapped_column(Integer)  # Use TripProposalStatus enum values
    timestamp: Mapped[datetime.datetime] = mapped_column(
        # pylint: disable=not-callable
        DateTime(timezone=True), server_default=func.now()
    )
    origin_finalized: Mapped[bool] = mapped_column(Boolean, default=False)
    destinations_finalized: Mapped[bool] = mapped_column(Boolean, default=False)
    dates_finalized: Mapped[bool] = mapped_column(Boolean, default=False)
    budget_finalized: Mapped[bool] = mapped_column(Boolean, default=False)
    max_travelers_finalized: Mapped[bool] = mapped_column(Boolean, default=False)
    sex_preference_finalized: Mapped[bool] = mapped_column(Boolean, default=False)
    activities_finalized: Mapped[bool] = mapped_column(Boolean, default=False)
    age_range_finalized: Mapped[bool] = mapped_column(Boolean, default=False)
    status_finalized: Mapped[bool] = mapped_column(Boolean, default=False)
    
class Meetup(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    trip_proposal_id: Mapped[int] = mapped_column(ForeignKey("trip_proposal.id"))
    creator_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    location: Mapped[str] = mapped_column(String(128))
    date_time: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))
    description: Mapped[Optional[str]] = mapped_column(String(512))