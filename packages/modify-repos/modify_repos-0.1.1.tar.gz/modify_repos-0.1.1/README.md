# modify-repos

Clone, modify, and create pull requests across multiple repositories at once.

> [!WARNING]
> This is under development, and how it's used may change at any time.

Documentation: <https://modify-repos.readthedocs.io/>

## Example Use

Use [uv] to create a script that depends on this library.

```
$ uv init --script mod.py
$ uv add --script mod.py modify-repos
```

Subclass `modify_repos.GitHubScript` to define the repositories to change and
what changes to make. This uses the [gh] GitHub CLI, which must already be
installed and logged in.

```python
from modify_repos import GitHubScript, GitHubRepo

class MyScript(GitHubScript):
    # title used in commit and PR
    title = "..."
    # description used in commit and PR
    body = "..."
    # branch to merge into, defaults to main
    target = "main"
    # branch to create and PR
    branch = "my-changes"
    # one or more users/orgs to clone repos from
    orgs = ["username"]

    def select_for_clone(self, repo: GitHubRepo) -> bool:
        # filter to only clone some of the available repos
        return repo.name in {"a", "b", "d"}

    def modify(self, repo: GitHubRepo) -> None:
        # make any changes, such as add/remove files, here
        ...

if __name__ == "__main__":
    MyScript().run()
```

Call `uv run mod.py`, and it will clone and modify all the selected repos. PRs
will not be created unless you use `MyScript(submit=True)` instead, so you can
develop and preview your changes first.

[uv]: https://docs.astral.sh/uv/
[gh]: https://cli.github.com/

## Develop

This project uses [uv] to manage the development environment and [tox] to define
different tests and management scripts.

```
# set up env
$ uv sync
$ uv run pre-commit install --install-hooks

# run tests and checks
$ uv run tox p

# develop docs with auto build and serve
$ uv run tox r -e docs-auto

# update dependencies
$ uv run tox r -m update
```

[tox]: https://tox.wiki/
