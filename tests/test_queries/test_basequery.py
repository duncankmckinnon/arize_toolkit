from arize_toolkit.queries.basequery import BaseQuery


class TestFindExactNameMatch:
    def test_exact_match_found(self):
        edges = [
            {"node": {"name": "alpha", "id": "1"}},
            {"node": {"name": "beta", "id": "2"}},
        ]
        result = BaseQuery._find_exact_name_match(edges, "beta")
        assert result == {"name": "beta", "id": "2"}

    def test_no_match(self):
        edges = [
            {"node": {"name": "alpha", "id": "1"}},
        ]
        result = BaseQuery._find_exact_name_match(edges, "gamma")
        assert result is None

    def test_partial_match_not_returned(self):
        edges = [
            {"node": {"name": "alpha-v2", "id": "1"}},
        ]
        result = BaseQuery._find_exact_name_match(edges, "alpha")
        assert result is None

    def test_empty_edges(self):
        result = BaseQuery._find_exact_name_match([], "anything")
        assert result is None

    def test_custom_name_field(self):
        edges = [
            {"node": {"email": "user@test.com", "id": "1"}},
            {"node": {"email": "other@test.com", "id": "2"}},
        ]
        result = BaseQuery._find_exact_name_match(edges, "user@test.com", name_field="email")
        assert result == {"email": "user@test.com", "id": "1"}

    def test_missing_node_key(self):
        edges = [{"other": "data"}, {"node": {"name": "found", "id": "1"}}]
        result = BaseQuery._find_exact_name_match(edges, "found")
        assert result == {"name": "found", "id": "1"}

    def test_none_node(self):
        edges = [{"node": None}, {"node": {"name": "found", "id": "1"}}]
        result = BaseQuery._find_exact_name_match(edges, "found")
        assert result == {"name": "found", "id": "1"}

    def test_case_sensitive(self):
        edges = [{"node": {"name": "Alpha", "id": "1"}}]
        result = BaseQuery._find_exact_name_match(edges, "alpha")
        assert result is None
