from logs.error_parser import analyze_text


def test_analyze_text_counts_expected_signals():
    sample = """
    INFO startup complete
    WARN cache latency
    ERROR request failed with HTTP 500
    warning downstream timeout
    ERROR another failure
    """

    result = analyze_text(sample)

    assert result["ERROR"] == 2
    assert result["WARN"] == 2
    assert result["TIMEOUT"] == 1
    assert result["HTTP_500"] == 1
