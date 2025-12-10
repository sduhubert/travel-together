import datetime
import enum
from typing import List, Optional, Set

import flask_login
from sqlalchemy import String, DateTime, ForeignKey, Boolean, Integer, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func


from . import db
    
class TripProposalParticipation(db.Model):
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
    trip_proposal_id: Mapped[int] = mapped_column(ForeignKey("trip_proposal.id", ondelete="CASCADE"), primary_key=True)
    is_editor: Mapped[bool] = mapped_column(Boolean, default=False)
    
class TripProposalMessage(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    trip_proposal_id: Mapped[int] = mapped_column(ForeignKey("trip_proposal.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="SET NULL"))
    user: Mapped["User"] = relationship("User")
    forum_topic: Mapped[str] = mapped_column(String(64), default="Main")
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
    birthday: Mapped[datetime.date] = mapped_column(Date)
    home_uni: Mapped[str] = mapped_column(String(128))
    visiting_uni: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    country: Mapped[str] = mapped_column(String(2))
    profile_pic: Mapped[str] = mapped_column(String(256))
    trip_proposals: Mapped[Set["TripProposal"]] = relationship("TripProposal", secondary="trip_proposal_participation", back_populates="participants")

    @property
    def age(user):
        today = datetime.date.today()
        return(today.year - user.birthday.year - ((today.month, today.day) < (user.birthday.month, user.birthday.day)))
    
    def is_editor_for(self, trip):
        participation = db.session.scalar(
            db.select(TripProposalParticipation.is_editor).where(
                TripProposalParticipation.user_id == self.id,
                TripProposalParticipation.trip_proposal_id == trip.id
            )
        )
        return bool(participation)
    
    def has_pending_request_for(self, trip):
        pending_request = db.session.scalar(
            db.select(func.count()).select_from(TripProposalJoinRequest).where(
                TripProposalJoinRequest.user_id == self.id,
                TripProposalJoinRequest.trip_proposal_id == trip.id
            )
        )
        return pending_request > 0
    
class TripProposalStatus(enum.Enum):
    OPEN = 0
    APPROVAL_REQUIRED = 1
    CLOSED = 2
    FINALIZED = 3
    CANCELLED = 4

class TripSexPreference(enum.Enum):
    FEMALE = 0
    MALE = 1
    
class TripProposalJoinRequest(db.Model):
    trip_proposal_id: Mapped[int] = mapped_column(ForeignKey("trip_proposal.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
    timestamp: Mapped[datetime.datetime] = mapped_column(
        # pylint: disable=not-callable
        DateTime(timezone=True), server_default=func.now()
    )
    
class TripProposal(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="SET NULL"))
    creator: Mapped["User"] = relationship("User")
    participants: Mapped[Set["User"]] = relationship("User", secondary="trip_proposal_participation", back_populates="trip_proposals")
    messages: Mapped[List["TripProposalMessage"]] = relationship("TripProposalMessage", backref="trip", order_by="TripProposalMessage.timestamp.asc()")
    title: Mapped[str] = mapped_column(String(128))
    description: Mapped[str] = mapped_column(String(512))
    origin: Mapped[str] = mapped_column(String(128))
    destinations: Mapped[str] = mapped_column(String(512))  # Comma-separated list
    start_date: Mapped[datetime.date] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[datetime.date] = mapped_column(DateTime(timezone=True))
    budget: Mapped[Optional[int]] = mapped_column(Integer) # in EUR
    max_travelers: Mapped[Optional[int]] = mapped_column(Integer)
    min_age: Mapped[Optional[int]] = mapped_column(Integer)
    max_age: Mapped[Optional[int]] = mapped_column(Integer)
    university: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    status: Mapped["TripProposalStatus"] = mapped_column(Integer)  # Use TripProposalStatus enum values
    image: Mapped[str] = mapped_column(String(256))
    timestamp: Mapped[datetime.datetime] = mapped_column(
        # pylint: disable=not-callable
        DateTime(timezone=True), server_default=func.now()
    )
    origin_finalized: Mapped[bool] = mapped_column(Boolean, default=False)
    destinations_finalized: Mapped[bool] = mapped_column(Boolean, default=False)
    dates_finalized: Mapped[bool] = mapped_column(Boolean, default=False)
    budget_finalized: Mapped[bool] = mapped_column(Boolean, default=False)
    max_travelers_finalized: Mapped[bool] = mapped_column(Boolean, default=False)
    age_range_finalized: Mapped[bool] = mapped_column(Boolean, default=False)
    university_finalized: Mapped[bool] = mapped_column(Boolean, default=False)
    
    def num_editors(self):
        return db.session.scalar(
            db.select(func.count()).select_from(TripProposalParticipation).where(
                TripProposalParticipation.trip_proposal_id == self.id,
                TripProposalParticipation.is_editor == True
            )
        )
    
class Meetup(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    trip_proposal_id: Mapped[int] = mapped_column(ForeignKey("trip_proposal.id", ondelete="CASCADE"))
    creator_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="SET NULL"))
    location: Mapped[str] = mapped_column(String(128))
    date_time: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))
    description: Mapped[Optional[str]] = mapped_column(String(512))
    link: Mapped[Optional[str]] = mapped_column(String(256))
    trip = relationship('TripProposal', backref='meetups')
    creator = relationship('User', backref='created_meetups')