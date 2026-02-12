# Zero to Hero Portfolio

A full portfolio project using vanilla frontend files and a Flask backend with Google OAuth, Gmail notifications, and Google Tasks automation.

## Access policy

- Only **monaimabdel119@gmail.com** is allowed to authenticate and manage backend-changing actions.
- Any other visitor is considered **read-only** and can only browse/watch the portfolio.

## Project page presentation standard

Each page inside `/projects/` should clearly present:
1. Context/goal.
2. Implementation highlights.
3. Outcome/value.

## Run locally

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open `http://localhost:5000`.


## Testing

```bash
python scripts/run_smoke_test.py
```
