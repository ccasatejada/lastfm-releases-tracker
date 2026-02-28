from utils.url_utils import clean_url


class TestCleanUrl:
    def test_removes_fr_prefix(self):
        assert clean_url('/fr/user/alice') == '/user/alice'

    def test_no_change_without_fr(self):
        assert clean_url('/en/user/alice') == '/en/user/alice'

    def test_empty_string(self):
        assert clean_url('') == ''

    def test_multiple_fr_segments(self):
        assert clean_url('/fr/user/fr/page') == '/user/page'
