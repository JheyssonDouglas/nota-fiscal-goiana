from src.data import normalize_name, parse_brazilian_number

def test_normalize_name():
    assert normalize_name("  João  da Silva ") == "JOAO DA SILVA"

def test_parse_brazilian_number():
    assert parse_brazilian_number("400000,0") == 400000.0
    assert parse_brazilian_number("1.000,50") == 1000.5
