"""
explainability/llm_explainer.py
================================
Step 2 of Day 5: LLM-generated natural language explanation.

WHAT THIS DOES:
  Takes the SHAP values from shap_explainer.py and sends them to
  a locally-running Ollama LLM (llama3.2:3b).  Gets back a 2-sentence
  plain English explanation like:

  "This transaction is flagged as high-risk due to an unusually large
  amount of $12,500 combined with a velocity pattern suggesting rapid
  card testing.  The unrecognised email domain and missing billing
  address further indicate a likely stolen card scenario."

WHY LOCAL OLLAMA (not cloud API):
  - Free — no API costs
  - Private — transaction data never leaves the machine
  - llama3.2:3b gives good quality explanations at 2GB RAM

OLLAMA API:
  POST http://localhost:11434/api/generate
  { "model": "llama3.2:3b", "prompt": "...", "stream": false }
  Response: { "response": "the text..." }

FALLBACK:
  If Ollama is not running or times out, returns a rule-based
  explanation built directly from SHAP values.  Never crashes.
"""

import httpx
from typing import Any, Dict


class LLMExplainer:
    """
    Connects to Ollama and generates natural language fraud explanations.
    """

    def __init__(
        self,
        model:   str = "qwen2.5:1.5b",
        host:    str = "http://localhost:11434",
        timeout: int = 25,          # seconds — LLM on CPU needs time
    ):
        self.model   = model
        self.host    = host.rstrip("/")
        self.timeout = timeout

        print(f"  [LLMExplainer] Connecting to Ollama at {self.host}...")
        self._verify_connection()
        print(f"  [LLMExplainer] Ready. Model: {self.model}")

    # ──────────────────────────────────────────────────────
    def _verify_connection(self):
        """Check Ollama is running. Raise a clear error if not."""
        try:
            r = httpx.get(f"{self.host}/api/tags", timeout=5)
            r.raise_for_status()
        except Exception:
            raise RuntimeError(
                "\n\nCannot connect to Ollama at http://localhost:11434\n"
                "Fix: open a NEW PowerShell window and run:  ollama serve\n"
                "Then re-run this script.\n"
            )

    # ──────────────────────────────────────────────────────
    def _build_prompt(
        self,
        transaction:      Dict[str, Any],
        shap_results:     dict,
        fraud_probability: float,
    ) -> str:
        """
        Build a focused prompt that produces a concise 2-sentence explanation.
        The prompt is structured so the LLM acts as a fraud analyst,
        not a general assistant.
        """
        amt      = transaction.get("TransactionAmt", "unknown")
        card_type = transaction.get("card4", "unknown")
        email    = transaction.get("P_emaildomain", "unknown")

        # Format top features for the prompt
        top = shap_results.get("top_features", [])
        feat_lines = []
        for item in top:
            direction = "INCREASES fraud risk" if item["shap_value"] > 0 else "DECREASES fraud risk"
            feat_lines.append(
                f"  - {item['feature']}: {item['shap_value']:+.4f} ({direction})"
            )
        features_text = "\n".join(feat_lines) if feat_lines else "  - No significant features"

        prompt = f"""You are a financial fraud analyst writing a brief explanation for a fraud alert.

Transaction details:
  Amount: ${amt}
  Card type: {card_type}
  Email domain: {email}
  Fraud probability: {fraud_probability:.1%}

Top SHAP feature contributions (positive = increases fraud risk):
{features_text}

Write exactly 2 sentences explaining why this transaction is suspicious. 
Be specific about the features. Do not use bullet points. Do not say "I" or "The model".
Start directly with the explanation."""

        return prompt

    # ──────────────────────────────────────────────────────
    def _fallback_explanation(
        self,
        shap_results:      dict,
        fraud_probability: float,
    ) -> str:
        """
        Rule-based fallback if Ollama is unavailable or times out.
        Always returns something meaningful — never crashes.
        """
        top = shap_results.get("top_features", [])
        risk_factors = [
            f['feature'] for f in top if f['shap_value'] > 0
        ]
        risk_str = ", ".join(risk_factors[:3]) if risk_factors else "multiple features"

        level = (
            "critically high"   if fraud_probability >= 0.9 else
            "very high"         if fraud_probability >= 0.75 else
            "high"
        )

        return (
            f"This transaction has a {level} fraud probability of "
            f"{fraud_probability:.1%} driven primarily by {risk_str}. "
            f"Immediate review is recommended before processing."
        )

    # ──────────────────────────────────────────────────────
    
    # ──────────────────────────────────────────────────────

    def explain(
        self,
        transaction: Dict[str, Any],
        shap_results: dict,
        fraud_probability: float,
    ) -> str:
        """
        Generate a 2-sentence plain English fraud explanation.

        Args:
            transaction:       Raw transaction dict
            shap_results:      Output from SHAPExplainer.explain()
            fraud_probability: Final ensemble fraud score (0–1)

        Returns:
            str: 2-sentence explanation for fraud analysts
        """

        # Safety check — never block the pipeline
        try:
            prompt = self._build_prompt(
                transaction,
                shap_results,
                fraud_probability
            )
        except Exception:
            return self._fallback_explanation(
                shap_results,
                fraud_probability
            )

        try:
            response = httpx.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 120,
                    },
                },
                timeout=self.timeout,
            )

            response.raise_for_status()

            narrative = (
                response.json()
                .get("response", "")
                .strip()
            )

            # If the LLM output is unusable, fall back
            if len(narrative) < 20:
                return self._fallback_explanation(
                    shap_results,
                    fraud_probability
                )

            return narrative

        except httpx.TimeoutException:
            print(
                "  [LLMExplainer] WARNING: "
                "Ollama timed out — using fallback explanation"
            )
            return self._fallback_explanation(
                shap_results,
                fraud_probability
            )

        except Exception as e:
            print(
                f"  [LLMExplainer] WARNING: "
                f"LLM call failed ({e}) — using fallback"
            )
            return self._fallback_explanation(
                shap_results,
                fraud_probability
            )