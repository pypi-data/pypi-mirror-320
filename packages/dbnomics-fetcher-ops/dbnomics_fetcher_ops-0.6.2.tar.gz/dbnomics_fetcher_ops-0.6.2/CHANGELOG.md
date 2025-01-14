# Changelog

## 0.6.2

- Use [uv](https://docs.astral.sh/uv/) instead of [Poetry](https://github.com/python-poetry/poetry/).
- Update development tools.
- Use src layout for Python package.
- Read `--failed` and `--success` options from environment variables in clean workspace commands.

## 0.6.1

- Add retry command to retry failed jobs of the latest pipeline of a fetcher.
- Add openssh-client to container image.

## 0.6.0

- clean_pipeline_workspaces service: only log message if bytes were actually reclaimed.
- Delete protecting branches of source-data and json-data repositories when configuring a fetcher, because the upgrade to GitLab 16 made the fetcher pipeline unable to push to those repositories by using a deploy key.
- Add prune command to delete a deploy key by title for source-data or json-data projects. This has been introduced to clean the "next.db.nomics.world" keys that are no more relevant.

## 0.5.4

- Show reclaimed disk space after operation.
- Show human friendly paths.
- Test clean workspace service.

## 0.5.3

- Remove cli extras because the script is shipped anyway.

## 0.5.2

- Enhance log messages of clean-workspace(s) commands.

## 0.5.1

- Log when .env is loaded from XDG config dir.
- Add clean-workspace command.
- Upgrade typer and dbnomics-solr.

## 0.5.0

- Add progression indicator in the logs of the "apply" command.
- Add `ProjectRef.get_path_with_namespace. method.
- Make GitLab authentication optional.
- Add clean-workspaces CLI command.

## 0.4.16

- Switch to PyYAML.
- Let mypy analyze package, not directory.

## 0.4.15

- Upgrade dbnomics-solr dependency.
- Remove main function that just calls app.
- Declare package as typed.

## 0.4.14

- Update devtools config, run them in CI.
- Ensure package works with Python >= 3.9.
- Update dbnomics-solr to 1.1.11.

## 0.4.13

- Upgrade to python-gitlab 3.11.0.

## 0.4.12

- Now that all the fetchers use the pipeline v5:
  - use pipeline v5 by default, and
  - stop cleaning up webhooks from pipelines < v5.
- Allow ignoring some managed files. Example:

  ```yaml
  # fetchers.yml
  fetchers:
    - provider_code: P1
      provider_slug: p1
      ignore_managed_files:
        - .dockerignore
        - Dockerfile
  ```

## 0.4.11

- Add -h shortcut for --help.
- Add --dry-run global option, use it in the "run" command.
- Use DEBUG and VERBOSE env vars.

## 0.4.10

- Read config from XDG config directory too (`~/.config/dbnomics/dbnomics-fetchers.env`).

## 0.4.9

- Add run pipeline command and service.

## 0.4.8

- Upgrade devtools.

## 0.4.7

- Upgrade dependencies.

## 0.4.6

- Update Python version constraint to guarantee compatibility at least with Python 3.8.

## 0.4.5

- When configuring fetchers having pipeline v5, remove webhooks defined by pipelines v1 or v2 that are no more used. This includes, for source-data projects, the webhook that triggers a data model validation and the one that triggers a Solr indexation, and for json-data projects, the webhook that triggers a convert job.

## 0.4.4

- Add missing parentheses to function call.

## 0.4.3

- Add logging messages for undeploy.

## 0.4.2

- Enhance error handling during undeploy.

## 0.4.1

- Do not rely on `FetcherDef` in undeploy.

## 0.4.0

- Remove `deploy` property of `FetcherDef` entity. Now just delete a fetcher definition from `fetchers.yml` to trigger an undeploy action from the fetcher management pipeline.
- Add `base_url` property to `GitLabStructure` entity.

## 0.3.14

- Handle case when user cannot take ownership of schedule with business-level exception

## 0.3.13

- Add `download_mode`: `full` (default) or `incremental` to fetcher definition.

## 0.3.12

- Allow reading multiple files from pipeline config. Used to create a default `Dockerfile` in fetcher GitLab projects.

## 0.3.11

- Allow adding environment variables to project definition as well as fetcher definition in `fetchers.yml` under the `env` property
- Do not recreate schedules each time the configure command is run

## 0.3.10

- Support update strategy for category tree and datasets

## 0.3.9

- Support `pipelines.yml` config file, default one is in <https://git.nomics.world/dbnomics/dbnomics-fetcher-pipeline>

## 0.3.8

- Do not fail with error 500 while forking project

## 0.3.7

Non-breaking changes:

- Add ability to fork a fetcher project from an upstream one

## 0.3.6

Non-breaking changes:

- Support multiple pipeline versions (`v1`, `v2`, `v5`)
- Add `labels` to `FetcherDef`

## 0.3.5

Non-breaking changes:

- Use "master" default branch instead of "main" because dbnomics-dashboard is hard-coded with it

## 0.3.4

Non-breaking changes:

- Create fetcher project and group if missing
- Use "main" default branch if project has no branch yet
- Take ownership of pipeline schedule to match declared owner in `fetchers.yml`

## 0.3.3

Non-breaking changes:

- Define PROVIDER_SLUG in project settings, not in .gitlab-ci.yml
- Do not hardcode "master" branch name, use project default branch

## 0.3.2

Non-breaking changes:

- fixup: add missing "raise"

## 0.3.1

Non-breaking changes:

- Fail fast with "apply" command: do not ignore errors

## 0.3

Non-breaking changes:

- Add "apply" command that loops over all fetchers in fetchers.yml and configures or undeploys them according to their `deploy` property

## 0.2

Non-breaking changes:

- Check "deploy: false" in fetchers.yml before undeploy, delete schedules

## 0.1.9

Non-breaking changes:

- Add undeploy command to remove provider data from Solr

## 0.1.8

Non-breaking changes:

- Enhance configuration of fetcher projects based on new features of `fetchers.yml` (schedules per fetcher, data projects location, pipeline template)
- Create container image

Breaking changes:

- Remove SSH deploy key support for next.db.nomics.world fetchers introduced in 0.1.5

## 0.1.7

Non-breaking changes:

- Really correct path of global deploykeys.

## 0.1.6

Non-breaking changes:

- Correct path of global deploykeys.

## 0.1.5

Non-breaking changes:

- Add "next.db.nomics.world fetchers" SSH deploy key to source-data & json-data repositories ([#821](https://git.nomics.world/dbnomics-fetchers/management/-/issues/821))

## 0.1.4

Non-breaking changes:

- Setup JSON-data webhooks for solr and validate jobs ([#821](https://git.nomics.world/dbnomics-fetchers/management/-/issues/821#note_21768))

## 0.1.3

Non-breaking changes:

- Do not overwrite schedule properties that may have been configured manually ([#780](https://git.nomics.world/dbnomics-fetchers/management/-/issues/780))

## 0.1.2

Non-breaking changes:

- Create `.gitlab-ci.yml` file from shared pipeline template if missing

## 0.1.1

Non-breaking changes:

- Add default value for schedule cron expression
- Ensure source-data and json-data projects exist when configuring a fetcher

## 0.1.0

Initial release
