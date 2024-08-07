# Alembic Migration Guide for NexusWare

## Setup

1. Install Alembic:
    ```bash
    pip install alembic
    ```
   
2. Initialize Alembic (run from the `server` directory):
    ```bash
    alembic init alembic
    ```
   
3. Configure `alembic.ini`:
- Set `sqlalchemy.url = sqlite:///./nexusware.db`

4. Update `alembic/env.py`:
- Add import statements:
  ```python
  import sys
  import os
  sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
  from app.models import Base
  from app.core.config import settings
  ```
- Set `target_metadata = Base.metadata`

5. Create `.env` file in the `server` directory:
- Add `SECRET_KEY=your_secret_key_here`

## Creating Migrations

To create a new migration after changing models:
```bash
alembic revision --autogenerate -m "Description of changes"
```

## Applying Migrations

To apply migrations:
```bash
alembic upgrade head
```

To apply a specific migration:
```bash
alembic upgrade <revision>
```

## Rolling Back Migrations

To roll back the last migration:
```bash
alembic downgrade -1
```

To roll back to a specific migration:
```bash
alembic downgrade <revision>
```

## Viewing Migration History

To see the current migration version:
```bash
alembic current
```

To see the full migration history:
```bash
alembic history
```

## Troubleshooting

- If you encounter "No module named 'server'" error, ensure you're running commands from the `server` directory.
- If you get a "SECRET_KEY missing" error, check your `.env` file in the `server` directory.
- Always run Alembic commands from the `server` directory.

