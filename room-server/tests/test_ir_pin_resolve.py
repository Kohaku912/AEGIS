import pytest

from aegis_room.providers import resolve_ir_pin


def test_resolve_pc9_aliases() -> None:
    for spec in ("PC9", "pc9", "7", "gpiochip1:73", "73"):
        info = resolve_ir_pin(spec)
        assert info["soc_pin"] == "PC9"
        assert info["bank"] == 2
        assert info["bit"] == 9
        assert info["gpio_line"] == 73


def test_resolve_pc11_aliases() -> None:
    for spec in ("PC11", "pc11", "12", "gpiochip1:75", "75"):
        info = resolve_ir_pin(spec)
        assert info["soc_pin"] == "PC11"
        assert info["bank"] == 2
        assert info["bit"] == 11
        assert info["gpio_line"] == 75


def test_forbid_i2c_axp_pins() -> None:
    for spec in ("PH4", "PH5", "3", "5"):
        with pytest.raises(ValueError, match="forbidden"):
            resolve_ir_pin(spec)
