import json
import os
import sys
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()


def _build_model():
    return ChatGroq(model="llama-3.1-8b-instant")


def get_ai_review(code_string: str, issues: dict, language: str = "Python") -> dict:
    model = _build_model()
    prompt = PromptTemplate(
        input_variables=["code_string", "issues", "language"],
        template=(
            "You are an expert code reviewer.\n"
            "Language: {language}\n"
            "Original Code:\n{code_string}\n\n"
            "Static Analysis Issues (dict):\n{issues}\n\n"
            "Return EXACTLY this JSON schema:\n"
            "{{\n"
            "  \"quality_grade\": \"B\",\n"
            "  \"analysis_summary\": \"...\",\n"
            "  \"issues_found\": [\"Unused import: math\", \"Unused function: unused_function\"],\n"
            "  \"improved_code\": \"...full cleaned up code...\",\n"
            "  \"detailed_explanations\": {{\n"
            "    \"scalability_impact\": \"...\",\n"
            "    \"time_space_complexity\": \"O(1) for all operations...\",\n"
            "    \"security_vulnerabilities\": \"...\",\n"
            "    \"best_practices\": \"...\"\n"
            "  }}\n"
            "}}\n\n"
            "Respond ONLY with valid JSON. No markdown fences. No explanation outside JSON."
        ),
    )

    final_prompt = prompt.format(
        code_string=code_string,
        issues=json.dumps(issues, ensure_ascii=True),
        language=language,
    )

    try:
        result = model.invoke(final_prompt)
        content = result.content if hasattr(result, "content") else str(result)
        parsed = json.loads(content)
        if not isinstance(parsed, dict):
            raise ValueError("Model response is not a JSON object")

        improved_code = parsed.get("improved_code", code_string)
        if not isinstance(improved_code, str):
            improved_code = json.dumps(improved_code, ensure_ascii=True)

        issues_found = parsed.get("issues_found", [])
        if not isinstance(issues_found, list):
            issues_found = [str(issues_found)]

        detailed_explanations = parsed.get("detailed_explanations", {})
        if not isinstance(detailed_explanations, dict):
            detailed_explanations = {}

        return {
            "quality_grade": str(parsed.get("quality_grade", "N/A")),
            "analysis_summary": str(parsed.get("analysis_summary", "Parse error")),
            "issues_found": [str(item) for item in issues_found],
            "improved_code": improved_code,
            "detailed_explanations": detailed_explanations,
        }
    except Exception:
        return {
            "quality_grade": "N/A",
            "analysis_summary": "Parse error",
            "issues_found": [],
            "improved_code": code_string,
            "detailed_explanations": {},
        }


def ask_ai_assistant(question: str, code_context: str, chat_history: list) -> str:
    model = _build_model()
    messages = [
        SystemMessage(
            content=(
                "You are an expert code reviewer. The user is asking about their code.\n"
                f"Code context:\n{code_context}"
            )
        )
    ]

    for item in chat_history:
        role = item.get("role", "").lower()
        content = item.get("content", "")
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))

    messages.append(HumanMessage(content=question))

    try:
        response = model.invoke(messages)
        return response.content if hasattr(response, "content") else str(response)
    except Exception as exc:
        return f"Unable to get AI response: {exc}"
