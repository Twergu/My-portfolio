# Local browser smoke

Date: 2026-09-14. Source revision: `14e38dc` (local source matches application code in that revision).

| Check | Observed result |
|---|---|
| Server restart | Latest application running at `http://127.0.0.1:8000/` |
| Japanese settings | Generator `gpt-5.6-luna`, Verifier `gpt-5.6-luna`, Embedding `text-embedding-3-small`; off/fast/strict selector and Japanese descriptions visible |
| Mode | Local passage retrieval remained selected; connection-test button was not used |
| Existing fictional PDF | Query `员工年假如何申请？` returned the leave-policy passage with Japanese interface text |
| Citation | Citation 1 opened the source panel for physical PDF page 2, with the source excerpt and PDF link |
| API usage | The observed query used local retrieval and displayed USD 0.000000; no model request was made |

This is manual browser smoke, not a complete visual/accessibility or Japanese-generation evaluation. The sample PDF itself is Chinese; the application retains the original source text.
