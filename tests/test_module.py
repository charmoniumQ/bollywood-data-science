# package imports
from bollywood_data_science.module import Human


def test_human():
    jon_snow = Human(name="Jon Snow")
    assert isinstance(jon_snow, Human) == True
