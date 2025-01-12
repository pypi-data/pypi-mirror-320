from rubymarshal.reader import loads



dumped = b'\x04\x08u:\x17Gem::Specification\x01\xd0\x04\x08[\x17"\n1.3.7i\x08"\x06aU:\x11Gem::Version[\x06"\n0.1.0Iu:\tTime\rp\x93\x1b\x80\x00\x00\x00\x00\x06:\x1f@marshal_with_utc_coercionF"\x0cSummaryU:\x15Gem::Requirement[\x06[\x06[\x07"\x07>=U;\x00[\x06"\x060U;\x08[\x06[\x06[\x07"\x07>=U;\x00[\x06"\x060"\truby[\x000"\x0b Email[\x06"\x0c Author"\x00"\x16http://google.comT@\x1d[\x00'

def test_github_bug_11():
    result = loads(dumped)
    print(result)
