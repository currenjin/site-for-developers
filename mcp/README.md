# Site for Developers MCP

Read-only bundled README catalog; Node.js >=22 (including Node 22). This package is private, not published to npm, and has no public endpoint. No runtime website fetching, LLM calls, writes, or user-file access. Installation may need registry access for dependencies; runtime catalog queries do not.

## Installed users

Install the locally generated archive into your own project (replace the absolute path):

```sh
npm install /absolute/path/site-for-developers-mcp-0.1.0.tgz --ignore-scripts
./node_modules/.bin/site-for-developers-mcp --stdio
```

The installed bin defaults to stdio. Configure an MCP client with `command` set to the absolute path of `node_modules/.bin/site-for-developers-mcp` and `args: ["--stdio"]`. Working directory does not matter; stdout is reserved for MCP messages. Alternatively run `node /absolute/path/node_modules/site-for-developers-mcp/src/cli.js --stdio`.

Local stateless Streamable HTTP:

```sh
MCP_HOST=127.0.0.1 PORT=3000 ./node_modules/.bin/site-for-developers-mcp --http
curl http://127.0.0.1:3000/health
```

Connect your MCP client's Streamable HTTP transport to `http://127.0.0.1:3000/mcp`. Only POST is supported there; GET streaming and DELETE sessions return 405. There are no persistent sessions or event replay. `/health` reports process liveness, not catalog freshness or external URL verification, and bypasses the query limiter (not Host/Origin checks).

### Runtime environment and security

| Variable | Default | Contract |
| --- | --- | --- |
| `MCP_HOST` | `127.0.0.1` | Listen address; public bind requires both allowlists below |
| `PORT` | `3000` | Integer 1..65535 |
| `MCP_ALLOWED_HOSTS` | loopback hosts | Comma-separated lowercase Host names without ports; use `[::1]` for IPv6; no wildcard |
| `MCP_ALLOWED_ORIGINS` | empty | Comma-separated exact Origin values (scheme, host, port); no wildcard; absent Origin allowed |
| `MCP_MAX_REQUESTS` | `120` | Decimal integer 1..100000, requests per socket-IP bucket per window |
| `MCP_RATE_WINDOW_MS` | `60000` | Decimal integer 1..3600000, fixed window in milliseconds |

Invalid rate budgets fail at startup; limits cannot be disabled. `/mcp` requests, including rejected methods or malformed JSON, consume budget. Each process supports at most 10000 active IP buckets. Exceeding budget returns 429 with Retry-After. JSON bodies are limited to 64 KiB; header/request timeouts are 10 seconds.

Only raw Host/Origin and socket IP are used; **Forwarded and X-Forwarded-* are never trusted**. The server has no authentication or TLS, and Origin checking is not authentication. No CORS/preflight support is provided. Before remote use, put it behind a gateway with TLS, authentication/access control, per-client limits, aggregate request/concurrency limits, and matching Host/Origin configuration; block direct backend access.

**Reverse proxy shared-IP budget:** clients behind one proxy share its backend socket-IP bucket. The default is 120 requests/60 seconds for all those users together, not 120 each. Gateway per-client limiting does not remove this shared backend bottleneck. Set `MCP_MAX_REQUESTS` and `MCP_RATE_WINDOW_MS` explicitly for the measured aggregate backend workload and set the gateway aggregate budget below it with headroom for initialization/notifications and bursts. For example, a single proxy could use `MCP_MAX_REQUESTS=6000 MCP_RATE_WINDOW_MS=60000` with a gateway aggregate cap of 5000 backend requests/minute plus a separate per-client quota; these are illustrative values, not a capacity guarantee. Multiple proxies/processes have separate buckets, not a distributed global limit. This backend budget is a shared safety ceiling, not a fair user quota. Health bypass keeps monitoring available when exhausted; monitor backend 429s as well as liveness. Load-test and choose budgets for your deployment; this is not complete DoS protection.

## Catalog contract and snapshot limitations

Tools: `search_sites` (AND keywords, optional category/language, limit 1..20), `get_site` (stable ID), and `list_categories`. All are read-only. Search normalizes bilingual aliases (`깃/git`, `레디스/redis`, `정규식/정규표현식/regular expression/regex`, `연습/practice/exercise/실습`). Description words 학습, 튜토리얼, 게임 remain searchable and additionally imply 실습. `matchedFields` names the originating field, including its documented alias match; it is not necessarily a literal substring match. Results use stable ID order, not a relevance score.

`rawLabels` preserves the distinct README labels in first-seen order across duplicate URLs. `languages` derives only from EN/KR; `openSource` derives only from O. `cost` is `free` for F, `paid-or-freemium` for $ alone (README: 유료/부분유료), `free-and-paid` for F+$, or `unknown` when unlabelled. These are source-label interpretations, not verified pricing, language, or license claims.

The bundled snapshot does not update automatically. `source.version` is a SHA-256 of source README bytes and `verified:false` explicitly means provenance, **not live URL, price, language, or license verification**. Confirm details on official sites. Canonical duplicate URLs merge categories/labels; first name/description wins. Snapshot changes require regenerating catalog in the repository, repacking, and reinstalling/redeploying. Runtime never reads the original README.

## Repository developers

Only the full repository checkout includes the lockfile, tests, and generation scripts. Do not run `npm ci`, `npm test`, `npm start`, or catalog scripts inside the installed package: those repository-only development assets are intentionally excluded from the archive.

```sh
cd mcp
npm ci --ignore-scripts
npm run catalog:generate
npm run catalog:check
npm test
npm audit --omit=dev
npm pack
npm start # repository convenience command for local HTTP
```

The parser supports the current authoritative README's space-indented `- ` list and span hierarchy, not arbitrary Markdown. Unsupported list/site syntax, duplicate span IDs (including empty aliases), malformed metadata/URLs, and unresolved references fail generation rather than silently dropping sites. Source-checkout Korean operations documentation is `docs/MCP.md`; this README is self-contained for installed runtime users. No commit, publish, or deployment is part of these commands.
