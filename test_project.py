import pytest
from pyfiglet import FontNotFound
from project import banner, display_table, prompt

def main():
    test_banner()
    test_display_table()
    test_prompt()

def test_banner():
    # Type or returned value
    assert isinstance(banner("Hello"), str)
    assert isinstance(banner(), str)

    # Int instead of a text
    with pytest.raises(TypeError):
        banner(123)
    
    # Incorrect font
    with pytest.raises(FontNotFound):
        banner("Hello", 123)

def test_display_table():

    assert isinstance(display_table("shortcuts.csv"), str)

    with pytest.raises(OSError):
        display_table(123)

    with pytest.raises(FileNotFoundError):
        display_table()

def test_prompt():
    with pytest.raises(TypeError):
        prompt(123)
        
    with pytest.raises(TypeError):
        prompt("Testing")

if __name__ == "__main__":
    main()