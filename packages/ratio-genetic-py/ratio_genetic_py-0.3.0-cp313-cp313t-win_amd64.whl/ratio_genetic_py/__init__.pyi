"""Typings for the bindings."""
from enum import Enum
from typing import List, Optional, Set, Union

class FitnessStatistics:
    def __init__(
        self,
        size: int,
        min: float,
        max: float,
        sum: float,
        mean: float,
        variance: float,
    ) -> None: ...

class Chromosome:
    def __init__(self, genes: List[int], fitness: Optional[float]) -> None: ...

class Population:
    def __init__(self, chromosomes: List[Chromosome], generation: int) -> None: ...

class HallOfFame:
    def __init__(
        self, chromosomes: List[Chromosome], uniques: Set[List[int]], capacity: int
    ) -> None: ...

class Lineage:
    def __init__(
        self,
        generations: List[Population],
        records: List[FitnessStatistics],
        hall_of_fame: HallOfFame,
        n_generations: Optional[int],
        n_records: Optional[int],
    ) -> None: ...

class ConvergenceKinds(Enum):
    Never = "Never"

class CrossoverKinds(Enum):
    IPX = "IPX"
    Point = "Point"
    Blend = "Blend"
    SimulatedBinary = "SimulatedBinary"

class CrossoverBlend:
    def __init__(self, alpha: float) -> None: ...

class CrossoverSimulatedBinary:
    def __init__(self, eta: float) -> None: ...

class EvaluatorKinds(Enum):
    FeedbackDistance = "FeedbackDistance"
    FeedbackMarks = "FeedbackMarks"
    LowerLeftDistance = "LowerLeftDistance"
    Value = "Value"

class EvaluatorMatrix:
    def __init__(
        self, kind: EvaluatorKinds, matrix: List[float], offset: Optional[int]
    ) -> None: ...
    @staticmethod
    def kinds() -> Set[EvaluatorKinds]: ...

class EvaluatorValue:
    def __init__(self, value: float) -> None: ...

class GeneratorKinds(Enum):
    RandomSequence = "RandomSequence"

class MutatorKinds(Enum):
    Swap = "Swap"

class MutatorSwap:
    def __init__(self, p_swap: float) -> None: ...

class RecorderKinds(Enum):
    FitnessStatistics = "FitnessStatistics"
    HdrHistogram = "HdrHistogram"

class RecorderHdrHistogram:
    def __init__(self, sigfig: int) -> None: ...

class SelectorKinds(Enum):
    Roulette = "Roulette"
    Random = "Random"

class SequencingSettings:
    def __init__(
        self,
        n_genes: int,
        p_crossover: float,
        p_mutation: float,
        n_chromosomes: Optional[int] = None,
        n_generations: Optional[int] = None,
        n_records: Optional[int] = None,
        n_hall_of_fame: Optional[int] = None,
    ) -> None: ...

def sequence_sga(
    settings: SequencingSettings,
    generator: GeneratorKinds,
    evaluator: Union[EvaluatorMatrix, EvaluatorValue],
    recorder: Union[RecorderHdrHistogram, RecorderKinds],
    selector: SelectorKinds,
    crossover: Union[CrossoverBlend, CrossoverSimulatedBinary, CrossoverKinds],
    mutator: MutatorSwap,
) -> Lineage: ...
