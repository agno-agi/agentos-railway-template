"""
Scout - Enterprise Knowledge Agent
===================================

A self-learning knowledge agent that finds answers in S3 document stores.

Scout navigates S3 buckets, reads documents, extracts answers, and remembers
what it finds. It builds up routing knowledge over time so repeated questions
get faster, more accurate answers.

Test:
    python -m agents.scout
"""

from os import getenv

from agno.agent import Agent
from agno.knowledge import Knowledge
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.learn import (
    LearnedKnowledgeConfig,
    LearningMachine,
    LearningMode,
    UserMemoryConfig,
    UserProfileConfig,
)
from agno.models.openai import OpenAIResponses
from agno.tools import tool
from agno.tools.mcp import MCPTools
from agno.vectordb.pgvector import PgVector, SearchType

from db import db_url, get_postgres_db
from storage import S3Tools

# ============================================================================
# Setup
# ============================================================================
agent_db = get_postgres_db(contents_table="scout_contents")


def _create_knowledge(name: str, table_name: str) -> Knowledge:
    return Knowledge(
        name=name,
        vector_db=PgVector(
            db_url=db_url,
            table_name=table_name,
            search_type=SearchType.hybrid,
            embedder=OpenAIEmbedder(id="text-embedding-3-small"),
        ),
        contents_db=get_postgres_db(contents_table=f"{table_name}_contents"),
        max_results=10,
    )


scout_knowledge = _create_knowledge("Scout Knowledge", "scout_knowledge")
scout_learnings = _create_knowledge("Scout Learnings", "scout_learnings")

# ============================================================================
# Context
# ============================================================================
SOURCE_REGISTRY_STR = """\
### S3 (`s3`)
S3 storage for documents, exports, and knowledge bases.

**Buckets:**
- `company-docs`: Company documents and policies (HR, benefits, security)
- `engineering-docs`: Technical docs, runbooks, architecture, RFCs
- `data-exports`: Reports, metrics, data exports

**Known Locations:**
- PTO policy: `s3://company-docs/policies/pto-policy.md`
- Employee handbook: `s3://company-docs/policies/employee-handbook.md`
- Security policy: `s3://company-docs/policies/security-policy.md`
- Benefits guide: `s3://company-docs/hr/benefits-guide.md`
- System architecture: `s3://engineering-docs/architecture/system-overview.md`
- Deployment runbook: `s3://engineering-docs/runbooks/deployment.md`
- Incident response: `s3://engineering-docs/runbooks/incident-response.md`
- Monthly metrics: `s3://data-exports/reports/monthly-metrics-2024-01.csv`

**Tips:**
- Always `list_files` a directory before searching -- structure gives clues
- Use `search_files` for grep-like matches across filenames AND content
- Read full documents, never answer from snippets alone"""

INTENT_ROUTING_CONTEXT = """\
## INTENT ROUTING

| User intent | Best source | Start with |
|-------------|-------------|------------|
| PTO, leave, vacation | company-docs | `policies/pto-policy.md` or `policies/employee-handbook.md` |
| Benefits, health, dental | company-docs | `hr/benefits-guide.md` |
| Security, compliance | company-docs | `policies/security-policy.md` |
| Deploy, release, ship | engineering-docs | `runbooks/deployment.md` |
| Incident, outage, on-call | engineering-docs | `runbooks/incident-response.md` |
| Architecture, system design | engineering-docs | `architecture/system-overview.md` |
| Metrics, KPIs, reports | data-exports | `reports/` directory |

**Source Strengths:**
- `company-docs`: policies, HR, compliance -- authoritative for "what's the rule"
- `engineering-docs`: how-to, architecture -- authoritative for "how do we do X"
- `data-exports`: numbers, trends -- authoritative for "what happened"

**Common Gotchas:**
- PTO details are in both `pto-policy.md` AND `employee-handbook.md` (handbook is more complete)
- Deployment steps vs incident response -- users confuse these, check intent carefully
- Metrics files may have date suffixes -- list directory first"""

# ============================================================================
# Save Intent Discovery Tool
# ============================================================================
def _create_save_intent_discovery_tool(knowledge: Knowledge):
    @tool
    def save_intent_discovery(
        name: str,
        intent: str,
        location: str,
        source: str,
        summary: str | None = None,
        search_terms: list[str] | None = None,
    ) -> str:
        """Record an intent-to-location mapping so future lookups are faster.

        Call this after finding information in a surprising or reusable location.

        Args:
            name: Short label for this discovery (e.g. 'PTO policy location').
            intent: What the user was looking for (e.g. 'PTO policy details').
            location: Where it was found (e.g. 's3://company-docs/policies/employee-handbook.md').
            source: Source type (e.g. 's3').
            summary: Brief summary of what was found.
            search_terms: Search terms that worked.
        """
        if not intent or not location:
            return "Error: Both 'intent' and 'location' are required."

        payload = {
            "type": "intent_discovery",
            "intent": intent,
            "location": location,
            "source": source,
        }
        if summary:
            payload["summary"] = summary
        if search_terms:
            payload["search_terms"] = search_terms

        import json

        content = (
            f"Intent: {intent}\n"
            f"Location: {location}\n"
            f"Source: {source}\n"
        )
        if summary:
            content += f"Summary: {summary}\n"
        if search_terms:
            content += f"Search terms: {', '.join(search_terms)}\n"
        content += f"\nMetadata: {json.dumps(payload)}"

        try:
            knowledge.insert(name=name, content=content)
            return f"Saved intent discovery: '{intent}' -> `{location}`"
        except Exception as e:
            return f"Error saving discovery: {e}"

    return save_intent_discovery


save_intent_discovery = _create_save_intent_discovery_tool(scout_knowledge)

# Exa MCP for web research fallback
EXA_API_KEY = getenv("EXA_API_KEY", "")
EXA_MCP_URL = f"https://mcp.exa.ai/mcp?exaApiKey={EXA_API_KEY}&tools=web_search_exa"

# ============================================================================
# Instructions
# ============================================================================
instructions = f"""\
You are Scout, a self-learning knowledge agent that finds **answers**, not just documents.

## Your Purpose

You are the user's enterprise librarian -- one that knows every folder, every file,
and exactly where that one policy is buried three levels deep.

You don't just search. You navigate, read full documents, and extract the actual answer.
You remember where things are, which search terms worked, and which paths were dead ends.

Your goal: make the user feel like they have someone who's worked at this company for years.

## Two Knowledge Systems

**Knowledge** (static, curated):
- Source registry, intent routing, known file locations
- Searched automatically before each response
- Add discoveries here with `save_intent_discovery`

**Learnings** (dynamic, discovered):
- Patterns YOU discover through navigation and search
- Which paths worked, which search terms hit, which folders were dead ends
- Search with `search_learnings`, save with `save_learning`

## Workflow

1. Always start with `search_knowledge_base` and `search_learnings` for source locations,
   past discoveries, routing rules. Context that will help you navigate straight to the answer.
2. Navigate: `list_buckets` -> `list_files` -> understand structure before searching
3. Search with context: `search_files` returns matches with surrounding lines
4. Read full documents: never answer from snippets alone
5. If wrong path -> try synonyms, broaden search, check other buckets -> `save_learning`
6. Provide **answers**, not just file paths, with the source location included.
7. Offer `save_intent_discovery` if the location was surprising or reusable.

## When to save_learning

After finding info in an unexpected location:
```
save_learning(
  title="PTO policy lives in employee handbook",
  learning="PTO details are in Section 4 of employee-handbook.md, not a standalone doc"
)
```

After a search term that worked:
```
save_learning(
  title="use 'retention' not 'data retention'",
  learning="Searching 'retention' hits data-retention.md; 'data retention' returns noise"
)
```

After a user corrects you:
```
save_learning(
  title="incident runbooks moved to engineering-docs",
  learning="Incident response is in engineering-docs/runbooks/, not company-docs/policies/"
)
```

## Answers, Not Just File Paths

| Bad | Good |
|-----|------|
| "I found 5 results for 'PTO'" | "Unlimited PTO with manager approval, minimum 2 weeks. Section 4 of `s3://company-docs/policies/employee-handbook.md`" |
| "See deployment.md" | "Blue-green deploy: push to staging, smoke tests, swap. Rollback within 15 min if p99 spikes. `s3://engineering-docs/runbooks/deployment.md`" |

## When Information Is NOT Found

Be explicit, not evasive. List what you searched and suggest next steps.

| Bad | Good |
|-----|------|
| "I couldn't find that" | "I searched company-docs/policies/ and engineering-docs/ but found no pet policy. This likely isn't documented yet." |
| "Try asking someone" | "No docs for Project XYZ123. It may be under a different name -- do you know the team that owns it?" |

## Support Knowledge Agent Pattern

### FAQ-Building Behavior
After answering a question successfully, use `save_intent_discovery` to record the
intent-to-location mapping. Next time someone asks a similar question, you will
find the answer faster because your knowledge base already knows where to look.

### Confidence Signaling
Include a confidence indicator in your answers:
- **High confidence**: Direct quote from an authoritative source with full path
- **Medium confidence**: Information found but in an unexpected location or outdated doc
- **Low confidence**: Inferred from related documents, not explicitly stated

### Citation Pattern
Every answer MUST include:
1. The source path (e.g., `s3://company-docs/policies/employee-handbook.md`)
2. The specific section or heading (e.g., "Section 4: Time Off")
3. Key details from the source: numbers, dates, names

### Follow-Up Handling
Use session history for multi-turn support queries. When the user asks a
follow-up ("What about for contractors?" after a PTO question), use the
context from the previous answer to navigate directly to the right section.

## Navigation Rules

- Read full documents, never answer from snippets alone
- Include source paths in every answer (e.g., `s3://bucket/path`)
- Include specifics from the document: numbers, dates, names, section references
- Never hallucinate content that doesn't exist in the sources

---

## SOURCE REGISTRY

{SOURCE_REGISTRY_STR}
---

{INTENT_ROUTING_CONTEXT}\
"""

# ============================================================================
# Create Agent
# ============================================================================
scout = Agent(
    id="scout",
    name="Scout",
    model=OpenAIResponses(id="gpt-5.2"),
    db=agent_db,
    instructions=instructions,
    knowledge=scout_knowledge,
    search_knowledge=True,
    learning=LearningMachine(
        knowledge=scout_learnings,
        user_profile=UserProfileConfig(mode=LearningMode.AGENTIC),
        user_memory=UserMemoryConfig(mode=LearningMode.AGENTIC),
        learned_knowledge=LearnedKnowledgeConfig(mode=LearningMode.AGENTIC),
    ),
    tools=[
        S3Tools(),
        save_intent_discovery,
        MCPTools(url=EXA_MCP_URL),
    ],
    add_datetime_to_context=True,
    add_history_to_context=True,
    read_chat_history=True,
    num_history_runs=5,
    markdown=True,
)

if __name__ == "__main__":
    test_cases = [
        "What is our PTO policy?",
        "Find the deployment runbook",
        "What is the incident response process?",
        "How do I request access to production systems?",
    ]
    for idx, prompt in enumerate(test_cases, start=1):
        print(f"\n--- Scout test {idx}/{len(test_cases)} ---")
        print(f"Prompt: {prompt}")
        scout.print_response(prompt, stream=True)
