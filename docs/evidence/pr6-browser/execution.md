# PR6 real browser execution

Executed exact source dfecff7344c65041f7c330319903a54a518d8cf5 using installed Google Chrome through Playwright, outside sandbox due to socket/process restrictions. Preview status reported available=false. Isolated SQLite /tmp/arcaccept.sqlite and local port 18766; random synthetic reviewer password never printed. Server/browser terminated after run. No OpenAI calls. Provider and asynchronous dispatch were mocked; processing used the real task pipeline.

Observed browser login; actual tester JS canonical JSON POST returned 202; polling observed pending then completed; detail navigation and Back; Human Review filter (empty fixture inbox); desktop 1440x900 and mobile 390x844 screenshots; intercepted submission network abort exposed Resume; removing interception and clicking Resume completed successfully. Screenshots: tester.png, detail.png, back.png, review.png, mobile.png, failure.png.

Executable JS regression harness passed; Python 72 tests passed (five missing staticfiles warnings); Ruff passed. Python tests cover CSRF rejection, export and hostile text escaping.

Acceptance remains incomplete: actual bfcache use was not measured; Back screenshot alone does not prove preserved lifecycle recovery. Bounded 60-poll expiry, uncertain delivery after server acceptance, duplicate network counts, populated Human Review fixture, browser export/entities/reasons assertions and keyboard focus remain unverified. No merge approval claimed. No live provider, Redis/PostgreSQL or container acceptance.
