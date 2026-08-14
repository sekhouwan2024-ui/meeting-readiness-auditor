# Contributing

Thank you for helping improve Meeting Readiness Auditor.

## Before opening a pull request

1. Keep changes focused on cross-file evidence extraction, audit quality, report output, or the reusable Skill workflow.
2. Use synthetic or properly anonymized fixtures. Do not commit confidential presentations, customer data, credentials, or generated evidence databases.
3. Preserve the distinction between confirmed evidence, interpretation, assumptions, and recommendations.
4. Add or update a regression test when changing a script or schema.
5. Run `python -m unittest discover -s tests -v` and the Skill validator before submitting.

For large schema changes, open an issue first so compatibility and migration can be discussed.
