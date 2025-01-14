import pytest

from dbnomics_fetcher_ops.model.fetcher_metadata.gitlab import GitLabStructure


@pytest.fixture
def gitlab_structure_data():
    return {
        "base_url": "https://example.tld",
        "fetcher": {"group": "fetchers", "name": "{PROVIDER_SLUG}-fetcher"},
        "json_data": {"group": "json-data", "name": "{PROVIDER_SLUG}-json-data"},
        "source_data": {"group": "source-data", "name": "{PROVIDER_SLUG}-source-data"},
    }


def test_base_url_trim_end_slash(gitlab_structure_data):
    gitlab_structure_data["base_url"] += "/"
    gitlab_structure = GitLabStructure.parse_obj(gitlab_structure_data)
    assert gitlab_structure.base_url == "https://example.tld"


def test_fetcher_http_clone_url(gitlab_structure_data):
    gitlab_structure = GitLabStructure.parse_obj(gitlab_structure_data)
    clone_url = gitlab_structure.get_http_clone_url("my-provider", project_ref=gitlab_structure.fetcher)
    assert clone_url == "https://example.tld/fetchers/my-provider-fetcher.git"
