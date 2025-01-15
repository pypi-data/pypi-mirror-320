import importlib
import inspect
import textwrap
from collections.abc import Generator, Iterator
from pathlib import Path
from typing import TYPE_CHECKING

from loguru import logger

from graph_sitter.codemod import Codemod3
from graph_sitter.enums import ProgrammingLanguage
from graph_sitter.testing.constants import DIFF_FILEPATH, REPO_ID_TO_URL
from graph_sitter.testing.models import BASE_PATH, CODEMOD_PATH, TEST_DIR, VERIFIED_CODEMOD_TEST_DIR, ClonedRepoTestCase, CodemodMetadata, Repo, Size
from graph_sitter.testing.verified_codemod_utils import CodemodAPI, SkillTestConfig
from gscli.generate.runner_imports import get_runner_imports

if TYPE_CHECKING:
    pass


def find_repos(
    extra_repos: bool = False,
    sizes: list[Size] | None = None,
    languages: list[ProgrammingLanguage] | None = None,
) -> dict[str, Repo]:
    sizes = sizes or [size for size in Size]
    languages = languages or [language for language in ProgrammingLanguage]
    results = {}
    repo_path = TEST_DIR / ("repos/extra" if extra_repos else "repos/open_source")
    for file in repo_path.glob("*.json"):
        text = file.read_bytes()
        repo = Repo.from_json(text)
        if repo.size not in sizes:
            continue
        if repo.language not in languages:
            continue
        results[file.stem] = repo
    return results


def codemods_from_dir(codemod_dir: Path) -> Iterator[CodemodMetadata]:
    for file in codemod_dir.glob("*.py"):
        relative = file.relative_to(BASE_PATH).with_suffix("")
        import_path = str(relative).removeprefix("src/").replace("/", ".")
        mod = importlib.import_module(import_path)
        for name, value in inspect.getmembers(mod, inspect.isclass):
            if issubclass(value, Codemod3) and name != "Codemod3":
                yield CodemodMetadata(codemod=value, category=codemod_dir.parent.name, directory=codemod_dir)


def find_test_cases(codemod_dir: Path, repos: dict[str, Repo], codemod: CodemodMetadata) -> Generator[ClonedRepoTestCase, None, None]:
    for dir in codemod_dir.iterdir():
        if dir.is_dir() and "__pycache__" != dir.name:
            repo_name = dir.name.removeprefix("test_")
            if repo_name in repos:
                repo = repos[repo_name]
                yield ClonedRepoTestCase(test_dir=dir, repo=repo, codemod_metadata=codemod, repo_name=repo_name, diff_path=dir / DIFF_FILEPATH)


def find_codemods() -> Generator[CodemodMetadata, None, None]:
    for directory in CODEMOD_PATH.iterdir():
        if directory.name == "repos" or directory.is_file():
            continue
        for codemod_dir in directory.iterdir():
            yield from codemods_from_dir(codemod_dir)


def find_codemod_test_cases(repos: dict[str, Repo]) -> Generator[ClonedRepoTestCase, None, None]:
    for codemod in find_codemods():
        test_dir = codemod.test_dir
        if not test_dir.exists() and codemod.category == "canonical":
            logger.warning(f"No tests exist for {codemod.name}")
        if test_dir.exists():
            tests = list(find_test_cases(codemod_dir=test_dir, repos=repos, codemod=codemod))
            if all(test.repo.extra_repo for test in tests):
                logger.warning(f"All tests for {codemod.name} are against extra repositories")
            elif len(tests) == 0:
                logger.warning(f"No tests exist for {codemod.name}")
            yield from tests


def find_verified_codemod_cases(metafunc):
    """Generate test cases for a list of codemods"""
    repos = {}
    config = SkillTestConfig.from_metafunc(metafunc)
    codemod_api = CodemodAPI(api_key=config.api_key)

    for repo_id, url in REPO_ID_TO_URL.items():
        if config.repo_id and repo_id != config.repo_id:
            continue
        # fetch the verified codemods using CodemodAPI
        codemods_data = codemod_api.get_verified_codemods(
            repo_id=repo_id,
            codemod_id=config.codemod_id,
            base_commit=config.base_commit,
        )

        repo_name = codemods_data["repo_name"]
        programming_language = codemods_data["language"]

        for commit, codemods in codemods_data["codemods_by_base_commit"].items():
            repo_dir_name = f"{repo_name}_{commit}"
            if repo_dir_name not in repos:
                repo = Repo(
                    commit=commit,
                    url=url,
                    language=programming_language,
                    size=Size.Large,
                )
                repos[repo_dir_name] = repo

            yield from generate_codemod_test_cases(repos[repo_dir_name], codemods, repo_dir_name, codemod_api)


def generate_codemod_test_cases(repo, codemods, repo_name, codemod_api):
    """Generate test cases for a list of codemods"""
    for codemod_data in codemods:
        test_dir = VERIFIED_CODEMOD_TEST_DIR / str(codemod_data["codemod_id"])
        diff_path = test_dir / DIFF_FILEPATH
        diff_path.parent.mkdir(parents=True, exist_ok=True)
        with diff_path.open("w") as f:
            # write the diff to the file
            diff = codemod_data["diff"]
            if diff:
                f.write(diff)
            else:
                logger.warning(f"No diff found for codemod: {codemod_data['codemod_id']}")

            # add the execute method to the codemod
            execute_func = create_function_from_string("execute", codemod_data)
            codemod = Codemod3(name=codemod_data["codemod_id"], execute=execute_func)

            codemod_metadata = CodemodMetadata(
                codemod=codemod,
                category="verified_codemod",
                directory=VERIFIED_CODEMOD_TEST_DIR,
                repo_app_id=codemod_data["repo_app_id"],
                codemod_id=codemod_data["codemod_id"],
                codemod_url=codemod_data["codemod_url"],
                codemod_api=codemod_api,
                empty_diff=codemod_data["diff"] is None,
            )
            yield ClonedRepoTestCase(
                test_dir=test_dir,
                repo=repo,
                codemod_metadata=codemod_metadata,
                repo_name=repo_name,
                diff_path=diff_path,
            )


def create_function_from_string(function_name, codemod):
    """Adds a function to a class instance using a string of code.

    Args:
        function_name: Name of the function to create
        skill: Skill object containing the function code

    Returns:
        The function object if successful, None if there was an error
    """
    # Create a namespace for the execution
    code_string = codemod["source"]

    namespace = {}
    import_str = get_runner_imports(include_private_imports=False, include_codegen=False)
    # Prepare the code string by ensuring proper indentation
    code_string = code_string.strip()
    # logger.info(f"Adding function: \n{code_string}\n")
    code_string = import_str + "\n\n" + "def " + function_name + "(codebase):\n" + textwrap.indent(code_string, "    ")

    try:
        # Execute the code string in our namespace
        exec(code_string, namespace)

        # Get the function from our namespace
        function = namespace[function_name]

        return function
    except Exception as e:
        logger.error(f"Error adding function for codemod: {codemod['codemod_id']}, codemod: {codemod['codemod_url']}, error: {e!s}")
        raise e
