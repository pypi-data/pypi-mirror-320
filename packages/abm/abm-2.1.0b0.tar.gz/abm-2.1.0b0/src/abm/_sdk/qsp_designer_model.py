from dataclasses import dataclass
from typing import Literal
from uuid import UUID

from serialite import AbstractSerializableMixin, abstract_serializable, serializable

from .ode_model import OdeModel


#######################################################
# Dosing
#######################################################
@abstract_serializable
@dataclass(frozen=True)
class DosingScheduleState:
    pass


@serializable
@dataclass(frozen=True)
class CustomDoseScheduleState(DosingScheduleState):
    dose_times: str


@abstract_serializable
@dataclass(frozen=True)
class DoseStateBase:
    pass


@serializable
@dataclass(frozen=True)
class BolusDoseState(DoseStateBase):
    amount: str
    unit: str


@serializable
@dataclass(frozen=True)
class GeneralBolusDoseState(DoseStateBase):
    amount: str


@serializable
@dataclass(frozen=True)
class GeneralInfusionState(DoseStateBase):
    infusion_rate: str
    duration: str


#######################################################
# Units
#######################################################
@serializable
@dataclass(frozen=True)
class BaseUnitState:
    symbol: str


@serializable
@dataclass(frozen=True)
class PrefixState:
    symbol: str
    definition: float


@serializable
@dataclass(frozen=True)
class NamedDerivedUnitState:
    symbol: str
    definition: str


@serializable
@dataclass(frozen=True)
class SimulationBaseUnitsState:
    base_unit_id: UUID
    simulation_base_unit: str


#######################################################
# Indices
#######################################################
@serializable
@dataclass(frozen=True)
class IndexIndexValuePairState:
    index_id: UUID
    index_value: int


@serializable
@dataclass(frozen=True)
class IndexRelativeValueState:
    id: UUID
    offset: int
    offset_wraps: bool
    index_value: str
    index_value_variable: str


@serializable
@dataclass(frozen=True)
class MultipleIndicesKeyState:
    pairs: list[IndexIndexValuePairState]
    runtime_pairs: list[IndexRelativeValueState]


@serializable
@dataclass(frozen=True)
class MultipleIndicesKeyValuePairStateFloat:
    key_state: MultipleIndicesKeyState
    value: float


@serializable
@dataclass(frozen=True)
class MultipleIndicesKeyValueCollectionStateFloat:
    index_ids: list[UUID]
    pairs: list[MultipleIndicesKeyValuePairStateFloat]


@serializable
@dataclass(frozen=True)
class MultipleIndicesKeyValuePairStateUuid:
    key_state: MultipleIndicesKeyState
    value: UUID


@serializable
@dataclass(frozen=True)
class MultipleIndicesKeyValueCollectionStateUuid:
    index_ids: list[UUID]
    pairs: list[MultipleIndicesKeyValuePairStateUuid]


@serializable
@dataclass(frozen=True)
class IndexCreatorIndexValuePairState:
    index_creator_id: UUID
    index_value: int


@serializable
@dataclass(frozen=True)
class MultipleIndicesKeyIndexCreatorsState:
    pairs: list[IndexCreatorIndexValuePairState]
    runtime_pairs: list[IndexRelativeValueState]


#######################################################
# Edge end types
#######################################################
@abstract_serializable
@dataclass(frozen=True)
class EdgeEndState:
    node_id: UUID


@serializable
@dataclass(frozen=True)
class NonSpecificEdgeEndState(EdgeEndState):
    each_updated_by_all: bool  # TODO: what does this mean?


@serializable
@dataclass(frozen=True)
class SpecificEdgeEndState(EdgeEndState):
    key: MultipleIndicesKeyIndexCreatorsState


#######################################################
# Node traits
#######################################################
@dataclass(frozen=True)
class Deactivatable:
    is_deactivated: bool


@dataclass(frozen=True)
class Exposable:
    is_exposed: bool


#######################################################
# Abstract graph entity type
#######################################################
@dataclass(frozen=True)
class GraphEntityState(AbstractSerializableMixin):
    id: UUID


#######################################################
# Abstract node types
#######################################################
@dataclass(frozen=True)
class LocalNodeState(GraphEntityState):
    name: str


@dataclass(frozen=True)
class LocalQuantityState(LocalNodeState, Exposable):
    values: MultipleIndicesKeyValueCollectionStateFloat
    unit: str
    attached_index_node_ids: list[UUID]
    is_output: bool


#######################################################
# Node types
#######################################################
@serializable
@dataclass(frozen=True)
class LocalAssignmentState(LocalNodeState, Deactivatable):
    is_initial_only: bool
    expression: str | None  # Can be None if is_deactivated is True
    condition: str | None = None
    alternative_expression: str | None = None


@serializable
@dataclass(frozen=True)
class LocalDosingPlanState(LocalNodeState, Exposable, Deactivatable):
    dosing_schedule_state: DosingScheduleState
    dose_state: DoseStateBase


@serializable
@dataclass(frozen=True)
class LocalEventState(LocalNodeState, Exposable, Deactivatable):
    condition: str
    expression: str


@serializable
@dataclass(frozen=True)
class LocalIndexNodeState(LocalNodeState):
    index_values: list[str]
    index_id: UUID
    priority: int


@serializable
@dataclass(frozen=True)
class LocalRuntimeIndexNodeState(LocalNodeState):
    range_expression: str
    index_id: UUID
    priority: int


@serializable
@dataclass(frozen=True)
class LocalReactionState(LocalNodeState, Exposable, Deactivatable):
    rate: str
    reverse_rate: str | None
    index_mapping: str | None


#######################################################
# Quantity node types
#######################################################
@serializable
@dataclass(frozen=True)
class LocalCompartmentState(LocalQuantityState):
    pass


@serializable
@dataclass(frozen=True)
class LocalParameterState(LocalQuantityState):
    pass


@serializable
@dataclass(frozen=True)
class LocalSpeciesState(LocalQuantityState):
    owner_id: UUID
    is_concentration: bool = False


#######################################################
# Abstract edge types
#######################################################
@dataclass(frozen=True)
class EdgeState(GraphEntityState):
    pass


#######################################################
# Edge types
#######################################################
@serializable
@dataclass(frozen=True)
class LocalAssignmentEdgeState(EdgeState):
    direction: Literal["FromAssignment", "ToAssignment", "ToAssignmentInhibitor"]
    quantity_end: EdgeEndState
    assignment_end: EdgeEndState


@serializable
@dataclass(frozen=True)
class DosingPlanEdgeState(EdgeState):
    quantity_end: EdgeEndState
    dosing_plan_end: EdgeEndState


@serializable
@dataclass(frozen=True)
class LocalEventEdgeState(EdgeState):
    edge_type: Literal["Growth", "Product", "Modifier"]
    quantity_end: EdgeEndState
    event_end: EdgeEndState


@serializable
@dataclass(frozen=True)
class ReactionParameterEdgeState(EdgeState):
    reaction_end: EdgeEndState
    parameter_end: EdgeEndState


@serializable
@dataclass(frozen=True)
class ReactionSpeciesEdgeState(EdgeState):
    stoichiometry: str
    edge_type: Literal["Substrate", "Product", "Modifier", "Growth", "Inhibitor"]
    reaction_end: EdgeEndState
    species_end: EdgeEndState


@serializable
@dataclass(frozen=True)
class QspDesignerModel(OdeModel):
    base_unit_states: list[BaseUnitState]
    prefix_states: list[PrefixState]
    named_derived_unit_states: list[NamedDerivedUnitState]
    simulation_base_units: list[SimulationBaseUnitsState | None]
    graph_entity_states: list[GraphEntityState]


# abstract_serializable only works on direct subclasses
# Recurse over subclasses to find them all
def get_all_subclasses(cls: type) -> dict[str, type]:
    subclasses = {}
    for subclass in cls.__subclasses__():
        if hasattr(subclass, "__fields_serializer__"):
            subclasses[subclass.__name__] = subclass
        subclasses.update(get_all_subclasses(subclass))
    return subclasses


GraphEntityState.__subclass_serializers__ = get_all_subclasses(GraphEntityState)
