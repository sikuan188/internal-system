# Repository Guidelines

## Project Structure & Module Organization
- `backend/`: Django 5.2 project (`pcms_staff`) with apps `staff_management/` and `application_submission/`; shared templates, static assets, and media uploads live here. `manage.py` sits at the backend root; logs rotate under `backend/logs/`.
- `frontend/`: React (MUI) app in `src/` with pages/components split by feature; `public/` holds static entry files.
- `docker/`: Compose files and env templates for local/https stacks; `docker/mysql/` and `docker/nginx/` define service configs.
- `docs/`: Deployment and admin guides; check here before changing infra defaults.
- Tests: Django tests in each app’s `tests.py`; React tests colocated as `*.test.js`/`*.test.tsx` in `src/`.

## Build, Test, and Development Commands
- Backend setup: `cd backend && pip install -r requirements.txt`.
- Backend dev server (SQLite fallback via `USE_SQLITE=true`): `python manage.py migrate && python manage.py runserver 0.0.0.0:8000`.
- Backend tests: `python manage.py test` or per app (`python manage.py test staff_management`).
- Frontend setup: `cd frontend && npm install`.
- Frontend dev server: `npm start` (proxies to `localhost:8000`).
- Frontend tests: `npm test` (watch) or `CI=true npm test` for non-interactive runs.
- Docker stack: `cd docker && docker-compose -f docker-compose.yml up --build` to bring up MySQL, backend, and frontend together.

## Coding Style & Naming Conventions
- Python: PEP8 with 4-space indents; keep DRF serializers/views in the app folder; name modules snake_case and classes PascalCase. Use structured logging to `backend/logs/` instead of prints.
- React: Components PascalCase, hooks camelCase; keep API helpers in `src/services/` or `src/api/` (avoid ad-hoc axios calls in views); prefer functional components with hooks.
- Files & translations: Default language is zh-hant; keep labels consistent with existing bilingual patterns in `docs/` and UI strings.

## Testing Guidelines
- Add/extend Django tests in each app’s `tests.py`; fixture data should live alongside the test module. Aim to cover view permissions, serializers, and key workflows (submission, approvals, exports).
- React tests: colocate `*.test.js/tsx` near components; cover routing guards, form validation, and API error states. Use `@testing-library` patterns already in dependencies.
- Before PRs, run backend + frontend test suites and note results in the PR description.

## Commit & Pull Request Guidelines
- Commits in history are short, descriptive summaries (often zh/zh-hant); keep that style, one logical change per commit, imperative mood where possible.
- PRs should include: scope/intent, linked issue or task ID, test commands and results, and UI screenshots/gifs for visible changes. Call out DB migrations and new env vars explicitly.
- Avoid committing secrets; override `SECRET_KEY`, DB creds, and HTTPS flags via env (see `docker/docker-ssl.env.template` and `backend/pcms_staff/settings.py`).

## Security & Configuration Tips
- Database switches between MySQL and SQLite via `DB_ENGINE`/`USE_SQLITE`; HTTPS flags (`HTTPS_ENABLED`, `SECURE_SSL_REDIRECT`) gate SSL behavior. Never hardcode production hostnames or credentials.
- Logs are rotated under `backend/logs/`; verify permissions before deploying. Remove debug-only settings (wide `ALLOWED_HOSTS`, `CORS_ALLOW_ALL_ORIGINS`) when promoting to production.
