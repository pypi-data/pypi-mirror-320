"""Lifelong Learning in Flexible Ontologies (LLFO) package."""

from llfo.core.ontology import FlexibleOntology, OntologyNode
from llfo.core.learner import LifelongLearner, TaskEncoder
from llfo.core.transfer import KnowledgeTransfer
from llfo.core.metrics import OntologyMetrics

__version__ = "0.1.0"

__all__ = [
    'FlexibleOntology',
    'OntologyNode',
    'LifelongLearner',
    'TaskEncoder',
    'KnowledgeTransfer',
    'OntologyMetrics'
]
