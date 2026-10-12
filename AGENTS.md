# CodeFlowAtlas collaborator instructions

Read `README.md`, `AI_CONTEXT.md`, `docs/project-specification.md`, and `docs/developer-guide.md` before substantial changes. These documents state product intent and proposed implementation; inspect current code, tests, and decision records to learn what is implemented.

Keep static inference, observed telemetry, and AI hypotheses separate in storage, APIs, and the UI. Do not execute imported repositories during static analysis. Run target applications and traffic or failure experiments only in approved isolated environments with bounded resources and target allowlists.

Build the next smallest complete part of the core flow. Add fixture expectations and tests for analyzer or contract changes. Update the relevant focused document when behavior changes. Record architecture decisions in `docs/decisions/` and state unsupported cases explicitly.

Do not introduce Kafka, vector search, microservices, or another language analyzer solely because they appear in the long-term specification. Connect each addition to a demonstrated need and acceptance criteria.
