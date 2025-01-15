# Docker Shaper

This is a spin-off package for the `docker-shaper` tool, which can be used to monitor Docker stuff
like containers, images and volumes and automatically enforce certain cleanup-rules.


## Installation

```sh
[<PYTHON> -m] pip[3] install [--user] [--upgrade] docker-shaper
```


## Usage

The tool will start an interactive terminal UI (TUI).

```
poetry run docker-shaper
```

### Attach to build nodes

The application is running in a tmux on the build nodes.
The following command can be used to attach to the session:

```
ssh -t <build node> "su jenkins -Pc 'tmux attach-session -t docker-shaper'"
```

## Development & Contribution

### Setup

For active development you need to have `poetry` and `pre-commit` installed

```sh
python3 -m pip install --upgrade --user poetry pre-commit
git clone ssh://review.lan.tribe29.com:29418/docker_shaper
cd docker_shaper
pre-commit install
# if you need a specific version of Python inside your dev environment
poetry env use ~/.pyenv/versions/3.8.10/bin/python3
poetry install
```

### Workflow


Create a new changelog snippet. If no new snippets is found on a merged change
no new release will be built and published.

If the change is based on a Jira ticket, use the Jira ticket name as snippet
name otherwise use a unique name.

```sh
poetry run \
    changelog-generator \
    create .snippets/CMK-21130.md
```

After committing the snippet a changelog can be generated locally. For CI usage
the `--in-place` flag is recommended to use as it will update the existing
changelog with the collected snippets. For local usage remember to reset the
changelog file before a second run, as the version would be updated recursively
due to the way the changelog generator is working. It extracts the latest
version from the changelog file and puts the found snippets on top.

Future changes to the changelog are ignored by

```sh
git update-index --assume-unchanged changelog.md
```

```sh
poetry run \
    changelog-generator \
    changelog changelog.md \
    --snippets=.snippets \
    --in-place \
    --version-reference="https://review.lan.tribe29.com/gitweb?p=docker_shaper.git;a=tag;h=refs/tags/"
```

Update the version of the project in all required files by calling

```sh
poetry run \
    changelog2version \
    --changelog_file changelog.md \
    --version_file cmk_dev/version.py \
    --version_file_type py \
    --additional_version_info="-rc42+$(git rev-parse HEAD)" \
    --print \
    | jq -r .info.version
```

* modify and check commits via `pre-commit run --all-files`
* after work is done locally:

  - update dependencies before/with a new release
```sh
poetry lock
```
  - build and check package locally
```sh
poetry build && \
twine check dist/* &&
python3 -m pip uninstall -y docker-shaper && \
python3 -m pip install --user dist/docker_shaper-$(grep -E "^version.?=" pyproject.toml | cut -d '"' -f 2)-py3-none-any.whl
```
  - commit, push, review and merge the changes, see `docker_shaper/+/92759/`
```sh
git add ...
git commit -m "bump version, update dependencies"
# merge
```
  - test deployed packages from `test.pypi.org`. The extra index URL is required to get those dependencies from `pypi.org` which are not available from `test.pypi.org`
```sh
pip install --no-cache-dir \
    -i https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple \
    docker-shaper==<VERSION_WITH_RC>
```
  - finally merge the changes and let Jenkins create the release tag and deployment

#### Troubleshooting

##### Publishing fails with HTTP Error 403

As a workaround which uses the token directly, you can do something like this:

```bash
poetry publish --username __token__ --password=<token here>
```

## Todo

- [x] Fix: stuck auto-reload: was: postpone=True + monitoring log
- [x] Fix: crawl-images should fix parents not having them listed
- [-] Fix: stuck crawl images (too many async requests, does not happen in production)
- [ ] Fix: `'677aff0727' could not be removed: DockerError(404, 'No such image: 677aff0727:latest')`
- [ ] Fix: `tried to remove container 4f5fb0848c unknown to us`
- [ ] Fix: Crashes (see runlog)
- [ ] Image update message only if needed
- [ ] New TUI
    - make ongoing progress visible
- [ ] review log levels (too verbose)
- [ ] answer https://stackoverflow.com/questions/32723111

- [x] installable via `pip install`
- [x] Quart interface (instead of `flask`)
- [x] auto-apply changes to source and configuration files
- [x] outsourced config file
- [x] bring in features of former `dgcd`
- [x] bring in features of former `dockermon`
- [x] untag certain tags
- [x] container cleanup
- [x] Fix `none` image lookup
- [x] Exceptions to messages
- [x] Clip
- [x] Increase/decrease logging via web / signal
- [x] Link: cleanup (images/containers) now
- [x] Add volumes list (with recent owners)
- [x] Containers: Store CPU / Memory usage over time
- [x] Containers: store history
- [x] Persist messages
- [ ] Remove old message/container logs
- [ ] Show different color for unmatched images
- [ ] Warn about use of unpinned / upstream images
- [ ] Handle 'build cache objects' (found on system prune)
- [ ] Bring in volume monitoring: which volumes have been created and used by which containers?
- [ ] Containers: show total CPU usage
- [ ] Containers: list volumes
- [ ] Images: list parents / children
- [ ] Volumes: list usage
- [ ] Instructions to readme
- [ ] List unmatched / overmatched tags
- [ ] Links to `delete` / `remove`
- [ ] Links to jobs
- [ ] Link: inspect
- [ ] Graph: cpu / containers (idle/up)
- [ ] Authenticate (at least if we can modify behavior, like stopping/removing images/containers)

## Knowledge

(just misc links to articles that helped me out)
* [How to delete docker images from Nexus Repository 3](https://support.sonatype.com/hc/en-us/articles/360009696054-How-to-delete-docker-images-from-Nexus-Repository-3)
* [Showing Text Box On Hover (In Table)](https://stackoverflow.com/questions/52562345/showing-text-box-on-hover-in-table)
* [Beautiful Interactive Tables for your Flask Templates](https://blog.miguelgrinberg.com/post/beautiful-interactive-tables-for-your-flask-templates)
* https://github.com/torfsen/python-systemd-tutorial
* https://www.digitalocean.com/community/tutorials/how-to-use-templates-in-a-flask-application
* https://stackoverflow.com/questions/49957034/live-updating-dynamic-variable-on-html-with-flask
* https://pgjones.gitlab.io/quart/how_to_guides/templating.html

### Logging

* https://pgjones.gitlab.io/hypercorn/how_to_guides/logging.html#how-to-log

