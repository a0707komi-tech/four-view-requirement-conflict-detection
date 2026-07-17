from __future__ import annotations

from conflict_detection.io.prompt_rendering import render_prompt_template
from conflict_detection.llm.response_parser import parse_json_response
from conflict_detection.orchestration.session_types import CrossExamResult, DetectionPair
from conflict_detection.runtime.artifacts.phase1_summary import serialize_phase1_summary
from conflict_detection.runtime.artifacts.schemas import DaChallengeArtifact, Phase1SummaryBundle


def execute_rebuttal_agent(
    llm_client,
    prompt_loader,
    pair: DetectionPair,
    phase1_bundle: Phase1SummaryBundle,
    da_artifact: DaChallengeArtifact,
) -> CrossExamResult:
    bundle = prompt_loader.load("rebuttal")
    outputs = {
        agent_name: serialize_phase1_summary(summary)
        for agent_name, summary in phase1_bundle.summaries.items()
    }
    target_agent = da_artifact.target_agent
    challenge = da_artifact.challenge
    role_map = {
        "semantic": llm_client.semantic,
        "logic": llm_client.logic,
        "feasibility": llm_client.feasibility,
        "goal": llm_client.goal,
    }
    raw_text = role_map.get(target_agent, llm_client.logic).chat(
        render_prompt_template(
            bundle.user_prompt,
            {
                "r1_text": pair.r1_text,
                "r2_text": pair.r2_text,
                "original_output": outputs.get(target_agent, ""),
                "challenge": challenge,
            },
        ),
        temperature=bundle.metadata.temperature_policy.get("value"),
        max_tokens=bundle.metadata.max_tokens_policy.get("value"),
        system_prompt=bundle.system_prompt if bundle.metadata.supports_system_role else None,
    )
    return CrossExamResult(
        da_verdict={},
        target_agent=target_agent,
        challenge=challenge,
        rebuttal=parse_json_response(raw_text),
    )
