from __future__ import annotations

from conflict_detection.io.prompt_rendering import render_prompt_template
from conflict_detection.llm.response_parser import parse_json_response
from conflict_detection.orchestration.session_types import DetectionPair
from conflict_detection.runtime.artifacts.debate_summary import serialize_rebuttal_summary
from conflict_detection.runtime.artifacts.phase1_summary import serialize_phase1_summary
from conflict_detection.runtime.artifacts.schemas import ArbiterInputBundle


def execute_arbiter_agent(
    llm_client,
    prompt_loader,
    pair: DetectionPair,
    arbiter_bundle: ArbiterInputBundle,
) -> dict:
    bundle = prompt_loader.load("arbiter")
    outputs = {
        agent_name: serialize_phase1_summary(summary)
        for agent_name, summary in arbiter_bundle.phase1_summaries.items()
    }
    prompt = render_prompt_template(
        bundle.user_prompt,
        {
            "r1_text": pair.r1_text,
            "r2_text": pair.r2_text,
            "semantic_label": f"Semantic Agent ({llm_client.get_model_name('semantic')})",
            "semantic_output": outputs.get("semantic", ""),
            "logic_label": f"Logic Agent ({llm_client.get_model_name('logic')})",
            "logic_output": outputs.get("logic", ""),
            "feasibility_label": f"Feasibility Agent ({llm_client.get_model_name('feasibility')})",
            "feasibility_output": outputs.get("feasibility", ""),
            "goal_label": f"Goal Agent ({llm_client.get_model_name('goal')})",
            "goal_output": outputs.get("goal", ""),
            "target_agent": arbiter_bundle.da_challenge.target_agent,
            "challenge": arbiter_bundle.da_challenge.challenge,
            "rebuttal": serialize_rebuttal_summary(arbiter_bundle.rebuttal),
        },
    )
    raw_text = llm_client.arbiter.chat(
        prompt,
        temperature=bundle.metadata.temperature_policy.get("value"),
        max_tokens=bundle.metadata.max_tokens_policy.get("value"),
        system_prompt=bundle.system_prompt if bundle.metadata.supports_system_role else None,
    )
    return parse_json_response(raw_text)
