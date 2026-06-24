# Contributing to Uroboros

We love contributions! To keep the repository clean and efficient, please follow these guidelines:

## Code Philosophy (Ponytail)
We follow the **Ponytail (lazy developer)** philosophy:
1. **YAGNI**: Don't build speculative features or add unrequested abstractions.
2. **Standard Library first**: Utilize standard library features before adding external dependencies.
3. **Terse diffs**: Prefer readable, minimal code changes over over-engineered refactoring cycles.

## Submitting Pull Requests
1. Fork the repository and create your feature branch.
2. Ensure all tests pass by running:
   ```bash
   pytest test_api.py test_db.py
   ```
3. Add a corresponding `Report_Vx.md` in the `Progress Reports` directory tracking quantitative modifications and features.
4. Commit your changes and submit a pull request.
