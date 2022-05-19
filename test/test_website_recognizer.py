from website_recognizer import retrieve_text, result_ready


def test_retrieve_text():
    result_id = "_88514a1791fe4b92a9ba8d83eda205d7"
    text = retrieve_text(result_id)
    assert "а б ц д е ё" in text


def test_result_ready():
    assert result_ready("_ef398361ed1244fda49f99b9972edeb1") is True
    assert result_ready("non-existing id") is False
