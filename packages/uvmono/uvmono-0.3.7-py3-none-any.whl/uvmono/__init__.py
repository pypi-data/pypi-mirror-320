from __future__ import annotations
import shutil
import subprocess
import fire
import yaml

from uvmono.github import find_projects, get_includes, set_github_output
from uvmono.template import (
    add_project_standards,
    create_devcontainer,
    create_dockerfile,
)
from uvmono.types import Include
from uvmono.utils import find_git_root, has_uv


class UvMono:
    """uvmono is a tool to help manage mono-repos in python"""

    def __init__(self):
        self._root = find_git_root()
        self._packages_root = self._root / "packages"
        if (
            not self._packages_root.exists()
            and input(
                "Packages directory not found. Would you like to create it? (y/n)"
            ).lower()
            == "y"
        ):
            self._packages_root.mkdir()

        self._packages = [p for p in self._packages_root.iterdir() if p.is_dir()]

    def new(self, package_name: str, overwrite: bool = False):
        """Create a new package in the mono-repo.

        Args:
            package_name (str): The name of the package to create.
            overwrite (bool, optional): Whether to overwrite the package if it already exists.
        """
        has_uv()
        package_dir = self._packages_root / package_name
        if package_dir.exists() and not overwrite:
            raise FileExistsError(f"Package {package_name} already exists")
        elif package_dir.exists() and overwrite:
            print(f"Overwriting package: {package_name}")
            shutil.rmtree(package_dir)
        package_dir.mkdir()
        dir_cmd = ["--directory", str(package_dir)]
        default_packages = ["pytest", "pytest-cov", "pre-commit", "commitizen"]
        subprocess.run(["uv", "init", "--package", *dir_cmd])
        assert (package_dir / "pyproject.toml").exists(), (
            f"Failed to create package: {package_name}"
        )
        add_project_standards(package_dir)
        subprocess.run(["uv", "add", *default_packages, "--dev", *dir_cmd])
        self.add_devcontainer(package_name=package_name)

    def list(self):
        """List the packages in the mono-repo"""
        packages = [p.name for p in self._packages_root.iterdir() if p.is_dir()]
        return sorted(packages)

    def add_devcontainer(
        self,
        package_name: str = "",
        all: bool = False,
        dry_run: bool = False,
        ubuntu_version: str = "22.04",
        spark_version: str = "3.5.4",
        uv_version: str = "0.5.15",
    ):
        """Add a devcontainer configuration to a package

        Args:
            package_name (str): The name of the package to add the devcontainer to.
            all (bool, optional): Whether to add the devcontainer to all packages.
            dry_run (bool, optional): Whether to run in dry-run mode.
            ubuntu_version (str, optional): The version of ubuntu to use.
            spark_version (str, optional): The version of spark to use.
            uv_version (str, optional): The version of uv to use.
        """
        if not package_name and not all:
            return "Either `package_name` or `all` must be set. Use `--help` for more information."
        packages = self.list() if all else [package_name]
        self._create_dockerfiles(
            ubuntu_version=ubuntu_version,
            spark_version=spark_version,
            uv_version=uv_version,
            dry_run=dry_run,
        )
        self._create_devcontainers(packages, dry_run=dry_run)
        return f"Successfully created devcontainer configuration{'' if all is True else 's'}"

    def _create_devcontainers(self, packages: list[str], dry_run=False):
        print(f"Adding devcontainer configuration to {', '.join(packages)}")
        for package in packages:
            container_path = self._root / ".devcontainer" / package
            dot_to_root = "/".join(
                [".." for _ in container_path.relative_to(self._root).parts]
            )
            if container_path.exists():
                print(
                    f"Devcontainer configuration already exists for {package}. Overwriting"
                )
            docker_compose_file = f"{dot_to_root}/.docker/docker-compose.yml"
            template = create_devcontainer(
                package_name=package,
                dockerfile_path=docker_compose_file,
            )
            if dry_run:
                print(
                    f"[DRY_RUN] Would create devcontainer configuration for {package}"
                )
                continue
            container_path.mkdir(exist_ok=True, parents=True)
            with open(container_path / "devcontainer.json", "w") as f:
                f.write(template)
            print(f"Successfully created devcontainer configuration for {package}")

    def _create_dockerfiles(
        self, ubuntu_version, spark_version, uv_version, dry_run=False
    ):
        compose = {
            "version": "3",
            "services": {
                package: {
                    "build": {
                        "context": "..",
                        "dockerfile": ".docker/Dockerfile",
                        "args": {
                            "UBUNTU_VERSION": ubuntu_version,
                            "SPARK_VERSION": spark_version,
                            "UV_VERSION": uv_version,
                        },
                    },
                    "volumes": ["..:/workspace:cached"],
                    "command": "sleep infinity",
                }
                for package in self.list()
            },
        }
        if dry_run:
            print("Would create docker-compose.yml with the following content:")
            print(yaml.dump(compose))
            return
        if not (self._root / ".docker").exists():
            (self._root / ".docker").mkdir()
        with open(self._root / ".docker" / "docker-compose.yml", "w") as f:
            yaml.dump(compose, f, indent=4)
        dockerfile_path = self._root / ".docker" / "Dockerfile"
        dockerfile_template = create_dockerfile(
            ubuntu_version=ubuntu_version,
            spark_version=spark_version,
            uv_version=uv_version,
        )
        with open(dockerfile_path, "w") as f:
            f.write(dockerfile_template)

    def matrix_strategy(self, key: str, dry_run: bool = False) -> list[Include]:
        """Set the matrix strategy for the mono-repo

        Args:
            key (str): The key to use for the matrix strategy.
                This also appends the key to the `GITHUB_OUTPUT` environment variable.
            dry_run (bool, optional): Whether to run in dry-run mode. Defaults to False.

        Example:
            $ uvmono matrix-strategy python
        """
        projects = find_projects()
        includes = get_includes(projects)
        if not dry_run:
            set_github_output(key, includes)
        return includes

    def _get_relative_package_path(self, package_name: str):
        """Get the path to the package"""
        package_path = self._packages_root / package_name
        if not package_path.exists():
            raise FileNotFoundError(f"Package {package_name} not found")
        return package_path.relative_to(self._packages_root.parent).as_posix()


def main() -> None:
    fire.Fire(UvMono)


if __name__ == "__main__":
    main()
