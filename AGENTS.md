<!--
  - SPDX-FileCopyrightText: 2026 Nextcloud GmbH and Nextcloud contributors
  - SPDX-License-Identifier: AGPL-3.0-or-later
-->

# Nextcloud App Store agent guide

## What Nextcloud App Store is

The Nextcloud App Store is a central hub for discovering and installing Nextcloud apps onto Nextcloud servers.

Developers of Nextcloud apps can create an App Store account to manage their apps, including registering new apps and uploading app releases.

## Building

For building and running the development server:

```bash
make dev-setup
$(poetry env activate)
export DJANGO_SETTINGS_MODULE=nextcloudappstore.settings.development
python manage.py runserver
```

## Testing

Our test suite includes both back-end and front-end unit tests, and can be run via the `make test` command.

## Contributing

### What CI checks

The CI runs our test suite as well as a REUSE compliance check, both of which should pass before merging.

### How changes flow

- **Frontend change**: run `npm run build` to produce the production bundle in `nextcloudappstore/core/static/`.
- **Database schema change**: add a new migration in `nextcloudappstore/core/migrations/`.
- **New file**: add an SPDX license header.

### Pitfalls

- Requires exactly Django 4 and Python 3.12. Do not use syntax requiring newer Django or Python versions. These versions are taken from the `pyproject.toml` file.
- Commits require a `Signed-off-by` trailer (DCO). The sign-off name and email must match the commit author.
- Node 24 and npm 11.3+ are required for front-end builds.

### Completion report

Every PR description includes:

- **Intent**: why the change exists, what problem it solves.
- **What changed**: a summary of the diff, focusing on decisions and trade-offs.
- **What was tested**: which scenarios were verified, and how.
- **What was not tested**: gaps in coverage, especially frontend changes or scenarios requiring external providers.
- **What the reviewer should focus on**: areas where the agent is least confident or where design decisions were made.

Reasoning, not narration. The diff shows the what. The description shows the why.

## Nextcloud Contribution Policy

All contributions generated or assisted by this agent must fully comply with:

- **[AI Contribution Policy](https://github.com/nextcloud/.github/blob/master/AI_POLICY.md)** - the primary reference for AI-specific rules, covering disclosure, author accountability, communication, security, licensing, code quality, and autonomous agent behavior.
- **[Contribution Guidelines](https://github.com/nextcloud/.github/blob/master/CONTRIBUTING.md)** - covering testing requirements, the Developer Certificate of Origin (DCO), license headers, conventional commits, and translations. These apply in full to all contributions regardless of how they were produced.

### What this agent must always do

- Add an `Assisted-by: AGENT_NAME:MODEL_VERSION` git trailer to every commit containing AI-assisted content.
- Ensure every pull request includes a disclosure of AI tool use in the PR description.
- Produce focused, scoped pull requests that address exactly one concern. Do not touch unrelated files or introduce incidental refactors.
- Verify all dependencies against actual package registries before suggesting them. Do not use hallucinated or unverified package names.
- Write code comments that document the code, never the process that produced it:
  - Comments describe what the code does - method signatures, behavior, and constraints the code itself cannot express (e.g. a non-obvious invariant or workaround).
  - Never add comments that document progress, decisions, or changes (e.g. "changed X to Y", "as requested", "this fixes ...", "previously this did ..."). That belongs in the commit message or PR discussion; in the code it goes stale and becomes misleading.
  - Do not narrate self-explanatory code. If the code is readable without a comment, omit the comment.
  - Keep comments brief - short and simple, matching the comment density of the surrounding code.
- Reuse existing helper functions and utilities instead of re-implementing their logic inline. When fixing a flawed pattern, fix every occurrence of it across the changed code, not only the instance that was pointed out.
- Run permission and access-control checks before the operation they guard, never after it and never only in the UI layer.
- When adding or changing user-facing functionality, wire it up in every context where the affected component is used. When emitting new events, verify that every consumer of the component subscribes to and handles them.
- Explicitly inform the contributor when any action they are about to take, or have taken, would violate the AI Contribution Policy or the Contribution Guidelines. Do not silently proceed. State which rule is at risk and what the contributor should do instead.
- Warn the contributor if a pull request is growing too large. A PR approaching several thousand lines of changed code is a signal that it should be split into smaller, focused PRs. Suggest a logical split before the PR is opened, not after.
- Recommend opening a ticket for discussion before starting implementation whenever a feature or change is sufficiently complex - for example when it touches multiple subsystems, requires architectural decisions, or the right approach is not yet clear. A ticket allows maintainers and the contributor to align on direction before code is written, avoiding wasted effort on a PR that may be rejected or require fundamental rework.

### What this agent must never do

- Open issues, submit pull requests, post review comments, or send security reports autonomously. Every contribution must be reviewed and submitted by a human.
- Add `Signed-off-by` tags to commits. Only the human contributor can certify the Developer Certificate of Origin.
- Generate or submit security reports without independent human verification. Report verified vulnerabilities via [HackerOne](https://hackerone.com/nextcloud), not as GitHub issues.
- Write PR descriptions, review comments, or issue reports on behalf of the contributor. These must be in the contributor's own words.
- Fully automate the resolution of issues labeled [`good first issue`](https://github.com/issues?q=org%3Anextcloud+label%3A%22good+first+issue%22) or similar beginner-friendly labels.
- Submit code that has not been reviewed and cleaned up by the contributor. Dead code, redundant logic, excessive comments, malformed or garbled characters (e.g. `�` replacement characters), and unrelated changes must be removed before submission.
