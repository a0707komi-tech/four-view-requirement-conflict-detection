from __future__ import annotations

from conflict_detection.io.prompt_rendering import render_prompt_template
from conflict_detection.llm.response_parser import parse_json_response
from conflict_detection.orchestration.session_types import AgentDecision, DetectionPair


class BasePromptAgent:
    agent_name: str
    prompt_name: str

    def __init__(self, llm_client, prompt_loader) -> None:
        self.llm_client = llm_client
        self.prompt_loader = prompt_loader

    def build_user_prompt(self, template: str, pair: DetectionPair) -> str:
        return render_prompt_template(
            template,
            {
                "r1_text": pair.r1_text,
                "r2_text": pair.r2_text,
                "pair_id": pair.pair_id,
                "r1_id": pair.r1_id,
                "r2_id": pair.r2_id,
                "requirement_a": pair.r1_text,
                "requirement_b": pair.r2_text,
            },
        )

    def analyze_pair(self, pair: DetectionPair) -> AgentDecision:
        bundle = self.prompt_loader.load(self.prompt_name)
        temperature = bundle.metadata.temperature_policy.get("value")
        max_tokens = bundle.metadata.max_tokens_policy.get("value")
        system_prompt = bundle.system_prompt if bundle.metadata.supports_system_role else None
        user_prompt = self.build_user_prompt(bundle.user_prompt, pair)
        if hasattr(self.llm_client, "chat"):
            raw_text = self.llm_client.chat(
                self.agent_name,
                user_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                system_prompt=system_prompt,
            )
        else:
            raw_text = getattr(self.llm_client, self.agent_name).chat(
                user_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                system_prompt=system_prompt,
            )
        parsed = parse_json_response(raw_text)
        return AgentDecision(
            agent=self.agent_name,
            model=self.llm_client.get_model_name(self.agent_name),
            verdict=str(parsed.get("verdict", "uncertain")),
            confidence=float(parsed.get("confidence", 0.5)),
            reasoning=str(parsed.get("reasoning", "")),
            key_evidence=list(parsed.get("key_evidence", [])),
            assumptions=list(parsed.get("assumptions", [])),
            pairwise_conflict_grounded=_coerce_pairwise_conflict_grounded(parsed),
            raw_json=parsed,
            raw_text=raw_text,
        )


def _coerce_pairwise_conflict_grounded(parsed: dict) -> bool:
    value = parsed.get("pairwise_conflict_grounded", True)
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes"}
    return bool(value)
