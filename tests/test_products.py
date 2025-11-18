import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from orm.models import Base, Product

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

def test_create_product(db_session):
    session = db_session
    p = Product(name="Test Milk", category="Dairy")
    session.add(p)
    session.commit()

    result = session.query(Product).filter_by(name="Test Milk").first()
    assert result is not None
    assert result.category == "Dairy"

def test_unique_product_name(db_session):
    session = db_session
    p1 = Product(name="Unique Bread", category="Bakery")
    session.add(p1)
    session.commit()

    p2 = Product(name="Unique Bread", category="Bakery")
    session.add(p2)

    with pytest.raises(Exception):
        session.commit()
