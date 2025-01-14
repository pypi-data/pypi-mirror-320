from itertools import chain
from pathlib import Path

from dbnomics_fetcher_ops.model.fetcher_metadata.base import FetcherDef, FetcherMetadata
from dbnomics_fetcher_ops.model.pipeline_repo.in_memory import InMemoryPipelineRepo, generate_provider_pipelines
from dbnomics_fetcher_ops.services.clean_pipeline_workspaces import clean_fetcher_workspace_pipeline_directories


def test_clean_fetcher_workspace_pipeline_directories(tmp_path: Path):
    pipelines_by_provider_slug = generate_provider_pipelines(
        failed_count=5, provider_slugs=["p1", "p2"], running_count=2, success_count=5
    )

    fetcher_metadata = FetcherMetadata(
        version=1,
        fetchers=[
            FetcherDef(provider_code=provider_slug.upper(), provider_slug=provider_slug)
            for provider_slug in pipelines_by_provider_slug
        ],
    )

    for provider_slug, provider_pipelines in pipelines_by_provider_slug.items():
        for pipeline_id in chain(provider_pipelines.failed, provider_pipelines.running, provider_pipelines.success):
            (tmp_path / provider_slug / "pipelines" / str(pipeline_id)).mkdir(parents=True)

    keep_failed_count = 3
    keep_success_count = 2

    for provider_slug in pipelines_by_provider_slug:
        clean_fetcher_workspace_pipeline_directories(
            tmp_path / provider_slug,
            fetcher_metadata=fetcher_metadata,
            pipeline_repo=InMemoryPipelineRepo(pipelines_by_provider_slug),
            keep_failed_count=keep_failed_count,
            keep_success_count=keep_success_count,
        )

    for provider_slug, provider_pipelines in pipelines_by_provider_slug.items():
        for pipeline_id in provider_pipelines.failed[:keep_failed_count]:
            assert (tmp_path / provider_slug / "pipelines" / str(pipeline_id)).is_dir()
        for pipeline_id in provider_pipelines.failed[keep_failed_count:]:
            assert not (tmp_path / provider_slug / "pipelines" / str(pipeline_id)).is_dir()
        for pipeline_id in provider_pipelines.running:
            assert (tmp_path / provider_slug / "pipelines" / str(pipeline_id)).is_dir()
        for pipeline_id in provider_pipelines.success[:keep_success_count]:
            assert (tmp_path / provider_slug / "pipelines" / str(pipeline_id)).is_dir()
        for pipeline_id in provider_pipelines.success[keep_success_count:]:
            assert not (tmp_path / provider_slug / "pipelines" / str(pipeline_id)).is_dir()
