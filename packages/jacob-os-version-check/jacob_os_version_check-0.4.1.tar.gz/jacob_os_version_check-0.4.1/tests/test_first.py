from jacob_os_version_check.osver import os_check_j
import sys
import platform

def test_first():
    v = os_check_j()
    #assert v == "Ubuntu 24.04.1 LTS"
    # 빈문자열이 아닌지
    assert v is not None
    # 문자열에 LTS가 포함 되었는지
    #assert "LTS" in v
    # 문자열에 문자도 있고, 숫자도 있는지
    assert any(i.isalpha() for i in v)
    assert any(i.isdigit() for i in v)
    # . 이 포함 되어 있는지
    assert '.' in v
    # 길이가 적어도 얼마 이상인지 
    assert len(v) > 5
