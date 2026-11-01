import localitylens


def test_package_exposes_version() -> None:
    assert localitylens.__version__.count(".") == 2
