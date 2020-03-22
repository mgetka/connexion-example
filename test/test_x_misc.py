import importlib
import os

# Realoads are dangerous - mark test to be performed last


def test_interface_definition_syntax():

    # Import to check for syntax errors
    import conexample.interface

    importlib.reload(conexample.interface)

    conexample.interface


def test_setting_initialization_from_default_location():

    import conexample

    importlib.reload(conexample)

    assert conexample.SETTINGS == os.environ


def test_setting_initialization_from_custom_location():

    original_env = os.environ.copy()
    os.environ["CONEXAMPLE_CONFIG"] = os.path.join(
        os.path.dirname(__file__), "dummy.env"
    )

    import conexample

    importlib.reload(conexample)

    assert "DUMMY" in conexample.SETTINGS

    os.environ = original_env
