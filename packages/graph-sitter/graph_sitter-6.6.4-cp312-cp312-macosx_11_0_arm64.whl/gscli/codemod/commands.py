import os
import shutil
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor

import click
from rich.console import Console
from rich.table import Table

from graph_sitter.enums import ProgrammingLanguage
from graph_sitter.testing.models import BASE_TMP_DIR, ClonedRepoTestCase, Size
from graph_sitter.testing.test_discovery import find_codemod_test_cases, find_codemods, find_repos


@click.group()
def codemod() -> None:
    """Commands for operating on the codemod tests (i.e. Modal)"""
    pass


@codemod.command()
@click.option("--extra-repos", is_flag=True)
def generate_cases(extra_repos: bool = False):
    """Generate cases for codemod tests. Very slow"""
    repos = find_repos(extra_repos=extra_repos)
    for codemod in find_codemods():
        for repo_name, repo in repos.items():
            (codemod.test_dir / f"test_{repo_name}").mkdir(parents=True, exist_ok=True)
    _generate_diffs(extra_repos=extra_repos)
    _clean_diffs(aggressive=True)


def _generate_diffs(extra_repos: bool = False):
    """Generate diffs for codemod tests"""
    os.system(f"pytest codegen_tests/graph_sitter/codemod/test_codemods.py::test_codemods_cloned_repos  --size small --extra-repos={str(extra_repos).lower()} -n auto --snapshot-update")
    os.system(f"pytest codegen_tests/graph_sitter/codemod/test_codemods.py::test_codemods_cloned_repos  --size large --extra-repos={str(extra_repos).lower()} -n auto --snapshot-update")


@codemod.command()
def generate_diffs():
    """Generate diffs for codemod tests"""
    _generate_diffs()
    _clean_diffs()


def is_empty(path) -> bool:
    for child in path.iterdir():
        if child.is_dir():
            if not is_empty(child):
                return False
        else:
            return False
    return True


def gather_repos_per_codemod() -> dict[str, dict[tuple[Size, bool], list[ClonedRepoTestCase]]]:
    repos = {**find_repos(extra_repos=True), **find_repos(extra_repos=False)}
    counter = defaultdict(lambda: defaultdict(lambda: []))
    for case in sorted(find_codemod_test_cases(repos), key=lambda case: case.codemod_metadata.name):
        counter[case.codemod_metadata.name][case.repo.size, case.repo.extra_repo].append(case)
    return counter


MAX_CASES = {Size.Small: 1, Size.Large: 1}


def _clean_diffs(aggressive: bool = False):
    repos = {**find_repos(extra_repos=True), **find_repos(extra_repos=False)}

    for test_case in find_codemod_test_cases(repos=repos):
        if test_case.diff_path.exists() and test_case.diff_path.read_text().strip() == "":
            os.remove(test_case.diff_path)
    for codemod in find_codemods():
        if not codemod.test_dir.exists():
            continue
        for test_folder in codemod.test_dir.iterdir():
            if test_folder.is_dir() and is_empty(test_folder):
                shutil.rmtree(test_folder)
        if is_empty(codemod.test_dir):
            shutil.rmtree(codemod.test_dir)
    if aggressive:
        for codemod, cases in gather_repos_per_codemod().items():
            for size in [Size.Small, Size.Large]:
                if len(cases[size, False]) > MAX_CASES[size]:
                    cases_to_remove = sorted(cases[size, False], key=lambda case: case.repo.priority, reverse=True)[MAX_CASES[size] :]
                    for case_to_remove in cases_to_remove:
                        if case_to_remove.test_dir.exists():
                            shutil.rmtree(case_to_remove.test_dir)


@codemod.command()
@click.option("--aggressive", is_flag=True)
def clean_diffs(aggressive: bool = False):
    _clean_diffs(aggressive)


@codemod.command()
def report_cases() -> None:
    """Report which test cases actually exists"""
    _clean_diffs()
    table = Table()
    table.add_column("Codemod name")
    table.add_column("OSS tests (small)")
    table.add_column("OSS tests (large)")
    table.add_column("extra tests (small)")
    table.add_column("extra tests (large)")
    for codemod, cases in gather_repos_per_codemod().items():

        def cases_to_str(cases: list[ClonedRepoTestCase]) -> str:
            return ",".join(case.repo_name for case in cases)

        table.add_row(codemod, cases_to_str(cases[Size.Small, False]), cases_to_str(cases[Size.Large, False]), cases_to_str(cases[Size.Small, True]), cases_to_str(cases[Size.Large, True]))
    console = Console()
    console.print(table)


@codemod.command()
@click.option("--extra-repos", is_flag=True)
@click.option("--size", type=click.Choice([e.value for e in Size]))
@click.option("--language", type=click.Choice([e.value for e in ProgrammingLanguage]))
def report_repos(extra_repos: bool = False, size: str | None = None, language: str | None = None) -> None:
    """Report which repos exist. Can filter by size."""
    all_repos = find_repos(
        extra_repos=extra_repos,
        sizes=[Size(size)] if size else None,
        languages=[ProgrammingLanguage(language)] if language else None,
    )

    table = Table()
    table.add_column("ID")
    table.add_column("Name")
    table.add_column("Language")
    table.add_column("Size")
    table.add_column("extra?")
    table.add_column("Priority")
    table.add_column("URL")

    for repo_name, repo in all_repos.items():
        table.add_row(repo.repo_id, repo_name, repo.language.value, repo.size.value, str(repo.extra_repo), str(repo.priority), repo.url)

    console = Console()
    console.print(table)


@codemod.command()
@click.option("--clean-cache", is_flag=True)
@click.option("--extra-repos", is_flag=True)
@click.option("--token", is_flag=False)
def clone_repos(clean_cache: bool = False, extra_repos: bool = False, token: str | None = None) -> None:
    """Clone all repositories for codemod testing."""
    if extra_repos and not token:
        raise ValueError("Token is required for extra repos")

    repo_dir = BASE_TMP_DIR / ("extra_repos" if extra_repos else "oss_repos")
    if clean_cache and repo_dir.exists():
        shutil.rmtree(repo_dir)
    with ProcessPoolExecutor() as executor:
        for name, repo in find_repos(extra_repos=extra_repos).items():
            executor.submit(repo.to_op, name, token)
