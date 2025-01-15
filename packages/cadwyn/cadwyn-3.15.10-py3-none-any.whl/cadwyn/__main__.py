import importlib
import sys
import warnings
from pathlib import Path
from typing import Any

import typer

from cadwyn.exceptions import CadwynError
from cadwyn.structure.versions import VersionBundle

app = typer.Typer(
    name="cadwyn",
    add_completion=False,
    help="Modern Stripe-like API versioning in FastAPI",
)


def version_callback(value: bool):
    if value:
        from . import __version__

        typer.echo(f"Cadwyn {__version__}")
        raise typer.Exit


@app.command(name="generate-code-for-versioned-packages", hidden=True)
def deprecated_generate_versioned_packages(
    path_to_template_package: str = typer.Argument(
        ...,
        help=(
            "The python path to the template package, from which we will generate the versioned packages. "
            "Format: 'path.to.template_package'"
        ),
        show_default=False,
    ),
    full_path_to_version_bundle: str = typer.Argument(
        ...,
        help="The python path to the version bundle. Format: 'path.to.version_bundle:my_version_bundle_variable'",
        show_default=False,
    ),
    ignore_coverage_for_latest_aliases: bool = typer.Option(
        default=True,
        help="Add a pragma: no cover comment to the star imports in the generated version of the latest module.",
    ),
) -> None:
    """For each version in the version bundle, generate a versioned package based on the template package"""
    warnings.warn(
        "`cadwyn generate-code-for-versioned-packages` is deprecated. Please, use `cadwyn codegen` instead",
        DeprecationWarning,
        stacklevel=1,
    )

    from .codegen._main import generate_code_for_versioned_packages

    sys.path.append(str(Path.cwd()))
    template_package = importlib.import_module(path_to_template_package)
    path_to_version_bundle, version_bundle_variable_name = full_path_to_version_bundle.split(":")
    version_bundle_module = importlib.import_module(path_to_version_bundle)
    possibly_version_bundle = getattr(version_bundle_module, version_bundle_variable_name)
    version_bundle = _get_version_bundle(possibly_version_bundle)

    return generate_code_for_versioned_packages(  # pyright: ignore[reportDeprecated]
        template_package,
        version_bundle,
        ignore_coverage_for_latest_aliases=ignore_coverage_for_latest_aliases,
    )


@app.command(
    name="codegen",
    help=(
        "For each version in the version bundle, generate a versioned package based on the "
        "`head_schema_package` package"
    ),
    short_help="Generate code for all versions of schemas",
)
def generate_versioned_packages(
    full_path_to_version_bundle: str = typer.Argument(
        ...,
        help="The python path to the version bundle. Format: 'path.to.version_bundle:my_version_bundle_var'",
        show_default=False,
    ),
) -> None:
    from .codegen._main import generate_code_for_versioned_packages

    sys.path.append(str(Path.cwd()))
    path_to_version_bundle, version_bundle_variable_name = full_path_to_version_bundle.split(":")
    version_bundle_module = importlib.import_module(path_to_version_bundle)
    possibly_version_bundle = getattr(version_bundle_module, version_bundle_variable_name)
    version_bundle = _get_version_bundle(possibly_version_bundle)

    if version_bundle.head_schemas_package is None:  # pragma: no cover
        raise CadwynError("VersionBundle requires a 'head_schemas_package' argument to generate schemas.")

    return generate_code_for_versioned_packages(version_bundle.head_schemas_package, version_bundle)


def _get_version_bundle(possibly_version_bundle: Any) -> VersionBundle:
    if not isinstance(possibly_version_bundle, VersionBundle):
        err = TypeError(
            "The provided version bundle is not a version bundle and "
            "is not a zero-argument callable that returns the version bundle. "
            f"Instead received: {possibly_version_bundle}",
        )
        if callable(possibly_version_bundle):
            try:
                return _get_version_bundle(possibly_version_bundle())
            except TypeError as e:
                raise err from e
        raise err
    return possibly_version_bundle


@app.callback()
def main(
    version: bool = typer.Option(None, "-V", "--version", callback=version_callback, is_eager=True),
): ...


if __name__ == "__main__":
    app()
