"""SQLAlchemy models for the portability scoring database."""

from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()


class Dimension(Base):
    """A scoring dimension (e.g., API Access, Export Formats)."""
    __tablename__ = "dimensions"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    slug = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    weight = Column(Float, nullable=False)  # 0.0–1.0, all weights sum to 1.0

    scores = relationship("Score", back_populates="dimension")


class Platform(Base):
    """A manufacturing software platform being scored."""
    __tablename__ = "platforms"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    slug = Column(String(200), nullable=False, unique=True)
    vendor = Column(String(200))
    category = Column(String(100))  # MES, MOM, OEE, IIoT, SCADA, etc.
    website = Column(String(500))
    description = Column(Text)
    notes = Column(Text)  # internal research notes

    scores = relationship("Score", back_populates="platform", cascade="all, delete-orphan")
    reports = relationship("UserReport", back_populates="platform", cascade="all, delete-orphan")

    @property
    def overall_score(self):
        """Weighted overall portability score (0–10)."""
        if not self.scores:
            return 0.0
        total = sum(s.value * s.dimension.weight for s in self.scores if s.dimension)
        return round(total, 1)

    @property
    def score_dict(self):
        """Dimension slug -> score value."""
        return {s.dimension.slug: s.value for s in self.scores if s.dimension}

    def to_dict(self, include_scores=False):
        d = {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "vendor": self.vendor,
            "category": self.category,
            "website": self.website,
            "description": self.description,
            "overall_score": self.overall_score,
        }
        if include_scores:
            d["scores"] = {
                s.dimension.slug: {
                    "dimension": s.dimension.name,
                    "value": s.value,
                    "notes": s.notes,
                }
                for s in self.scores if s.dimension
            }
        return d


class Score(Base):
    """A platform's score on a single dimension."""
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True)
    platform_id = Column(Integer, ForeignKey("platforms.id"), nullable=False)
    dimension_id = Column(Integer, ForeignKey("dimensions.id"), nullable=False)
    value = Column(Float, nullable=False)  # 0–10
    notes = Column(Text)  # justification

    platform = relationship("Platform", back_populates="scores")
    dimension = relationship("Dimension", back_populates="scores")


class UserReport(Base):
    """Community-submitted experience report."""
    __tablename__ = "user_reports"

    id = Column(Integer, primary_key=True)
    platform_id = Column(Integer, ForeignKey("platforms.id"), nullable=False)
    author_name = Column(String(200))
    author_role = Column(String(200))  # e.g., "MES Engineer", "Plant Manager"
    experience = Column(Text, nullable=False)
    rating = Column(Integer)  # 1–5 overall portability experience
    submitted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    platform = relationship("Platform", back_populates="reports")


def get_engine(db_path="portability.db"):
    return create_engine(f"sqlite:///{db_path}", echo=False)


def init_db(db_path="portability.db"):
    engine = get_engine(db_path)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()
