# PR6 real browser execution

Executed exact source dfecff7344c65041f7c330319903a54a518d8cf5 using installed Google Chrome through Playwright, outside sandbox due to socket/process restrictions. Preview status reported available=false. Isolated SQLite /tmp/arcaccept.sqlite and local port 18766; random synthetic reviewer password never printed. Server/browser terminated after run. No OpenAI calls. Provider and asynchronous dispatch were mocked; processing used the real task pipeline.

Observed browser login; actual tester JS canonical JSON POST returned 202; polling observed pending then completed; detail navigation and Back; Human Review filter (empty fixture inbox); desktop 1440x900 and mobile 390x844 screenshots; intercepted submission network abort exposed Resume; removing interception and clicking Resume completed successfully. Screenshots: tester.png, detail.png, back.png, review.png, mobile.png, failure.png.

Executable JS regression harness passed; Python 72 tests passed (five missing staticfiles warnings); Ruff passed. Python tests cover CSRF rejection, export and hostile text escaping.

Acceptance remains incomplete: actual bfcache use was not measured; Back screenshot alone does not prove preserved lifecycle recovery. Bounded 60-poll expiry, uncertain delivery after server acceptance, duplicate network counts, populated Human Review fixture, browser export/entities/reasons assertions and keyboard focus remain unverified. No merge approval claimed. No live provider, Redis/PostgreSQL or container acceptance.

## Bounded remaining scope, 2026-11-07

No production JS change was needed. `node tests/js/tester.cjs` and `node tests/js/lifecycle.cjs` pass. Fake timers assert exactly one POST plus 60 status GETs at expiry, zero remaining timers, one GET on Resume despite two clicks, and one GET after simulated `pageshow({persisted:true})` recovery; pagehide clears the loop. Persisted-event coverage is simulation, not browser bfcache evidence.

Installed Chrome executed `remaining.py` with the existing mocked provider/dispatch setup (isolated SQLite, no live model). Interception forwarded the first POST to the actual server (202) then aborted its response. Resume sent exactly a second identical payload/key (200); ORM asserted exactly one matching database row. Polling reached completed. Actual detail/Back succeeded; navigation type was `back_forward` with a fresh tester GET, so actual bfcache was not used. Existing six screenshots remain the prior visual evidence; they were not regenerated. Browser/server exited.

Locked Python suite: 73 passed, six missing-staticfiles warnings. Ruff passed. The server regression discards the accepted response before retry and asserts matching ID/key, one DB row and one dispatch. UI checkpoint's bounded remaining lifecycle/idempotency scope passes. Live provider, Redis/PostgreSQL and container/queue acceptance remain later gates; optional broader UI acceptance listed above was not added to this bounded scope.
