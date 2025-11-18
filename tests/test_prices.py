import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from orm.models import Base, Product, Supermarket, Price

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

def test_create_price(db_session):
    session = db_session

    p = Product(name="Yogurt", category="Dairy")
    s = Supermarket(name="Mercadona", city="Madrid")
    session.add_all([p, s])
    session.commit()

    price_row = Price(product_id=p.id, store_id=s.id, price=1.25)
    session.add(price_row)
    session.commit()

    result = session.query(Price).first()
    assert float(result.price) == 1.25

def test_price_must_be_positive(db_session):
    session = db_session

    p = Product(name="Coffee", category="Drinks")
    s = Supermarket(name="Carrefour", city="Madrid")
    session.add_all([p, s])
    session.commit()

    bad_price = Price(product_id=p.id, store_id=s.id, price=-1)

    session.add(bad_price)
    with pytest.raises(Exception):
        session.commit()
