# Model choice

ArcVault uses **gpt-6.1-terra**, reasoning `none`, prompt `triage_v4` and a 4,096-token output limit.

Terra was retained after the paired V3 comparison: 50/50 application-valid outputs versus Luna's 35/50, stronger category/entity/routing matches, and lower measured median latency. Luna's 15 failures were nonverbatim source excerpts, despite valid JSON responses.

The final compact V4 prompt reduces input tokens and keeps all 50 outputs valid. It trades some category and routing matches for a smaller prompt; it did not improve quality across the board.

See [benchmark results](submission/BENCHMARKS.md) for the complete comparison, run history and limitations. Classification, extraction and summary use one structured request; Python handles routing and arithmetic.
