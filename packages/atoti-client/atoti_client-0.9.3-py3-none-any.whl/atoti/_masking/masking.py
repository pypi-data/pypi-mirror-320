from __future__ import annotations

from collections.abc import Mapping, Set as AbstractSet
from typing import Final, final

from typing_extensions import override

from atoti._operation import combine_conditions
from atoti._operation.hierarchy_isin_condition import HierarchyIsinCondition

from .._collections import DelegatingMutableMapping
from .._constant import Constant
from .._identification import HierarchyIdentifier
from .._java_api import JavaApi
from .._operation import decombine_condition
from .masking_config import MaskingConfig


@final
class Masking(DelegatingMutableMapping[str, MaskingConfig]):
    def __init__(self, /, *, cube_name: str, java_api: JavaApi) -> None:
        self._cube_name: Final = cube_name
        self._java_api: Final = java_api

    @override
    def _get_delegate(self, *, key: str | None) -> Mapping[str, MaskingConfig]:
        result = self._java_api.get_masking_value(self._cube_name, role=key)

        cube_masking = {}
        for role, parsed_masking_config in result.items():
            only_conditions: list[HierarchyIsinCondition] = []
            exclude_conditions: list[HierarchyIsinCondition] = []

            for hierarchy_name, masking_rule in parsed_masking_config.items():
                hierarchy_identifier = HierarchyIdentifier._parse_java_description(
                    hierarchy_name
                )

                if masking_rule[True]:
                    only_conditions.extend(
                        HierarchyIsinCondition(
                            hierarchy_identifier,
                            {tuple(Constant.of(value) for value in values)},
                            level_names=(hierarchy_identifier.hierarchy_name,),
                        )
                        for values in masking_rule[True]
                    )

                if masking_rule[False]:
                    exclude_conditions.extend(
                        HierarchyIsinCondition(
                            hierarchy_identifier,
                            {tuple(Constant.of(value) for value in values)},
                            level_names=(hierarchy_identifier.hierarchy_name,),
                        )
                        for values in masking_rule[False]
                    )

            only = combine_conditions((only_conditions,)) if only_conditions else None
            exclude = (
                combine_conditions((exclude_conditions,))
                if exclude_conditions
                else None
            )
            cube_masking[role] = MaskingConfig(only=only, exclude=exclude)

        return cube_masking

    @override
    def _update_delegate(self, other: Mapping[str, MaskingConfig], /) -> None:
        for key, value in other.items():
            includes = {}
            excludes = {}

            if value.only is not None:
                include_conditions = decombine_condition(
                    value.only,
                    allowed_subject_types=(HierarchyIdentifier,),
                    allowed_combination_operators=("and",),
                    allowed_target_types=(Constant,),
                )[0][2]

                for include in include_conditions:
                    includes[include.subject._java_description] = include.member_paths

            if value.exclude is not None:
                excludes_conditions = decombine_condition(
                    value.exclude,
                    allowed_subject_types=(HierarchyIdentifier,),
                    allowed_combination_operators=("and",),
                    allowed_target_types=(Constant,),
                )[0][2]

                for exclude in excludes_conditions:
                    excludes[exclude.subject._java_description] = exclude.member_paths

            self._java_api.set_masking_value(
                includes,
                excludes,
                cube_name=self._cube_name,
                role=key,
            )

    @override
    def _delete_delegate_keys(self, keys: AbstractSet[str], /) -> None:
        raise NotImplementedError("Cannot delete masking value.")
