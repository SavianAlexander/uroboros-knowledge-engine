# Neuro Co-Pilot Commit Convention Standard

All git commits created under the **`neuro-copilot`** skill must adhere to the executive technical commit standard.

## Format
```
<type>(<scope>): <short summary> [Tududi #<task_id> | Neuro Hash: <sha256_short>]
```

## Commit Types
- `feat`: Executive technical feature additions or algorithmic enhancements
- `fix`: Root cause bug fix or diagnostic repair
- `refactor`: Structural optimization without logic changes
- `test`: Addition or modification of domain test suites
- `docs`: Technical documentation or skill specification updates
- `build`: Dependency, build script, or CI pipeline modifications

## Example Commit Messages
```
feat(indexer): optimize colbert reranker late-interaction matrix [Tududi #1042 | Neuro Hash: a8f73b9012c4]
fix(db): resolve thread-local connection pool leak on windows teardown [Tududi #1089 | Neuro Hash: 7c4e12d8a901]
docs(copilot): upgrade neuro-copilot skill to tri-engine dominance standard [Tududi #1105 | Neuro Hash: f3a10e8290bc]
```

## Automating Commit Formatting
Generate standard commit strings automatically using the helper script:
```bash
python .agents/skills/neuro-copilot/scripts/github_bridge.py provenance_tag --scope feat --desc "concise description" --task 1042
```
