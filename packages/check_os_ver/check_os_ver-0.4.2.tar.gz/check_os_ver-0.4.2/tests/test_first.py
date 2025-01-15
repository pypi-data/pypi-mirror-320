import pytest
import sys
from check_os_ver.osver import get_os_version

@pytest.mark.skipif(sys.platform != "darwin", reason="Only runs on macOS")
def test_on_mac():
    print("Running on macOS")

@pytest.mark.skipif(not sys.platform.startswith("Linux"), reason="Only runs on Linux")
def test_on_linux():
    print("Running on Linux")

def test_first():
    v = get_os_version()

    # 정상적인 값인지
    assert v is not None, "Unsupported platform"

    # 빈 문자열이 아닌지
    assert v != ""

    # 문자열에 문자도 있고, 숫자도 있는지
    assert any(c.isalpha() for c in v)
    assert any(c.isdigit() for c in v)
    
    # . 이 포함 되어있는지
    assert '.' in v

    # 길이가 최소 얼마 이상인지
    assert len(v) > 6

    print(f"\nYour OS version: {v}")
    print("\nAll test passed successfully!")
