from __future__ import annotations

from conflict_detection.io.prompt_rendering import render_prompt_template
from conflict_detection.llm.response_parser import parse_json_response
from conflict_detection.orchestration.session_types import CrossExamResult, DetectionPair
from conflict_detection.runtime.artifacts.phase1_summary import serialize_phase1_summary
from conflict_detection.runtime.artifacts.schemas import Phase1SummaryBundle


def execute_da_agent(
    llm_client,
    prompt_loader,
    pair: DetectionPair,
    phase1_bundle: Phase1SummaryBundle,
) -> CrossExamResult:
    bundle = prompt_loader.load("da")
    outputs = {
        agent_name: serialize_phase1_summary(summary)
        for agent_name, summary in phase1_bundle.summaries.items()
    }
    prompt = render_prompt_template(
        bundle.user_prompt,
        {
            "r1_text": pair.r1_text,
            "r2_text": pair.r2_text,
            "semantic_model": llm_client.get_model_name("semantic"),
            "semantic_output": outputs.get("semantic", ""),
            "logic_model": llm_client.get_model_name("logic"),
            "logic_output": outputs.get("logic", ""),
            "feasibility_model": llm_client.get_model_name("feasibility"),
            "feasibility_output": outputs.get("feasibility", ""),
            "goal_model": llm_client.get_model_name("goal"),
            "goal_output": outputs.get("goal", ""),
        },
    )
    raw_text = llm_client.da.chat(
        prompt,
        temperature=bundle.metadata.temperature_policy.get("value"),
        max_tokens=bundle.metadata.max_tokens_policy.get("value"),
        system_prompt=bundle.system_prompt if bundle.metadata.supports_system_role else None,
    )
    _validate_da_raw_response(raw_text)
    parsed = parse_json_response(raw_text)
    _validate_da_verdict(parsed, raw_text=raw_text)
    return CrossExamResult(
        da_verdict=parsed,
        target_agent=str(parsed["target_agent"]).strip(),
        challenge=str(parsed["challenge"]).strip(),
        rebuttal={},
    )


def _validate_da_raw_response(raw_text: str) -> None:
    if not isinstance(raw_text, str) or not raw_text.strip():
        raise ValueError("DA returned an empty response")


def _validate_da_verdict(da_verdict: dict[str, object], *, raw_text: str) -> None:
    if not isinstance(da_verdict, dict):
        raise ValueError("DA response did not parse into a JSON object")
    if da_verdict.get("_parse_error"):
        raise ValueError(f"DA response could not be parsed as JSON: {raw_text[:200]}")
    target_agent = str(da_verdict.get("target_agent", "")).strip()
    challenge = str(da_verdict.get("challenge", "")).strip()
    if target_agent not in {"semantic", "logic", "feasibility", "goal"}:
        raise ValueError(f"DA response missing valid target_agent: {target_agent or '<empty>'}")
    if not challenge:
        raise ValueError("DA response missing challenge")
