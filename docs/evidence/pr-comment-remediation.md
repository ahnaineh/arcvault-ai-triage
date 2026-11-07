# Missed GitHub comment remediation

Original bodies fetched via GitHub REST; audit read from /tmp/pr-audit/audit.md.

| Original comment | Fix file | Regression | Result | Fix commit |
|---|---|---|---|---|
| https://github.com/ahnaineh/arcvault-ai-triage/pull/5#discussion_r4501600455 | config/__init__.py | tests/test_startup.py::test_wsgi_celery_new_process | PASS | 13ad7590ab94771ed9ec5f5ca0829e7beeb7d7b8 |
| https://github.com/ahnaineh/arcvault-ai-triage/pull/2#discussion_r4501442695 | apps/triage/policy.py | tests/test_policy.py::test_unequal_decimal_scales | PASS | 13ad7590ab94771ed9ec5f5ca0829e7beeb7d7b8 |
| https://github.com/ahnaineh/arcvault-ai-triage/pull/2#discussion_r4501453820 | apps/triage/schemas.py | tests/test_policy.py::test_money_sentence_punctuation (6 cases) | PASS | 13ad7590ab94771ed9ec5f5ca0829e7beeb7d7b8 |
| https://github.com/ahnaineh/arcvault-ai-triage/pull/3#discussion_r4501443892 | config/settings.py, compose.yaml | tests/test_startup.py::test_raw_database_credentials_new_process | PASS | 13ad7590ab94771ed9ec5f5ca0829e7beeb7d7b8 |
| https://github.com/ahnaineh/arcvault-ai-triage/pull/6#discussion_r4501646338 | static/intake/tester.js | tests/js/body-timeout.cjs | PASS | 13ad7590ab94771ed9ec5f5ca0829e7beeb7d7b8 |

Focused Python: 67 passed. Full locked suite: 102 passed (6 existing missing-staticfiles warnings). Ruff and Django check passed; all three Node harnesses passed. Explicit SQLite/test secret and isolated uv environment used. Celery proof is fresh-process WSGI/task binding and Redis transport configuration only: no broker publish or provider call performed. No Docker operations, comment mutations, merge, or watch. Acceptance/provider and eval remediation remain outside this scope.
