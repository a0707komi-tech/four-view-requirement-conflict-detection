# Architecture

## Components

1. **Preprocessing** loads requirement CSVs, cleans text, forms unordered pairs, calculates similarity, builds duplicate groups, and routes pairs.
2. **Phase-1** runs semantic, logic, feasibility, and goal views independently for each candidate pair.
3. **Consensus** finalizes only unanimous four-view `compatible` or unanimous four-view `incompatible` results.
4. **DA** selects one Phase-1 conclusion to challenge when consensus is absent.
5. **Rebuttal** asks the challenged view to defend or revise its conclusion.
6. **Arbiter** produces the final verdict from original requirements and compact evidence artifacts.
7. **Persistence** stores per-agent records, compact artifacts, working memory, and final outputs.

## Runtime Boundaries

The scheduler controls readiness, concurrency, retries, timeouts, Batch submission, and persistence. Agents do not directly invoke one another.

The default public profile uses synchronous DeepSeek calls for semantic, logic, and DA; official Batch calls for Kimi feasibility and Qwen goal; dynamic synchronous rebuttal; and a synchronous user-configured OpenAI-compatible arbiter.

Batch is transport-level grouping. Every request body contains exactly one requirement pair, so pair-level reasoning remains isolated.

## Data Isolation

Agent prompts receive requirement IDs and the two requirement texts. Cosine similarity is preprocessing metadata and is not rendered into agent prompts. Downstream adjudication receives the original texts plus compact structured evidence from earlier stages.
