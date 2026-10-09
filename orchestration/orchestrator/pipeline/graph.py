"""
Pipeline Graph — orchestration/orchestrator/pipeline/graph.py
=============================================================
Builds and compiles the Riva-AGI LangGraph StateGraph.

  create_orchestrator() — single factory that wires all nodes, conditional
                          edges, and agent worker nodes, then compiles the graph.
"""
from langgraph.graph import StateGraph, START, END

from orchestration.orchestrator.infra.registry import registry

from .state import AgentState
from .nodes import (
    intent_node,
    planner_node,
    executor_node,
    reviewer_node,
    create_agent_node,
    aggregator_node,
    fallback_node,
)
from .edges import (
    route_after_intent,
    route_after_executor,
    route_after_worker,
    route_after_reviewer,
)


def sync_node(state: AgentState):
    return {}

def create_orchestrator():
    """
    Compile and return the Riva-AGI LangGraph orchestration graph using exact layers.
    """
    graph = StateGraph(AgentState)

    # ── Core Orchestration Nodes ───────────────────────────────────────────
    graph.add_node("intent", intent_node)
    graph.add_node("planner", planner_node)
    graph.add_node("reviewer", reviewer_node)
    
    # ── Sync Nodes ─────────────────────────────────────────────────────────
    graph.add_node("l1_sync", sync_node)
    graph.add_node("l2_sync", sync_node)
    graph.add_node("l3_sync", sync_node)

    # ── Dynamic Worker Agent Nodes ─────────────────────────────────────────
    workers = ["researcher", "designer", "coder", "qa", "devops", "seo_specialist", "writer"]
    for agent_name in workers:
        graph.add_node(agent_name, create_agent_node(agent_name))

    # ── Topology (L0 -> L1 -> L2 -> L3) ────────────────────────────────────
    
    # L0
    graph.add_edge(START, "intent")
    graph.add_edge(START, "planner")

    # L0 -> L1
    graph.add_edge("intent", "l1_sync")
    graph.add_edge("planner", "l1_sync")

    graph.add_edge("l1_sync", "researcher")
    graph.add_edge("l1_sync", "designer")
    graph.add_edge("l1_sync", "coder")

    # L1 -> L2
    graph.add_edge("researcher", "l2_sync")
    graph.add_edge("designer", "l2_sync")
    graph.add_edge("coder", "l2_sync")

    graph.add_edge("l2_sync", "qa")
    graph.add_edge("l2_sync", "devops")
    graph.add_edge("l2_sync", "seo_specialist")

    # L2 -> L3
    graph.add_edge("qa", "l3_sync")
    graph.add_edge("devops", "l3_sync")
    graph.add_edge("seo_specialist", "l3_sync")

    graph.add_edge("l3_sync", "reviewer")
    graph.add_edge("l3_sync", "writer")

    graph.add_edge("reviewer", END)
    graph.add_edge("writer", END)

    return graph.compile()
