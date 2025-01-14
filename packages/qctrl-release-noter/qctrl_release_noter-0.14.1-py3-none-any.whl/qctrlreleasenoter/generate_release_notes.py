# Copyright 2024 Q-CTRL
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Generates release notes based on the commit history since the last release.
"""
from __future__ import annotations

import re
import webbrowser
from dataclasses import (
    dataclass,
    field,
    fields,
)
from enum import Enum
from functools import partial
from itertools import (
    chain,
    islice,
)
from pathlib import Path
from typing import (
    Iterator,
    Optional,
)
from urllib.parse import quote_plus

import click
import pyinflect
from git import Repo
from git.objects import Commit
from git.refs.tag import TagReference
from packaging.version import (
    VERSION_PATTERN,
    Version,
    parse,
)


class _PrType(Enum):
    MINOR = ("feat",)
    PATCH = ("fix", "perf", "revert", "build")
    IGNORED = ("refactor", "chore", "ci", "docs", "style", "test")
    # Using an empty tuple here seems to cause issue in Python 3.11.1,
    # as it's treated as an object instead of an iterable.
    # Therefore, in `_classify_commit_type` we exclude the UNKNOWN item.
    UNKNOWN = ()


def _classify_commit_type(kind: str) -> _PrType:
    """
    Classify the PR type for a commit based on its kind.
    This could be a classmethod of _PrType, but it's convenient for type-checking as
    a private function.
    """
    # Classify the types for valid PRs in the release note.
    for type_ in islice(_PrType, len(_PrType) - 1):
        if kind in type_.value:
            return type_
    # Label the invalid PR.
    return _PrType.UNKNOWN


@dataclass
class _CommitInfo:
    title: str
    kind: _PrType
    sha: Optional[str]
    breaking_change_message: Optional[str]


class _ReleasePhase(Enum):
    ALPHA = "alpha"
    BETA = "beta"
    STABLE = "stable"


@dataclass
class NoteBody:
    """
    Dataclass to hold the body of release note.
    """

    major: list[str] = field(default_factory=list)
    minor: list[str] = field(default_factory=list)
    patch: list[str] = field(default_factory=list)
    unknown: list[str] = field(default_factory=list)

    def is_empty(self) -> bool:
        """
        Check whether the note body is empty.
        """
        return (
            sum(
                map(
                    len, (getattr(self, field.name) for field in fields(self.__class__))
                )
            )
            == 0
        )

    def add_item(self, item: _CommitInfo) -> None:
        """
        Update note body from a commit item.
        """
        # Handle the breaking change first since
        # any valid PR could be a breaking one.
        if item.breaking_change_message is not None:
            self.major.append(item.breaking_change_message)

        if item.kind is _PrType.IGNORED:
            return
        if item.kind is _PrType.UNKNOWN:
            print_warning(
                f"Commit {item.sha} has unknown kind {item.kind!r}, "
                "appending to unknown changes."
            )
            self.unknown.append(convert_to_past_tense(item.title))
        else:
            pr_type = getattr(self, item.kind.name.lower())
            pr_type.append(convert_to_past_tense(item.title))


def pull_latest_changes(branch, repo):
    """
    Pulls the latest changes from remote for the specified `branch`.
    """
    repo.git.checkout(branch)
    repo.remotes.origin.pull()


def is_version(tag: TagReference, tag_prefix: str) -> bool:
    """
    Use packaging.version's regex to determine if a tag name is a valid version.
    See also: https://packaging.pypa.io/en/stable/version.html
    """
    return (
        re.match(
            VERSION_PATTERN,
            tag.name.removeprefix(tag_prefix),
            flags=re.VERBOSE | re.IGNORECASE,
        )
        is not None
    )


def get_latest_tag(repo: Repo, tag_prefix: str) -> Optional[TagReference]:
    """
    Get the latest tag by the tag_prefix. Return None if nothing matches the tag_prefix or
    there is no tag.
    """
    tags = filter(
        partial(is_version, tag_prefix=tag_prefix),
        filter(lambda tag: tag.name.startswith(tag_prefix), repo.tags),
    )
    # Need a local variable for mypy. See https://github.com/python/mypy/issues/16267
    _tag = max(tags, key=lambda tag: tag.commit.committed_date, default=None)
    return _tag


def get_latest_version_and_commits(
    repo: Repo, tag_prefix: str, paths: str | list[str], branch: str
) -> tuple[Version, Iterator[Commit]]:
    """
    Return the latest version with tag_prefix stripped and the all commits since the last version
    on the `branch` in the given `paths`. If `paths` is empty, it returns all commits in the working
    directory.
    """
    latest_tag = get_latest_tag(repo, tag_prefix)

    if latest_tag is not None:
        return parse(latest_tag.name.removeprefix(tag_prefix)), repo.iter_commits(
            f"{latest_tag.name}..{branch}", reverse=True, paths=paths
        )

    # Meaning this is the first release of the target repo.
    return Version("0.0.0"), repo.iter_commits(reverse=True, paths=paths)


def _maybe_get_project_name_from_readme(repo: Repo) -> Optional[str]:
    """
    Attempt to fetch the project name from the README title.
    """
    readme_path = [
        f"{repo.working_dir}/.github/README.md",
        f"{repo.working_dir}/README.md",
    ]
    for filepath in readme_path:
        if Path(filepath).is_file():
            with open(filepath, "r", encoding="utf8") as file:
                header = re.search(
                    "^(?: *)#(?: *)(.+)(?: *)$", file.read(), re.MULTILINE
                )
            if header is not None:
                return header.group(1)
    print_warning("No project name found. Release name will not be suggested.")
    return None


def get_repo_github_url(repo: Repo) -> str:
    """
    Given a Repo object, return its GitHub URL.
    """
    if len(repo.remotes) == 0:
        raise RuntimeError("No remote repo found, cannot redirect to GitHub.")
    if len(repo.remotes) > 1:
        raise RuntimeError(
            "More than one remote repo found, cannot redirect to GitHub."
        )
    match = re.search(
        r"^(?:https://github.com/?|git@github.com:)([\d\w\/-]+)(?:\.git)?$",
        repo.remotes.origin.url,
    )
    if match is None:
        raise RuntimeError("Remote repository is not on GitHub, cannot redirect.")
    repo_url = f"https://github.com/{match.group(1)}"
    return repo_url


def generate_note(
    branch: str,
    github: bool,
    phase: str,
    repo: Repo,
    allow_empty: bool,
    paths: list[str] | str = "",
    tag_prefix: str = "",
    project_name: Optional[str] = None,
    extra_commits: Optional[list[Commit]] = None,
    include_all_commits: bool = False,
) -> dict[str, str]:
    """
    Generate release notes for the commits between the latest tag and `branch`.
    """
    version, commits = get_latest_version_and_commits(repo, tag_prefix, paths, branch)
    if extra_commits is not None:
        commits = chain.from_iterable((commits, extra_commits))
    note_body = generate_note_from_commits(commits, include_all_commits)
    if note_body.is_empty():
        if not allow_empty:
            raise RuntimeError(
                "No correctly formatted changes detected. "
                "You can use --allow-empty to create a release notes template."
            )
        note_body = generate_empty_note()
        print_warning(
            "No correctly formatted changes detected. "
            "Remember to update the template before releasing the new version."
        )

    if project_name is None:
        project_name = _maybe_get_project_name_from_readme(repo)

    try:
        release_phase = _ReleasePhase[phase.upper()]
    except KeyError as err:
        raise RuntimeError(f"Unknown release phase: {phase}.") from err

    query_parameters = {
        "tag": get_new_version_tag(
            release_phase=release_phase,
            current_version=version,
            has_major_changes=len(note_body.major) > 0,
            has_minor_changes=len(note_body.minor) > 0,
            tag_prefix=tag_prefix,
        ),
        "target": branch,
    }

    if project_name is not None:
        query_parameters["title"] = (
            f"{project_name} {query_parameters['tag'].removeprefix(tag_prefix)}"
        )

    # Create summary of changes.
    change_list = []
    for items, title in [
        (note_body.unknown, "UNKNOWN CHANGES"),
        (note_body.major, "Major changes"),
        (note_body.minor, "Minor changes"),
        (note_body.patch, "Patch changes"),
    ]:
        if not items:
            continue
        change_list += [title]
        formatted_items = [format_list_item(item) for item in items]
        change_list += ["\n".join(formatted_items)]
    query_parameters["body"] = "\n\n".join(change_list)

    if github:
        repo_url = get_repo_github_url(repo)
        parsed_parameters = "&".join(
            [f"{key}={quote_plus(value)}" for key, value in query_parameters.items()]
        )
        webbrowser.open(f"{repo_url}/releases/new?{parsed_parameters}")

    return query_parameters


def _get_commit_info(
    commit: Commit, include_all_commits: bool
) -> Optional[_CommitInfo]:
    """
    Extract relevant parts from the commit message.
    """
    message = commit.message
    assert isinstance(message, str)

    title_match = re.match("(?:(?P<kind>[a-z]*)(?P<break>!)?: )?(?P<title>.*)", message)

    # For now, this branch is never triggered since the title group in the
    # regex pattern above will match any string. This mainly serves as
    # a type-checking for mypy at the moment. We can revise this if we
    # change the regex pattern later.
    if title_match is None:
        print_warning(
            f"Commit {commit.hexsha} has incorrectly formatted "
            f"title {message.splitlines()[0]}, ignoring."
        )
        return None

    kind = title_match.groupdict()["kind"]
    title = title_match.groupdict()["title"]

    assert isinstance(title, str)

    # See whether this commit is a breaking change. We need to check both
    # the title for an exclamation mark and the description for BREAKING
    # CHANGE (we check for BREAKING-CHANGE too, as per Conventional
    # Commits).
    breaking_change_message = None
    breaking_description_match = re.search("BREAKING(?: |-)CHANGE:", message)
    if breaking_description_match:
        breaking_change_message = message[breaking_description_match.end() :]
    elif title_match.groupdict()["break"]:
        print_warning(
            f"Commit {commit.hexsha} is missing a breaking change "
            "description, using commit title instead."
        )
        breaking_change_message = convert_to_past_tense(title)

    _kind = _classify_commit_type(kind)
    # No commits are ignored if the include_all_commits flag was passed.
    if _kind is _PrType.IGNORED and include_all_commits:
        _kind = _PrType.PATCH

    return _CommitInfo(
        title=title,
        kind=_kind,
        sha=commit.hexsha,
        breaking_change_message=breaking_change_message,
    )


def generate_note_from_commits(
    commits: Iterator[Commit], include_all_commits: bool
) -> NoteBody:
    """
    Iterate through commits, collecting information about major, minor, and patch changes.
    """

    note_body = NoteBody()
    for commit in commits:
        commit_info = _get_commit_info(commit, include_all_commits)
        if commit_info is None:
            continue
        note_body.add_item(commit_info)
    return note_body


def generate_empty_note() -> NoteBody:
    """
    Create a template for empty release note.
    """
    note_body = NoteBody()
    title = (
        "No changes found. Add a description of the changes that require the release"
    )
    note_body.add_item(
        _CommitInfo(
            title=title, kind=_PrType.PATCH, sha=None, breaking_change_message=None
        )
    )
    return note_body


def get_new_version_tag(
    release_phase: _ReleasePhase,
    current_version: Version,
    has_major_changes: bool,
    has_minor_changes: bool,
    tag_prefix: str,
) -> str:
    """
    Get the version tag for the next release.
    """
    if release_phase is _ReleasePhase.STABLE:
        _release_func = _stable_release
    else:
        _release_func = partial(_pre_release, phase=release_phase)
    return tag_prefix + _release_func(
        current_version,
        has_major_changes=has_major_changes,
        has_minor_changes=has_minor_changes,
    )


def _pre_release(
    current_version: Version,
    has_major_changes: bool,
    has_minor_changes: bool,
    phase: _ReleasePhase,
) -> str:
    if current_version.is_prerelease:
        assert current_version.pre is not None  # for mypy
        current_pre_version, pre_version_num = current_version.pre
        if current_pre_version == "b" and phase is _ReleasePhase.ALPHA:
            print_warning(
                "Releasing an alpha version after a beta version means "
                "a stable version is skipped."
            )
        # Jumping between pre release phases would reset the pre version number.
        _num = 0 if current_pre_version != phase.value[0] else pre_version_num + 1
        return f"{current_version.base_version}-{phase.value}.{_num}"
    return f"{_stable_release(current_version, has_major_changes, has_minor_changes)}-{phase.value}"


def _stable_release(
    current_version: Version, has_major_changes: bool, has_minor_changes: bool
) -> str:
    # pre -> stable
    if current_version.is_prerelease:
        return current_version.base_version

    # stable -> stable
    major, minor, patch = current_version.release
    if has_major_changes:
        if major > 0:
            major += 1
            minor = 0
            patch = 0
        else:
            minor += 1
            patch = 0
    elif has_minor_changes:
        minor += 1
        patch = 0
    else:
        patch += 1
    return f"{major}.{minor}.{patch}"


def convert_to_past_tense(text: str) -> str:
    """
    Tries to convert the given text to past tense.
    """
    # Convert the first word to past tense if possible, otherwise just leave the
    # text unchanged.
    parts = text.split(" ", 1)
    past_tense = pyinflect.getInflection(parts[0], "VBD")
    if past_tense:
        parts[0] = past_tense[0]
    return " ".join(parts)


def format_list_item(text: str) -> str:
    """
    Formats text (which might contain newlines) into a Markdown list item.
    """
    text = text.strip()

    # Capitalize first word and add period if necessary.
    parts = text.split(" ", 1)
    parts[0] = parts[0].capitalize()
    text = " ".join(parts)
    if text[-1] not in ".?!":
        text += "."

    # Indent subsequent lines.
    indented = "\n  ".join([line.strip() for line in text.splitlines()])

    return f"- {indented}"


def print_warning(message: str):
    """
    Prints a warning message to stderr.
    """
    click.echo(click.style(message, fg="red"), err=True)
