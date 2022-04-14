from website_recognizer import retrieve_text


def test_retrieve_text():
    result_id = "_88514a1791fe4b92a9ba8d83eda205d7"
    text = retrieve_text(result_id)
    assert "а б ц д е ё" in text
