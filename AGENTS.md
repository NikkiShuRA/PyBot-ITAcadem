# AGENTS.md

Operational guide for AI agents working in this repository.

This file is a short instruction set. It does not replace project documentation. For architecture, process rules, security requirements, and decisions, always use the source documents referenced below.

## Purpose

- Use this file as the default working contract for agent discussions and task execution.
- Treat task-specific `DoD` as acceptance criteria for the current task, not as a place to restate global project rules.
- If this file conflicts with ADRs or core project docs, follow ADRs and core project docs.

## Read First

Before making meaningful changes, read these files in this order:

1. `README.md`
2. `ARCHITECTURE.md`
3. `CONTRIBUTING.md`
4. `DEPLOYMENT.md`
5. `SECURITY.md`
6. Relevant ADRs in `src/pybot/docs/adr/`

Read only the ADRs relevant to the task, but do not ignore them when the task touches architecture, layering, data flow, DTOs, DI, or domain modeling.

## Core Expectations

- Respect the architectural manifesto in `ARCHITECTURE.md`.
- Prefer the simplest solution that fits the current problem.
- Avoid speculative abstractions and unnecessary indirection.
- Keep code explicit, readable, and easy to trace.
- Follow existing project structure instead of concentrating a solution in one file.

## Architectural Invariants

- Maintain clear separation between presentation, business logic, and data access layers.
- Keep cross-layer communication aligned with the existing Dishka-based DI approach and the containers grouped in the `di` module.
- Do not violate principles defined in `ARCHITECTURE.md` unless there is a strong, explicit reason.
- Do not bypass established layering just to ship a one-off solution.
- Do not use absolute imports in Python code when project-relative imports are the established approach.
- Use type hints consistently to keep the system readable and scalable.
- Avoid type-hint hacks such as `cast`, `Any`, and `object` unless there is no cleaner option and the reason is clear.

## Placement Rules

- Put Telegram command handlers, routers, dialog handlers, keyboards, filters, and middleware in `src/pybot/bot/`.
- Keep dialog windows and other presentation-only `aiogram-dialog` pieces in `src/pybot/bot/dialogs/`. Do not move business decisions there.
- Put application orchestration in `src/pybot/services/`. Services coordinate repositories, domain behavior, and transactions.
- Put repository implementations and infrastructure adapters in `src/pybot/infrastructure/`.
- Put ORM models and database configuration in `src/pybot/db/`.
- Put DTOs and value objects used across layer boundaries in `src/pybot/dto/`.
- Put pure domain exceptions and domain-specific rules that do not belong to transport or infrastructure in `src/pybot/domain/`.
- Put mapping helpers between transport-layer data and DTOs in `src/pybot/mappers/`.
- Put dependency wiring and provider registration in `src/pybot/di/`.
- Put health-check API wiring in `src/pybot/health/`.
- Put shared cross-cutting utilities in `src/pybot/utils/`, and keep bot-specific helpers in `src/pybot/bot/utils/`.

## Naming Conventions

- Follow Python naming conventions consistently so the code stays compatible with the existing codebase and Ruff naming checks (`N` rules): `snake_case` for functions, methods, variables, and modules; `PascalCase` for classes; `UPPER_SNAKE_CASE` for constants.
- Names should reveal intent, not implementation trivia. Prefer `current_level`, `target_user`, `notification_schedule`, `missing_competence_ids` over vague names like `data`, `obj`, `res`, `temp`, or numbered variants such as `user2`.
- Do not use misleading collection names. If a value is not a `list`, do not call it `*_list`. Prefer `user_roles`, `role_names`, or `competence_ids` over names like `role_list` when the concrete type is different.
- Use one term per concept across the project. Do not mix near-synonyms like `handler/controller`, `message/text`, `competence/skill`, `notification/alert`, or `manager/service` unless they actually mean different things.
- Prefer nouns for classes and value objects, and verbs or verb phrases for functions and methods. Good examples: `UserProfileService`, `NotificationFacade`, `normalize_message`, `find_user_by_telegram_id`, `register_student`.
- Name methods by semantic contract, not by habit. Keep `find_*` for nullable lookups, `get_*` for required lookups, `has_*` / `exists_*` for boolean checks, and command-style verbs like `register_*`, `update_*`, `remove_*`, `dispatch_*` for state-changing operations.
- Avoid type-encoding or pseudo-Hungarian naming. Prefer `phone_number` over `phone_str`, `users` over `user_list`, and `notification_port` over `i_notification_port`.
- Boolean names should read like predicates. Prefer `is_ready`, `has_role`, `can_retry`, `should_seed` over generic names like `flag`, `status`, or `check`.
- Temporary short names are acceptable only for tiny, local scopes where the intent is obvious, such as `db`, `dp`, `ms`, `i`, or `err`. Do not let such names escape into broader scopes or public APIs.
- Avoid joke names, anime names, filler abbreviations, and “clever” identifiers. Names should be searchable, pronounceable, and boring in a good way.
- Prefer domain names over transport names when the code models business meaning. For example, prefer `user_profile`, `role_request`, and `competence_names` over generic names like `payload`, `input_data`, or `message_data` when the richer meaning is already known.

### Newspaper Rule

- Follow the Newspaper Rule in modules, classes, and longer functions: higher-level intent should appear first, and lower-level details should appear later.
- Public entrypoints should usually be near the top, and private helpers that support them should usually live below.
- Names should support top-down reading. Prefer a flow like `cmd_profile_private -> manage_profile -> _collect_user_profile -> _create_profile_message` over exposing low-level details first and only revealing the main intent later.
- Do not name a high-level function after a low-level mechanism. Prefer `build_profile_message` over names like `concat_profile_lines` when the real intent is to build a profile message.

## Change Playbooks

### If adding or changing a Telegram command or handler

- Update the relevant module under `src/pybot/bot/handlers/` and keep the handler thin.
- Put parsing, Telegram-specific branching, and response formatting in the handler, but move reusable business behavior into services.
- Re-check related command flags such as `role` and `rate_limit` when the command is admin-only, expensive, or user-facing.
- Add or update bot/flow tests for the command behavior, including at least one unhappy path when parsing or target resolution can fail.
- Update user-facing help or shared texts when the command contract or available behavior changes.

### If changing a dialog flow

- Treat `handlers.py`, `windows.py`, `states.py`, and `getters.py` as one flow unit and review them together.
- Keep business decisions out of `windows.py`; route validated dialog data into DTOs and services.
- Explicitly verify dialog completion, skip paths, stale callback handling, and keyboard cleanup when the flow can terminate early.
- Add or update flow tests around handler logic and important transitions, but do not force separate tests for purely declarative dialog widgets.
- Run a local smoke check for critical dialog flows such as registration when the UX path or runtime behavior changed.

### If changing profile logic or lookup contracts

- Keep nullable and strict lookup semantics aligned with ADR `008-nullable-and-strict-lookup-separation.md`.
- When repository or service lookup semantics change, update naming (`find_*` vs `get_*`), return types, call sites, and tests together.
- If the profile flow changes, review handler code, profile-oriented services, repositories, mappers, and related DTOs as one bundle.
- Remove dead `None` checks after strict lookups and add missing error handling where nullable lookups remain valid.
- Update ADRs or architecture docs when the semantic contract, not just the implementation, changes.

### If adding or changing service-layer business behavior

- Put orchestration in `src/pybot/services/`, not in handlers, middleware, or repositories.
- Pass validated DTOs or explicit arguments into services and let services coordinate repositories, domain rules, and transaction boundaries.
- Review whether the change also requires updates to repositories, mappers, DTOs, domain exceptions, or seed scripts.
- Add or update targeted service tests and cover both happy paths and domain-error paths.

### If changing repositories, ORM models, or database schema

- Treat model changes, repository changes, migrations, and related service/test updates as one coherent change set.
- Put schema changes behind Alembic migrations and verify repository behavior against the new schema.
- Revisit seed and bootstrap scripts when new required fields, constraints, or relations are introduced.
- Be explicit about SQLite-specific constraints and runtime behavior when the schema or migration logic depends on them.
- Add or update repository and service tests that cover both found and not-found behavior for the changed entities.

#### Migration Checklist

- Prefer backward-compatible migrations whenever possible. Assume production may pass through mixed states where code, schema, seed data, and deploy steps are not switched atomically.
- Before changing a model, review the current ORM model, existing Alembic revisions, repository behavior, seed/bootstrap scripts, and deploy/runtime path together.
- Treat `model + migration + repository + seed/bootstrap + tests + deploy impact` as one required review bundle, not as independent follow-up tasks.
- Account for SQLite-specific limitations and Alembic behavior. Be careful with `ALTER TABLE`, constraint rewrites, batch operations, enum/string storage, and other operations that SQLite handles differently.
- Do not trust Alembic autogenerate blindly. Review the generated revision manually and make sure it reflects the real intent of the change.
- Keep migrations explicit and readable. Avoid clever shortcuts that make downgrade/upgrade behavior unclear.
- When changing ORM models, verify that SQLAlchemy relationships, defaults, nullability, eager-loading assumptions, and repository queries still behave correctly after the migration.
- When changing repository code for a migrated model, preserve the architectural style of the project: repositories stay focused on persistence access, services keep orchestration, and presentation code must not absorb persistence logic.
- If a migration changes required fields, constraints, names, or relations, check `fill_point_db.py`, `db_reset_start.py`, entrypoint/bootstrap code, and any runtime/seed scripts that construct or query the affected model.
- After changing seed or bootstrap logic, verify that the script still works with the new model and migrated schema, not only at type-check level but at runtime behavior level.
- Check deployment impact both locally and for production. Review whether the migration affects one-shot migration containers, seed containers, startup order, mounted database paths, Redis/runtime assumptions, or health/readiness checks.
- Prefer rollout-safe changes for production paths. If a change is not backward compatible, call that out explicitly and document the deployment constraint or required operator action.
- Add or update tests for the changed model, repository, service behavior, and any script logic coupled to the new schema.
- Re-run and fix tests that fail because the model contract changed; do not silence or bypass them just to get green CI.
- When relevant, verify the migration path on a realistic local database state: apply migrations, run seed/bootstrap scripts, execute targeted flows, and confirm repository/service behavior after upgrade.

### If adding or changing DTOs, validation, or value objects

- Strengthen contracts through DTOs and value objects instead of spreading ad-hoc validation across handlers and services.
- When validation rules change, update the DTO or value object first, then align handlers, services, mappers, and tests with the new contract.
- Prefer explicit typed models over `cast`, `Any`, or loosely shaped dictionaries when passing structured data between layers.
- Add or update tests that exercise the new validation boundaries and regression-prone invalid inputs.

### If changing middleware, filters, or routing

- Keep middleware and filters focused on cross-cutting concerns such as roles, rate limits, routing context, and user activity.
- Re-check router registration and module `__init__` wiring when adding, moving, or removing handlers to avoid duplicated or missing routes.
- When adding role or rate-limit flags to commands, update the relevant bot tests so access-control or throttling regressions are visible.
- Do not move feature business logic into middleware just because it runs before handlers.

### If changing notifications, broadcasts, or TaskIQ flows

- Treat command entrypoints, DTOs, service orchestration, ports, concrete adapters, TaskIQ dispatcher/tasks, and runtime wiring as one feature slice.
- Keep scheduling and delivery validation in DTOs or dedicated services, not scattered across handlers and tasks.
- When background delivery changes, also review local runtime wiring, `docker-compose`/worker setup, and notification smoke tests.
- Add or update tests for validation, retries, partial failures, dispatch semantics, and runtime container wiring.

### If changing config, runtime wiring, or deployment

- Treat `.env`/settings, DI/bootstrap wiring, runtime process setup, deployment automation, and operational docs as one bundle.
- Update `.env.example`, relevant settings models, deploy docs, and automation scripts together when introducing or changing required configuration.
- Add or keep runtime validation close to deployment code when failures would otherwise surface only on the target server.
- Prefer lightweight post-deploy smoke checks for container/runtime readiness instead of assuming CI coverage is enough.
- Be especially careful with secrets, token rotation, environment-specific paths, and production SQLite/Redis behavior.

## Repo-Specific Examples

- `DON'T:` repeat the old profile pattern from the pre-refactor `src/pybot/bot/handlers/profile/grand_profile.py`, where an aiogram handler accepted `AsyncSession`, called a procedural helper, and assembled profile output itself. `DO:` follow the current split between `src/pybot/bot/handlers/profile/user_profile.py` and `src/pybot/services/user_services/user_profile.py`, where the handler stays thin and profile orchestration lives in a dedicated service.
- `DON'T:` reintroduce procedural helper functions like the old `collect_user_profile`, `create_user_profile`, `get_user_by_telegram_id`, or `update_user_points_by_id` that lived beside `UserService` and bypassed the intended service/repository flow. `DO:` keep use-case behavior inside services, repositories, ORM/domain methods, DTOs, and mappers according to the layered architecture.
- `DON'T:` inject database session handling directly into presentation code when the handler can work through existing services. The pre-refactor profile flow passed `AsyncSession` into the handler and then deeper into helper functions. `DO:` inject the proper service through Dishka and keep database access behind service/repository boundaries.
- `DON'T:` let one element own too many responsibilities at the wrong layer, such as reading transport input, querying repositories, performing level calculations, formatting UI text, and delivering output all in one place. `DO:` split responsibilities across handler, service, mapper/value object, and notification/output layers.
- `DON'T:` blur lookup semantics by naming a method like `get_*` while returning `None` as a normal absence case. `DO:` follow ADR `008-nullable-and-strict-lookup-separation.md`: `find_*` for nullable lookups, `get_*` for required lookups that raise domain errors.
- `DON'T:` patch new behavior into the codebase in a purely procedural style that ignores the existing DDD-oriented slices. `DO:` extend the current architecture by reusing or adding the proper entity, repository, DTO, mapper, service, port, or adapter instead of bypassing those layers for a quick fix.

## Error Boundary Rules

- Domain errors should originate in the business-logic or data-access layers and, when needed, be re-raised with preserved context until they reach the presentation layer.
- Expected domain errors must be translated into safe user-facing responses at the presentation layer, not exposed directly to the user as raw exception text.
- Data and business layers define the semantics of the error; the presentation layer defines how that error is shown to the user.
- Do not leak exception class names, raw exception messages, database details, repository internals, or infrastructure context into Telegram replies, dialog alerts, or other transport-level responses.
- Prefer centralized handling of expected domain errors where possible so the system keeps consistent UX without breaking encapsulation or separation of concerns.

## Transaction Boundaries

- Transaction boundaries belong to application services because they represent the start and end of a business operation.
- Services may coordinate `commit`, `rollback`, and related transaction control when completing or aborting a business use case.
- Repositories must stay stateless and must not perform hidden commits.
- Repository methods may prepare persistence state, query data, or use `flush` when needed, but they must not silently finalize the transaction boundary for the caller.
- Treat transaction boundaries as part of the business-operation contract, so they remain visible at the service layer and traceable in code review and debugging.

## Common Anti-Patterns

- Do not force the whole solution into one file when the architecture calls for splitting responsibilities across handlers, services, repositories, DTOs, and models.
- Do not move business logic into handlers, dialog windows, middlewares, or other presentation-layer code just because it is faster to wire there.
- Do not bypass the established service/repository layering with direct database access from presentation code.
- Do not introduce one-off shortcuts that conflict with ADRs or `ARCHITECTURE.md` unless there is a clear and explicit reason.
- Do not use type-hint hacks such as `cast`, `Any`, or `object` when the code can be modeled with clearer types.
- Do not break project code style, naming, or structure for a temporary fix that is expected to stay in the codebase.
- Do not skip tests for changed behavior, and do not skip a broader regression pass when the change can affect neighboring flows.
- Do not assume the project works without local verification when local verification is feasible.
- Do not expose, hardcode, print, or log tokens, secrets, or private values from `.env`.

## Validation Expectations

Before handing work off as complete:

- Run `just quality-gate` as described in `JUSTFILE.md`.
- For changes in handlers, dialogs, commands, middlewares, or other user-facing bot flows, add or update bot/flow tests. Prefer the existing `pytest-aiogram`-based approach where it fits.
- Do not add separate mandatory tests for purely declarative `aiogram-dialog` GUI elements if they do not contain meaningful logic of their own. Test them only when they include important branching, dynamic behavior, or other non-trivial presentation logic.
- For changes in services, domain logic, repositories, DTOs, or other core behavior, add or update targeted unit and/or integration tests.
- For larger user-facing changes, verify the critical scenario with a local smoke check in addition to automated tests.
- Check touched user-facing text and Cyrillic content for mojibake or broken encoding, and fix such issues in the same request where they were introduced or discovered.
- Run tests covering the code you changed or added.
- Run the broader test suite to detect regressions when the scope of the change justifies it.
- Verify the affected flow locally when local execution is feasible and relevant.

If you cannot run one of these checks, say so explicitly and explain why.

## Task Completion Output

When reporting completed work, the final response should include:

- A clear summary of what was changed, including the changed or added files, the key change points, and an explanation of what was added or modified and why.
- Enough implementation context for a reviewer to understand how the solution works without re-discovering the whole change set from scratch.
- The results of mandatory verification steps, including `just quality-gate`, targeted tests, broader regression checks, and local smoke checks when they were relevant.
- A clear note about anything that could not be verified, including what was skipped and why.
- A summary of documentation or ADR impact when docs, docstrings, runbooks, or architectural decisions were updated or should be updated.
- A detailed trade-off summary when trade-offs were made, including why the chosen option was selected, its pros and cons, and its likely impact on the project and future development.

## How To Treat DoD

- Treat `DoD` as task-specific acceptance criteria.
- Do not reinterpret `DoD` as the full development policy of the repository.
- Apply `AGENTS.md`, ADRs, and core project docs by default even when they are not repeated in the task text.

## Documentation Update Rules

- Update docstrings when behavior or logic changes and existing docstrings become stale.
- Update generated documentation when the underlying source for that documentation changes.
- Keep ADRs handwritten unless explicitly asked to generate or rewrite them automatically.
- Do not rewrite broad project documentation unless the task actually requires it.

## Security Notes

- Treat `.env` and all secrets as sensitive.
- Never copy secrets into code, tests, logs, fixtures, screenshots, or documentation.
- Follow `SECURITY.md` when the task touches credentials, deployment, configuration, or disclosure risk.

## Escalation Rule

If a requested change appears to require breaking ADRs, architectural invariants, or security rules, pause and state the tradeoff clearly before proceeding.
