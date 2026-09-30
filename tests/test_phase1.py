"""Focused Phase 1 contract tests."""

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from secureagentflow.llm import APILLM, MockLLM
from secureagentflow.messaging import MessageEnvelope


def test_message_envelope_signs_and_detects_tampering() -> None:
    private_key = Ed25519PrivateKey.generate()
    envelope = MessageEnvelope(
        trace_id="trace-1",
        sender="extractor",
        receiver="orchestrator",
        type="facts",
        payload={"facts": ["hemoglobin=12"]},
    ).sign(private_key)

    assert envelope.verify(private_key.public_key())
    envelope.payload["facts"] = ["hemoglobin=2"]
    assert not envelope.verify(private_key.public_key())


def test_mock_llm_is_deterministic() -> None:
    client = MockLLM()
    first = client.generate("Extract key facts from this document")
    second = client.generate("Extract key facts from this document")

    assert first == second
    assert first.text == '{"facts": [], "source": "mock"}'


def test_api_llm_requires_environment_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        APILLM()
