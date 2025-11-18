import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from orm.models import Base, Supermarket

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

def test_create_supermarket(db_session):
    session = db_session
    s = Supermarket(name="Carrefour", city="Madrid")
    session.add(s)
    session.commit()

    result = session.query(Supermarket).filter_by(name="Carrefour").first()
    assert result is not None
    assert result.city == "Madrid"

def test_unique_name_city(db_session):
    session = db_session

    s1 = Supermarket(name="Dia", city="Madrid")
    session.add(s1)
    session.commit()

    s2 = Supermarket(name="Dia", city="Madrid")
    session.add(s2)

    with pytest.raises(Exception):
        session.commit()
