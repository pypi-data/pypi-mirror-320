import pytest
import sys
from check_os_ver.osver import get_os_version_of_mac, get_os_version_of_linux

@pytest.mark.skipif(sys.platform != "darwin", reason="Only runs on macOS")
def test_on_mac():
    print("Running on macOS")
    v = get_os_version_of_mac()
    assert "Darwin" in v

@pytest.mark.skipif(not sys.platform.startswith("Linux"), reason="Only runs on Linux")
def test_on_linux(v):
    print("Running on Linux")
    v = get_os_version_of_linux()
    assert "LTS" in v

def test_first():
    if sys.platform == "darwin":
        v = get_os_version_of_mac()
    elif sys.platform.startswith("Linux"):
        v = get_os_version_of_linux()
    else:
        pytest.skip("Unsupported platform")

    # 정상적인 값인지
    assert v is not None

    # 빈 문자열이 아닌지
    assert v != ""

    # 문자열에 문자도 있고, 숫자도 있는지
    assert any(c.isalpha() for c in v)
    assert any(c.isdigit() for c in v)
    
    # . 이 포함 되어있는지
    assert '.' in v

    # 길이가 최소 얼마 이상인지
    assert len(v) > 6

    # 기타 등등
    print("\nAll test passed successfully!")
