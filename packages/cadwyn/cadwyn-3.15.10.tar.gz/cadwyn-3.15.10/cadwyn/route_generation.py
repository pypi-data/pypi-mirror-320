import functools
import inspect
import re
import types
import typing
import warnings
from collections import defaultdict
from collections.abc import Callable, Sequence
from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from types import GenericAlias, MappingProxyType, ModuleType
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    Generic,
    TypeVar,
    _BaseGenericAlias,  # pyright: ignore[reportAttributeAccessIssue]
    cast,
    final,
    get_args,
    get_origin,
    overload,
)

import fastapi.params
import fastapi.routing
import fastapi.security.base
import fastapi.utils
from fastapi import APIRouter
from fastapi._compat import ModelField as FastAPIModelField
from fastapi._compat import create_body_model
from fastapi.params import Depends
from fastapi.routing import APIRoute
from issubclass import issubclass as lenient_issubclass
from pydantic import BaseModel
from starlette.routing import BaseRoute
from typing_extensions import Self, assert_never, deprecated

from cadwyn._compat import get_annotation_from_model_field, model_fields, rebuild_fastapi_body_param
from cadwyn._package_utils import get_version_dir_path
from cadwyn._utils import Sentinel, UnionType, get_another_version_of_cls
from cadwyn.exceptions import (
    CadwynError,
    RouteAlreadyExistsError,
    RouteByPathConverterDoesNotApplyToAnythingError,
    RouteRequestBySchemaConverterDoesNotApplyToAnythingError,
    RouteResponseBySchemaConverterDoesNotApplyToAnythingError,
    RouterGenerationError,
    RouterPathParamsModifiedError,
)
from cadwyn.structure import Version, VersionBundle
from cadwyn.structure.common import Endpoint, VersionDate
from cadwyn.structure.endpoints import (
    EndpointDidntExistInstruction,
    EndpointExistedInstruction,
    EndpointHadInstruction,
)
from cadwyn.structure.versions import _CADWYN_REQUEST_PARAM_NAME, _CADWYN_RESPONSE_PARAM_NAME, VersionChange

if TYPE_CHECKING:
    from fastapi.dependencies.models import Dependant

_Call = TypeVar("_Call", bound=Callable[..., Any])
_R = TypeVar("_R", bound=fastapi.routing.APIRouter)
# This is a hack we do because we can't guarantee how the user will use the router.
_DELETED_ROUTE_TAG = "_CADWYN_DELETED_ROUTE"


@dataclass(slots=True, frozen=True, eq=True)
class _EndpointInfo:
    endpoint_path: str
    endpoint_methods: frozenset[str]


@deprecated("It will soon be deleted. Use HeadVersion version changes instead.")
class InternalRepresentationOf:
    def __class_getitem__(cls, original_schema: type, /) -> type[Self]:
        return cast(Any, type("InternalRepresentationOf", (cls, original_schema), {}))


@overload
def generate_versioned_routers(
    router: _R,
    versions: VersionBundle,
) -> dict[VersionDate, _R]: ...


@overload
@deprecated("Do not use the latest_schemas_package argument. Put head_schemas_package into your VersionBundle instead")
def generate_versioned_routers(
    router: _R,
    versions: VersionBundle,
    latest_schemas_package: ModuleType | None,
) -> dict[VersionDate, _R]: ...


def generate_versioned_routers(
    router: _R,
    versions: VersionBundle,
    latest_schemas_package: ModuleType | None = None,
) -> dict[VersionDate, _R]:
    if versions.head_schemas_package is not None:
        head_schemas_package = versions.head_schemas_package
    elif latest_schemas_package is not None:  # pragma: no cover
        head_schemas_package = latest_schemas_package
    else:  # pragma: no cover
        raise TypeError(
            "TypeError: generate_versioned_routers() must be called with a VersionBundle "
            "that contains a non-null head_schemas_package."
        )
    versions.head_schemas_package = head_schemas_package
    versions._validate_head_schemas_package_structure()
    return _EndpointTransformer(router, versions, head_schemas_package).transform()


class VersionedAPIRouter(fastapi.routing.APIRouter):
    def only_exists_in_older_versions(self, endpoint: _Call) -> _Call:
        route = _get_route_from_func(self.routes, endpoint)
        if route is None:
            raise LookupError(
                f'Route not found on endpoint: "{endpoint.__name__}". '
                "Are you sure it's a route and decorators are in the correct order?",
            )
        if _DELETED_ROUTE_TAG in route.tags:
            raise CadwynError(f'The route "{endpoint.__name__}" was already deleted. You can\'t delete it again.')
        route.tags.append(_DELETED_ROUTE_TAG)
        return endpoint


class _EndpointTransformer(Generic[_R]):
    def __init__(
        self,
        parent_router: _R,
        versions: VersionBundle,
        head_schemas_package: ModuleType,
    ) -> None:
        super().__init__()
        self.parent_router = parent_router
        self.versions = versions
        self.annotation_transformer = _AnnotationTransformer(head_schemas_package, versions)

        self.routes_that_never_existed = [
            route for route in parent_router.routes if isinstance(route, APIRoute) and _DELETED_ROUTE_TAG in route.tags
        ]

    def transform(self) -> dict[VersionDate, _R]:
        schema_to_internal_request_body_representation = _extract_internal_request_schemas_from_router(
            self.parent_router
        )
        router = deepcopy(self.parent_router)
        routers: dict[VersionDate, _R] = {}

        for version in self.versions:
            self.annotation_transformer.migrate_router_to_version(router, version)

            self._validate_all_data_converters_are_applied(router, version)

            routers[version.value] = router
            # Applying changes for the next version
            router = deepcopy(router)
            self._apply_endpoint_changes_to_router(router, version)

        if self.routes_that_never_existed:
            raise RouterGenerationError(
                "Every route you mark with "
                f"@VersionedAPIRouter.{VersionedAPIRouter.only_exists_in_older_versions.__name__} "
                "must be restored in one of the older versions. Otherwise you just need to delete it altogether. "
                "The following routes have been marked with that decorator but were never restored: "
                f"{self.routes_that_never_existed}",
            )

        for route_index, head_route in enumerate(self.parent_router.routes):
            if not isinstance(head_route, APIRoute):
                continue
            _add_request_and_response_params(head_route)
            copy_of_dependant = deepcopy(head_route.dependant)

            if _route_has_a_simple_body_schema(head_route):
                self._replace_internal_representation_with_the_versioned_schema(
                    copy_of_dependant,
                    schema_to_internal_request_body_representation,
                )

            for older_router in list(routers.values()):
                older_route = older_router.routes[route_index]

                # We know they are APIRoutes because of the check at the very beginning of the top loop.
                # I.e. Because head_route is an APIRoute, both routes are  APIRoutes too
                older_route = cast(APIRoute, older_route)
                # Wait.. Why do we need this code again?
                if older_route.body_field is not None and _route_has_a_simple_body_schema(older_route):
                    template_older_body_model = self.annotation_transformer._change_version_of_annotations(
                        older_route.body_field.type_,
                        self.annotation_transformer.head_version_dir,
                    )
                else:
                    template_older_body_model = None
                _add_data_migrations_to_route(
                    older_route,
                    # NOTE: The fact that we use latest here assumes that the route can never change its response schema
                    head_route,
                    template_older_body_model,
                    older_route.body_field.alias if older_route.body_field is not None else None,
                    copy_of_dependant,
                    self.versions,
                )
        for _, router in routers.items():
            router.routes = [
                route
                for route in router.routes
                if not (isinstance(route, fastapi.routing.APIRoute) and _DELETED_ROUTE_TAG in route.tags)
            ]
        return routers

    def _validate_all_data_converters_are_applied(self, router: APIRouter, version: Version):
        path_to_route_methods_mapping, head_response_models, head_request_bodies = self._extract_all_routes_identifiers(
            router
        )

        for version_change in version.version_changes:
            for by_path_converters in [
                *version_change.alter_response_by_path_instructions.values(),
                *version_change.alter_request_by_path_instructions.values(),
            ]:
                for by_path_converter in by_path_converters:
                    missing_methods = by_path_converter.methods.difference(
                        path_to_route_methods_mapping[by_path_converter.path]
                    )

                    if missing_methods:
                        raise RouteByPathConverterDoesNotApplyToAnythingError(
                            f"{by_path_converter.repr_name} "
                            f'"{version_change.__name__}.{by_path_converter.transformer.__name__}" '
                            f"failed to find routes with the following methods: {list(missing_methods)}. "
                            f"This means that you are trying to apply this converter to non-existing endpoint(s). "
                            "Please, check whether the path and methods are correct. (hint: path must include "
                            "all path variables and have a name that was used in the version that this "
                            "VersionChange resides in)"
                        )

            for by_schema_converters in version_change.alter_request_by_schema_instructions.values():
                for by_schema_converter in by_schema_converters:
                    missing_models = set(by_schema_converter.schemas) - head_request_bodies
                    if missing_models:
                        raise RouteRequestBySchemaConverterDoesNotApplyToAnythingError(
                            f"Request by body schema converter "
                            f'"{version_change.__name__}.{by_schema_converter.transformer.__name__}" '
                            f"failed to find routes with the following body schemas: "
                            f"{[m.__name__ for m in missing_models]}. "
                            f"This means that you are trying to apply this converter to non-existing endpoint(s). "
                        )
            for by_schema_converters in version_change.alter_response_by_schema_instructions.values():
                for by_schema_converter in by_schema_converters:
                    missing_models = set(by_schema_converter.schemas) - head_response_models
                    if missing_models:
                        raise RouteResponseBySchemaConverterDoesNotApplyToAnythingError(
                            f"Response by response model converter "
                            f'"{version_change.__name__}.{by_schema_converter.transformer.__name__}" '
                            f"failed to find routes with the following response models: "
                            f"{[m.__name__ for m in missing_models]}. "
                            f"This means that you are trying to apply this converter to non-existing endpoint(s). "
                        )

    def _extract_all_routes_identifiers(
        self, router: APIRouter
    ) -> tuple[defaultdict[str, set[str]], set[Any], set[Any]]:
        response_models: set[Any] = set()
        request_bodies: set[Any] = set()
        path_to_route_methods_mapping: dict[str, set[str]] = defaultdict(set)

        for route in router.routes:
            if isinstance(route, APIRoute):
                if route.response_model is not None and lenient_issubclass(route.response_model, BaseModel):
                    # FIXME: This is going to fail on Pydantic 1
                    response_models.add(route.response_model)
                    # Not sure if it can ever be None when it's a simple schema. Eh, I would rather be safe than sorry
                if _route_has_a_simple_body_schema(route) and route.body_field is not None:
                    annotation = get_annotation_from_model_field(route.body_field)
                    if lenient_issubclass(annotation, BaseModel):
                        # FIXME: This is going to fail on Pydantic 1
                        request_bodies.add(annotation)
                path_to_route_methods_mapping[route.path] |= route.methods

        head_response_models = {
            self.annotation_transformer._change_version_of_annotations(
                model,
                self.versions.versioned_directories_with_head[0],
            )
            for model in response_models
        }
        head_request_bodies = {
            self.annotation_transformer._change_version_of_annotations(
                body,
                self.versions.versioned_directories_with_head[0],
            )
            for body in request_bodies
        }

        return path_to_route_methods_mapping, head_response_models, head_request_bodies

    def _replace_internal_representation_with_the_versioned_schema(
        self,
        copy_of_dependant: "Dependant",
        schema_to_internal_request_body_representation: dict[type[BaseModel], type[BaseModel]],
    ):
        body_param: FastAPIModelField = copy_of_dependant.body_params[0]
        body_schema = body_param.type_
        new_type = schema_to_internal_request_body_representation.get(body_schema, body_schema)
        new_body_param = rebuild_fastapi_body_param(body_param, new_type)
        copy_of_dependant.body_params = [new_body_param]

    # TODO (https://github.com/zmievsa/cadwyn/issues/28): Simplify
    def _apply_endpoint_changes_to_router(  # noqa: C901
        self,
        router: fastapi.routing.APIRouter,
        version: Version,
    ):
        routes = router.routes
        for version_change in version.version_changes:
            for instruction in version_change.alter_endpoint_instructions:
                original_routes = _get_routes(
                    routes,
                    instruction.endpoint_path,
                    instruction.endpoint_methods,
                    instruction.endpoint_func_name,
                    is_deleted=False,
                )
                methods_to_which_we_applied_changes = set()
                methods_we_should_have_applied_changes_to = instruction.endpoint_methods.copy()

                if isinstance(instruction, EndpointDidntExistInstruction):
                    deleted_routes = _get_routes(
                        routes,
                        instruction.endpoint_path,
                        instruction.endpoint_methods,
                        instruction.endpoint_func_name,
                        is_deleted=True,
                    )
                    if deleted_routes:
                        method_union = set()
                        for deleted_route in deleted_routes:
                            method_union |= deleted_route.methods
                        raise RouterGenerationError(
                            f'Endpoint "{list(method_union)} {instruction.endpoint_path}" you tried to delete in '
                            f'"{version_change.__name__}" was already deleted in a newer version. If you really have '
                            f'two routes with the same paths and methods, please, use "endpoint(..., func_name=...)" '
                            f"to distinguish between them. Function names of endpoints that were already deleted: "
                            f"{[r.endpoint.__name__ for r in deleted_routes]}",
                        )
                    for original_route in original_routes:
                        methods_to_which_we_applied_changes |= original_route.methods
                        original_route.tags.append(_DELETED_ROUTE_TAG)
                    err = (
                        'Endpoint "{endpoint_methods} {endpoint_path}" you tried to delete in'
                        ' "{version_change_name}" doesn\'t exist in a newer version'
                    )
                elif isinstance(instruction, EndpointExistedInstruction):
                    if original_routes:
                        method_union = set()
                        for original_route in original_routes:
                            method_union |= original_route.methods
                        raise RouterGenerationError(
                            f'Endpoint "{list(method_union)} {instruction.endpoint_path}" you tried to restore in'
                            f' "{version_change.__name__}" already existed in a newer version. If you really have two '
                            f'routes with the same paths and methods, please, use "endpoint(..., func_name=...)" to '
                            f"distinguish between them. Function names of endpoints that already existed: "
                            f"{[r.endpoint.__name__ for r in original_routes]}",
                        )
                    deleted_routes = _get_routes(
                        routes,
                        instruction.endpoint_path,
                        instruction.endpoint_methods,
                        instruction.endpoint_func_name,
                        is_deleted=True,
                    )
                    try:
                        _validate_no_repetitions_in_routes(deleted_routes)
                    except RouteAlreadyExistsError as e:
                        raise RouterGenerationError(
                            f'Endpoint "{list(instruction.endpoint_methods)} {instruction.endpoint_path}" you tried to '
                            f'restore in "{version_change.__name__}" has {len(e.routes)} applicable routes that could '
                            f"be restored. If you really have two routes with the same paths and methods, please, use "
                            f'"endpoint(..., func_name=...)" to distinguish between them. Function names of '
                            f"endpoints that can be restored: {[r.endpoint.__name__ for r in e.routes]}",
                        ) from e
                    for deleted_route in deleted_routes:
                        methods_to_which_we_applied_changes |= deleted_route.methods
                        deleted_route.tags.remove(_DELETED_ROUTE_TAG)

                        routes_that_never_existed = _get_routes(
                            self.routes_that_never_existed,
                            deleted_route.path,
                            deleted_route.methods,
                            deleted_route.endpoint.__name__,
                            is_deleted=True,
                        )
                        if len(routes_that_never_existed) == 1:
                            self.routes_that_never_existed.remove(routes_that_never_existed[0])
                        elif len(routes_that_never_existed) > 1:  # pragma: no cover
                            # I am not sure if it's possible to get to this error but I also don't want
                            # to remove it because I like its clarity very much
                            routes = routes_that_never_existed
                            raise RouterGenerationError(
                                f'Endpoint "{list(deleted_route.methods)} {deleted_route.path}" you tried to restore '
                                f'in "{version_change.__name__}" has {len(routes_that_never_existed)} applicable '
                                f"routes with the same function name and path that could be restored. This can cause "
                                f"problems during version generation. Specifically, Cadwyn won't be able to warn "
                                f"you when you deleted a route and never restored it. Please, make sure that "
                                f"functions for all these routes have different names: "
                                f"{[f'{r.endpoint.__module__}.{r.endpoint.__name__}' for r in routes]}",
                            )
                    err = (
                        'Endpoint "{endpoint_methods} {endpoint_path}" you tried to restore in'
                        ' "{version_change_name}" wasn\'t among the deleted routes'
                    )
                elif isinstance(instruction, EndpointHadInstruction):
                    for original_route in original_routes:
                        methods_to_which_we_applied_changes |= original_route.methods
                        _apply_endpoint_had_instruction(version_change, instruction, original_route)
                    err = (
                        'Endpoint "{endpoint_methods} {endpoint_path}" you tried to change in'
                        ' "{version_change_name}" doesn\'t exist'
                    )
                else:
                    assert_never(instruction)
                method_diff = methods_we_should_have_applied_changes_to - methods_to_which_we_applied_changes
                if method_diff:
                    raise RouterGenerationError(
                        err.format(
                            endpoint_methods=list(method_diff),
                            endpoint_path=instruction.endpoint_path,
                            version_change_name=version_change.__name__,
                        ),
                    )


def _extract_internal_request_schemas_from_router(
    router: fastapi.routing.APIRouter,
) -> dict[type[BaseModel], type[BaseModel]]:
    """Please note that this functon replaces internal bodies with original bodies in the router"""
    schema_to_internal_request_body_representation = {}

    def _extract_internal_request_schemas_from_annotations(annotations: dict[str, Any]):
        for key, annotation in annotations.items():
            if isinstance(annotation, type(Annotated[int, int])):  # pyright: ignore[reportArgumentType]
                args = get_args(annotation)
                if isinstance(args[1], type) and issubclass(  # pragma: no branch
                    args[1],
                    InternalRepresentationOf,  # pyright: ignore[reportDeprecated]
                ):
                    internal_schema = args[0]
                    original_schema = args[1].mro()[2]
                    schema_to_internal_request_body_representation[original_schema] = internal_schema
                    if len(args[2:]) != 0:
                        annotations[key] = Annotated[(original_schema, *args[2:])]
                    else:
                        annotations[key] = original_schema
        return annotations

    for route in router.routes:
        if isinstance(route, APIRoute):  # pragma: no branch
            route.endpoint = _modify_callable_annotations(
                route.endpoint,
                modify_annotations=_extract_internal_request_schemas_from_annotations,
                annotation_modifying_wrapper_factory=_copy_endpoint,
            )
            _remake_endpoint_dependencies(route)
    return schema_to_internal_request_body_representation


def _validate_no_repetitions_in_routes(routes: list[fastapi.routing.APIRoute]):
    route_map = {}

    for route in routes:
        route_info = _EndpointInfo(route.path, frozenset(route.methods))
        if route_info in route_map:
            raise RouteAlreadyExistsError(route, route_map[route_info])
        route_map[route_info] = route


@final
class _AnnotationTransformer:
    __slots__ = (
        "versions",
        "head_schemas_package",
        "head_version_dir",
        "latest_version_dir",
        "change_versions_of_a_non_container_annotation",
    )

    def __init__(self, head_schemas_package: ModuleType, versions: VersionBundle) -> None:
        self.versions = versions
        self.versions.head_schemas_package = head_schemas_package
        self.head_schemas_package = head_schemas_package
        self.head_version_dir = min(versions.versioned_directories_with_head)  # "head" < "v0000_00_00"
        self.latest_version_dir = max(versions.versioned_directories_with_head)  # "v2005_11_11" > "v2000_11_11"

        # This cache is not here for speeding things up. It's for preventing the creation of copies of the same object
        # because such copies could produce weird behaviors at runtime, especially if you/fastapi do any comparisons.
        # It's defined here and not on the method because of this: https://youtu.be/sVjtp6tGo0g
        self.change_versions_of_a_non_container_annotation = functools.cache(
            self._change_versions_of_a_non_container_annotation,
        )

    def migrate_router_to_version(self, router: fastapi.routing.APIRouter, version: Version):
        version_dir = get_version_dir_path(self.head_schemas_package, version.value)
        if not version_dir.is_dir():
            raise RouterGenerationError(
                f"Versioned schema directory '{version_dir}' does not exist.",
            )
        for route in router.routes:
            if not isinstance(route, fastapi.routing.APIRoute):
                continue
            self.migrate_route_to_version(route, version_dir)

    def migrate_route_to_version(
        self,
        route: fastapi.routing.APIRoute,
        version_dir: Path,
        *,
        ignore_response_model: bool = False,
    ):
        if route.response_model is not None and not ignore_response_model:
            route.response_model = self._change_version_of_annotations(route.response_model, version_dir)
            route.response_field = fastapi.utils.create_model_field(
                name="Response_" + route.unique_id,
                type_=route.response_model,
                mode="serialization",
            )
            route.secure_cloned_response_field = fastapi.utils.create_cloned_field(route.response_field)
        route.dependencies = self._change_version_of_annotations(route.dependencies, version_dir)
        route.endpoint = self._change_version_of_annotations(route.endpoint, version_dir)
        for callback in route.callbacks or []:
            if not isinstance(callback, APIRoute):
                continue
            self.migrate_route_to_version(callback, version_dir, ignore_response_model=ignore_response_model)
        _remake_endpoint_dependencies(route)

    def _change_versions_of_a_non_container_annotation(self, annotation: Any, version_dir: Path) -> Any:
        if isinstance(annotation, _BaseGenericAlias | GenericAlias):
            return get_origin(annotation)[
                tuple(self._change_version_of_annotations(arg, version_dir) for arg in get_args(annotation))
            ]
        elif isinstance(annotation, Depends):
            return Depends(
                self._change_version_of_annotations(annotation.dependency, version_dir),
                use_cache=annotation.use_cache,
            )
        elif isinstance(annotation, UnionType):
            getitem = typing.Union.__getitem__  # pyright: ignore[reportAttributeAccessIssue]
            return getitem(
                tuple(self._change_version_of_annotations(a, version_dir) for a in get_args(annotation)),
            )
        elif annotation is typing.Any or isinstance(annotation, typing.NewType):
            return annotation
        elif isinstance(annotation, type):
            if annotation.__module__ == "pydantic.main" and issubclass(annotation, BaseModel):
                return create_body_model(
                    fields=self._change_version_of_annotations(model_fields(annotation), version_dir).values(),
                    model_name=annotation.__name__,
                )
            return self._change_version_of_type(annotation, version_dir)
        elif callable(annotation):
            if type(annotation).__module__.startswith(
                ("fastapi.", "pydantic.", "pydantic_core.", "starlette.")
            ) or isinstance(annotation, fastapi.params.Security | fastapi.security.base.SecurityBase):
                return annotation

            def modifier(annotation: Any):
                return self._change_version_of_annotations(annotation, version_dir)

            return _modify_callable_annotations(
                annotation,
                modifier,
                modifier,
                annotation_modifying_wrapper_factory=_copy_function_through_class_based_wrapper,
            )
        else:
            return annotation

    def _change_version_of_annotations(self, annotation: Any, version_dir: Path) -> Any:
        """Recursively go through all annotations and if they were taken from any versioned package, change them to the
        annotations corresponding to the version_dir passed.

        So if we had a annotation "UserResponse" from "head" version, and we passed version_dir of "v1_0_1", it would
        replace "UserResponse" with the the same class but from the "v1_0_1" version.

        """
        if isinstance(annotation, dict):
            return {
                self._change_version_of_annotations(key, version_dir): self._change_version_of_annotations(
                    value,
                    version_dir,
                )
                for key, value in annotation.items()
            }

        elif isinstance(annotation, list | tuple):
            return type(annotation)(self._change_version_of_annotations(v, version_dir) for v in annotation)
        else:
            return self.change_versions_of_a_non_container_annotation(annotation, version_dir)

    def _change_version_of_type(self, annotation: type, version_dir: Path):
        if issubclass(annotation, BaseModel | Enum):
            if version_dir == self.latest_version_dir:
                source_file = inspect.getsourcefile(annotation)
                if source_file is None:  # pragma: no cover # I am not even sure how to cover this
                    warnings.warn(
                        f'Failed to find where the type annotation "{annotation}" is located.'
                        "Please, double check that it's located in the right directory",
                        stacklevel=7,
                    )
                else:
                    self._validate_source_file_is_located_in_template_dir(annotation, source_file)
            return get_another_version_of_cls(annotation, version_dir, self.versions.versioned_directories_with_head)
        else:
            return annotation

    def _validate_source_file_is_located_in_template_dir(self, annotation: type, source_file: str):
        template_dir = str(self.head_version_dir)
        dir_with_versions = str(self.head_version_dir.parent)
        # So if it is somewhere close to version dirs (either within them or next to them),
        # but not located in "head",
        # but also not located in any other version dir
        if (
            source_file.startswith(dir_with_versions)
            and not source_file.startswith(template_dir)
            and any(source_file.startswith(str(d)) for d in self.versions.versioned_directories_with_head)
        ):
            raise RouterGenerationError(
                f'"{annotation}" is not defined in "{self.head_version_dir}" even though it must be. '
                f'It is defined in "{Path(source_file).parent}". '
                "It probably means that you used a specific version of the class in fastapi dependencies "
                'or pydantic schemas instead of "head".',
            )


def _modify_callable_annotations(
    call: _Call,
    modify_annotations: Callable[[dict[str, Any]], dict[str, Any]] = lambda a: a,
    modify_defaults: Callable[[tuple[Any, ...]], tuple[Any, ...]] = lambda a: a,
    *,
    annotation_modifying_wrapper_factory: Callable[[_Call], _Call],
) -> _Call:
    annotation_modifying_wrapper = annotation_modifying_wrapper_factory(call)
    old_params = inspect.signature(call).parameters
    callable_annotations = annotation_modifying_wrapper.__annotations__
    annotation_modifying_wrapper.__annotations__ = modify_annotations(callable_annotations)
    annotation_modifying_wrapper.__defaults__ = modify_defaults(
        tuple(p.default for p in old_params.values() if p.default is not inspect.Signature.empty),
    )
    annotation_modifying_wrapper.__signature__ = _generate_signature(
        annotation_modifying_wrapper,
        old_params,
    )

    return annotation_modifying_wrapper


def _remake_endpoint_dependencies(route: fastapi.routing.APIRoute):
    # Unlike get_dependant, APIRoute is the public API of FastAPI and it's (almost) guaranteed to be stable.

    route_copy = fastapi.routing.APIRoute(route.path, route.endpoint, dependencies=route.dependencies)
    route.dependant = route_copy.dependant
    route.body_field = route_copy.body_field
    _add_request_and_response_params(route)


def _add_request_and_response_params(route: APIRoute):
    if not route.dependant.request_param_name:
        route.dependant.request_param_name = _CADWYN_REQUEST_PARAM_NAME
    if not route.dependant.response_param_name:
        route.dependant.response_param_name = _CADWYN_RESPONSE_PARAM_NAME


def _add_data_migrations_to_route(
    route: APIRoute,
    head_route: Any,
    template_body_field: type[BaseModel] | None,
    template_body_field_name: str | None,
    dependant_for_request_migrations: "Dependant",
    versions: VersionBundle,
):
    if not (route.dependant.request_param_name and route.dependant.response_param_name):  # pragma: no cover
        raise CadwynError(
            f"{route.dependant.request_param_name=}, {route.dependant.response_param_name=} "
            f"for route {list(route.methods)} {route.path} which should not be possible. Please, contact my author.",
        )

    route.endpoint = versions._versioned(
        template_body_field,
        template_body_field_name,
        route,
        head_route,
        dependant_for_request_migrations,
        request_param_name=route.dependant.request_param_name,
        response_param_name=route.dependant.response_param_name,
    )(route.endpoint)
    route.dependant.call = route.endpoint


def _apply_endpoint_had_instruction(
    version_change: type[VersionChange],
    instruction: EndpointHadInstruction,
    original_route: APIRoute,
):
    for attr_name in instruction.attributes.__dataclass_fields__:
        attr = getattr(instruction.attributes, attr_name)
        if attr is not Sentinel:
            if getattr(original_route, attr_name) == attr:
                raise RouterGenerationError(
                    f'Expected attribute "{attr_name}" of endpoint'
                    f' "{list(original_route.methods)} {original_route.path}"'
                    f' to be different in "{version_change.__name__}", but it was the same.'
                    " It means that your version change has no effect on the attribute"
                    " and can be removed.",
                )
            if attr_name == "path":
                original_path_params = {p.alias for p in original_route.dependant.path_params}
                new_path_params = set(re.findall("{(.*?)}", attr))
                if new_path_params != original_path_params:
                    raise RouterPathParamsModifiedError(
                        f'When altering the path of "{list(original_route.methods)} {original_route.path}" '
                        f'in "{version_change.__name__}", you have tried to change its path params '
                        f'from "{list(original_path_params)}" to "{list(new_path_params)}". It is not allowed to '
                        "change the path params of a route because the endpoint was created to handle the old path "
                        "params. In fact, there is no need to change them because the change of path params is "
                        "not a breaking change. If you really need to change the path params, you should create a "
                        "new route with the new path params and delete the old one.",
                    )
            setattr(original_route, attr_name, attr)


def _generate_signature(
    new_callable: Callable,
    old_params: MappingProxyType[str, inspect.Parameter],
):
    parameters = []
    default_counter = 0
    for param in old_params.values():
        if param.default is not inspect.Signature.empty:
            assert new_callable.__defaults__ is not None, (  # noqa: S101
                "Defaults cannot be None here. If it is, you have found a bug in Cadwyn. "
                "Please, report it in our issue tracker."
            )
            default = new_callable.__defaults__[default_counter]
            default_counter += 1
        else:
            default = inspect.Signature.empty
        parameters.append(
            inspect.Parameter(
                param.name,
                param.kind,
                default=default,
                annotation=new_callable.__annotations__.get(
                    param.name,
                    inspect.Signature.empty,
                ),
            ),
        )
    return inspect.Signature(
        parameters=parameters,
        return_annotation=new_callable.__annotations__.get(
            "return",
            inspect.Signature.empty,
        ),
    )


def _get_routes(
    routes: Sequence[BaseRoute],
    endpoint_path: str,
    endpoint_methods: set[str],
    endpoint_func_name: str | None = None,
    *,
    is_deleted: bool = False,
) -> list[fastapi.routing.APIRoute]:
    found_routes = []
    endpoint_path = endpoint_path.rstrip("/")
    for route in routes:
        if (
            isinstance(route, fastapi.routing.APIRoute)
            and route.path.rstrip("/") == endpoint_path
            and set(route.methods).issubset(endpoint_methods)
            and (endpoint_func_name is None or route.endpoint.__name__ == endpoint_func_name)
            and (_DELETED_ROUTE_TAG in route.tags) == is_deleted
        ):
            found_routes.append(route)
    return found_routes


def _get_route_from_func(
    routes: Sequence[BaseRoute],
    endpoint: Endpoint,
) -> fastapi.routing.APIRoute | None:
    for route in routes:
        if isinstance(route, fastapi.routing.APIRoute) and (route.endpoint == endpoint):
            return route
    return None


def _copy_endpoint(function: Any) -> Any:
    function = _unwrap_callable(function)
    function_copy: Any = types.FunctionType(
        function.__code__,
        function.__globals__,
        name=function.__name__,
        argdefs=function.__defaults__,
        closure=function.__closure__,
    )
    function_copy = functools.update_wrapper(function_copy, function)
    # Otherwise it will have the same signature as __wrapped__ due to how inspect module works
    del function_copy.__wrapped__

    function_copy._original_callable = function
    function.__kwdefaults__ = function.__kwdefaults__.copy() if function.__kwdefaults__ is not None else {}

    return function_copy


class _CallableWrapper:
    """__eq__ and __hash__ are needed to make sure that dependency overrides work correctly.
    They are based on putting dependencies (functions) as keys for the dictionary so if we want to be able to
    override the wrapper, we need to make sure that it is equivalent to the original in __hash__ and __eq__
    """

    def __init__(self, original_callable: Callable) -> None:
        super().__init__()
        self._original_callable = original_callable
        functools.update_wrapper(self, original_callable)

    @property
    def __globals__(self):
        """FastAPI uses __globals__ to resolve forward references in type hints
        It's supposed to be an attribute on the function but we use it as property to prevent python
        from trying to pickle globals when we deepcopy this wrapper
        """
        #
        return self._original_callable.__globals__

    def __call__(self, *args: Any, **kwargs: Any):
        return self._original_callable(*args, **kwargs)

    def __hash__(self):
        return hash(self._original_callable)

    def __eq__(self, value: object) -> bool:
        return self._original_callable == value  # pyright: ignore[reportUnnecessaryComparison]


class _AsyncCallableWrapper(_CallableWrapper):
    async def __call__(self, *args: Any, **kwargs: Any):
        return await self._original_callable(*args, **kwargs)


def _copy_function_through_class_based_wrapper(call: Any):
    """Separate from copy_endpoint because endpoints MUST be functions in FastAPI, they cannot be cls instances"""
    call = _unwrap_callable(call)

    if inspect.iscoroutinefunction(call):
        return _AsyncCallableWrapper(call)
    else:
        return _CallableWrapper(call)


def _unwrap_callable(call: Any) -> Any:
    while hasattr(call, "_original_callable"):
        call = call._original_callable
    if not isinstance(call, types.FunctionType | types.MethodType):
        # This means that the callable is actually an instance of a regular class
        call = call.__call__

    return call


def _route_has_a_simple_body_schema(route: APIRoute) -> bool:
    # Remember this: if len(body_params) == 1, then route.body_schema == route.dependant.body_params[0]
    return len(route.dependant.body_params) == 1
