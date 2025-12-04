# APEX Back Office BE - AGENTS Development Rules

<!-- cSpell:ignore FastAPI SQLAlchemy Pydantic psycopg Mangum uvicorn httpx boto SplitIO -->

This document defines all coding standards, patterns, and conventions for the apex-back-office-be codebase.

---

## 🎯 Project Overview

**Tech Stack:**

- Python 3.11+ (strict typing)
- FastAPI 0.115+ (async web framework)
- SQLAlchemy 2.0+ (ORM)
- PostgreSQL (via RDS Proxy)
- AWS Lambda (serverless deployment)
- AWS CDK (infrastructure as code)
- Mangum (ASGI adapter for Lambda)
- Pydantic (data validation)
- Split.io (feature flags)
- pytest (testing)
- Ruff (linting & formatting)
- mypy (type checking)

**Python Requirements:**

- Python: 3.11+
- UV package manager (recommended)
- pip (alternative)

---

## 📁 Folder Structure

```
apex-back-office-be/
├── lambda-auth/                     # Lambda authorizer
├── lambda-warmer/                   # Lambda warmer for cold start optimization
├── src/                             # Source code directory
│   ├── backoffice/                  # Main application package
│   │   ├── core/                   # Core configuration and dependencies
│   │   ├── clients/                # Client service APIs and logic
│   │   │   ├── api/                # API endpoints (FastAPI routers)
│   │   │   └── service/            # Business logic layer
│   │   ├── database/               # Database operations and session management
│   │   ├── exceptions/             # Custom exception classes and handlers
│   │   ├── models/                 # Pydantic models (request/response)
│   │   │   ├── psql.py            # SQLAlchemy ORM models
│   │   │   ├── request_models.py  # Request Pydantic models
│   │   │   ├── response_models.py # Response Pydantic models
│   │   │   └── shared_models.py   # Shared/common models
│   │   ├── pricing_rating/         # Pricing and rating logic
│   │   ├── utils/                  # Utility functions
│   │   ├── logging.py              # Logging configuration
│   │   ├── main.py                 # FastAPI app initialization
│   │   └── lambda_handler.py      # Lambda entry point
│   ├── tests/                      # Test files
│   │   ├── clients/                # Client service tests
│   │   ├── core/                   # Core module tests
│   │   ├── database/               # Database module tests
│   │   └── utils/                  # Utils module tests
├── stacks/                          # CDK Infrastructure
│   ├── configs/                    # Configuration files
│   └── utils/                      # Stack utilities
├── stages/                          # CDK deployment stages
├── pyproject.toml                  # Project configuration and dependencies
├── cdk.json                        # CDK configuration
├── app.py                          # CDK application entry point
└── README.md                       # Project documentation
```

**Key Principles:**

- Separation of concerns: API routes → Service layer → Database
- Feature-based organization in `clients/`
- Shared models in `models/`
- Colocate tests with source structure
- Use type hints throughout
- Async/await for I/O operations

---

## 🧩 Code Structure & Naming

### File Naming

- Python modules: `snake_case.py` (e.g., `account_service.py`, `request_models.py`)
- Test files: `test_*.py` (e.g., `test_account_api.py`)
- Config files: `snake_case` (e.g., `config.py`, `deps.py`)

### Module Pattern

```python
# 1. Imports (organized: stdlib → third-party → local)
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.backoffice.core import db_dependency
from src.backoffice.logging import logger
from src.backoffice.models import AccountResponseWrapper

# 2. Router/Component initialization
router = APIRouter(prefix="/accounts", tags=["Accounts"])

# 3. Route handlers
@router.get("/{account_prefix}", response_model=AccountResponseWrapper)
async def get_accounts_by_prefix(
    account_prefix: str, db: db_dependency
) -> AccountResponseWrapper:
    logger.info(f"Searching accounts with prefix: {account_prefix}")
    # Implementation
    return AccountResponseWrapper(success=True, item=accounts)
```

### API Route Pattern

```python
from fastapi import APIRouter, Query
from sqlalchemy.orm import Session

from src.backoffice.clients.service import search_accounts_by_prefix
from src.backoffice.core import readonly_db_dependency
from src.backoffice.logging import logger
from src.backoffice.models import AccountResponseWrapper

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.get("/{account_prefix}", response_model=AccountResponseWrapper)
async def get_accounts_by_prefix(
    account_prefix: str, db: readonly_db_dependency
) -> AccountResponseWrapper:
    """Get accounts matching the provided prefix."""
    logger.info(f"Searching accounts with prefix: {account_prefix}")
    
    account_items = await search_accounts_by_prefix(account_prefix, db)
    
    logger.info(f"Found {len(account_items)} accounts")
    return AccountResponseWrapper(
        success=True, message=None, errorCode=None, item=account_items
    )
```

### Service Layer Pattern

```python
import time
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.backoffice.exceptions import ClientsServiceError
from src.backoffice.logging import logger
from src.backoffice.models import AccountItem

async def search_accounts_by_prefix(
    search_prefix: str, db: Session
) -> list[AccountItem]:
    """Search accounts by prefix with performance logging."""
    start_time = time.time()
    logger.info(f"Searching accounts with prefix: {search_prefix}")
    
    # Input validation
    search_prefix = search_prefix.strip()
    if not search_prefix:
        raise ClientsServiceError(
            "Search prefix cannot be empty",
            error_code="INVALID_SEARCH_PREFIX",
            status_code=400,
        )
    
    # Database query
    stmt = select(ShippingEntity).where(
        ShippingEntity.ref_client_code.ilike(f"{search_prefix}%")
    ).limit(100)
    
    try:
        results = db.execute(stmt).all()
        logger.info(f"Database query successful, found {len(results)} accounts")
    except Exception as e:
        logger.error(f"Database query failed: {str(e)}")
        raise ClientsServiceError(
            f"Failed to fetch account data: {str(e)}",
            error_code="DATABASE_ERROR",
            status_code=500,
        ) from e
    
    # Convert to response models
    account_items = [
        AccountItem(
            id=int(result.id),
            accountNumber=result.ref_client_code,
            # ... map other fields
        )
        for result in results
    ]
    
    end_time = time.time()
    total_time = (end_time - start_time) * 1000
    logger.info(
        f"✅ search_accounts_by_prefix completed in {total_time:.2f}ms, "
        f"returned {len(account_items)} accounts"
    )
    
    return account_items
```

---

## 🌐 API & Routing

### FastAPI Router Organization

```python
# src/backoffice/clients/api/account_api.py
from fastapi import APIRouter

router = APIRouter(prefix="/accounts", tags=["Accounts"])

@router.get("/{account_prefix}")
async def get_accounts_by_prefix(...):
    pass
```

### Route Registration

```python
# src/backoffice/main.py
from fastapi import APIRouter, FastAPI
from src.backoffice.clients import account_router

app = FastAPI(...)

protected_router = APIRouter(prefix="/secured/api/v1")
protected_router.include_router(account_router)
app.include_router(protected_router)
```

### Dependency Injection

```python
# src/backoffice/core/deps.py
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session

def get_db() -> Generator[Session, None, None]:
    db = get_db_session()
    try:
        yield db
    finally:
        db.close()

# Reusable dependencies
db_dependency = Annotated[Session, Depends(get_db)]
readonly_db_dependency = Annotated[Session, Depends(get_readonly_db)]
user_id_dependency = Annotated[str, Depends(get_user_id)]
```

### Database Session Management

**Read Operations:**
```python
@router.get("/accounts/{prefix}")
async def get_accounts(
    prefix: str, db: readonly_db_dependency
) -> AccountResponseWrapper:
    # Use readonly_db_dependency for SELECT queries
    pass
```

**Write Operations:**
```python
@router.post("/accounts/preferences")
async def save_preference(
    preference: AccountPreferenceItem,
    db: db_dependency,  # Use db_dependency for INSERT/UPDATE/DELETE
    user_id: user_id_dependency,
) -> ResponseWrapper:
    pass
```

**Multiple Database Sessions:**
```python
@router.post("/quotes")
async def create_quote(
    request: CreateQuoteRequest,
    readonly_db: readonly_db_dependency,  # For lookups
    write_db: db_dependency,              # For writes
    user_id: user_id_dependency,
) -> QuoteResponseWrapper:
    # Use readonly_db for SELECT queries
    # Use write_db for INSERT/UPDATE/DELETE
    pass
```

### Response Models

**Standard Response Wrapper:**
```python
from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar("T")

class ResponseWrapper(BaseModel, Generic[T]):
    success: bool
    message: str | None = None
    errorCode: str | None = None
    item: T

# Usage
class AccountResponseWrapper(ResponseWrapper[list[AccountItem]]):
    pass
```

---

## 🗄️ Database Patterns

### SQLAlchemy Query Patterns

**Prefer Core-style queries (SQLAlchemy 2.0):**
```python
from sqlalchemy import select
from sqlalchemy.orm import Session

# ✅ GOOD - Core-style select
stmt = select(ShippingEntity).where(
    ShippingEntity.ref_client_code == account_number,
    ShippingEntity.main.is_(True),
)
result = db.execute(stmt).scalar_one_or_none()
```

**Avoid ORM-style queries:**
```python
# ❌ AVOID - Legacy ORM-style
result = db.query(ShippingEntity).filter_by(
    ref_client_code=account_number
).first()
```

### Connection Pooling

Database engines are cached (lazy singleton pattern) for Lambda performance:

```python
# src/backoffice/database/db.py
_engine_cache: dict[str, Engine] = {}

def create_db_engine(db_conn_string: str) -> Engine:
    """Create or return cached database engine."""
    if db_conn_string in _engine_cache:
        return _engine_cache[db_conn_string]
    # Create and cache engine
    engine = create_engine(db_conn_string, ...)
    _engine_cache[db_conn_string] = engine
    return engine
```

### Read/Write Separation

```python
# Read-only connection (uses read replica)
def get_readonly_db() -> Generator[Session, None, None]:
    db = get_db_session(database_role="readonly")
    try:
        yield db
    finally:
        db.close()

# Write connection (uses primary)
def get_db() -> Generator[Session, None, None]:
    db = get_db_session()  # Default is write
    try:
        yield db
    finally:
        db.close()
```

### Transaction Management

```python
# ✅ GOOD - Explicit transaction handling
async def save_user_preference(
    user_id: str, account_number: str, db: Session
) -> None:
    try:
        # Check if exists
        existing = db.execute(select_stmt).scalar_one_or_none()
        
        if existing:
            db.execute(update_stmt)
        else:
            db.add(new_preference)
        
        db.commit()
        db.refresh(new_preference)
    except Exception as e:
        db.rollback()
        raise ClientsServiceError(...) from e
```

### Performance Logging

Always log query performance:
```python
query_start_time = time.time()
results = db.execute(stmt).all()
query_end_time = time.time()
query_duration = (query_end_time - query_start_time) * 1000
logger.info(f"Database query completed in {query_duration:.2f}ms")
```

---

## 🔒 TypeScript Conventions → Python Type Hints

### Type Annotations

**Always use type hints:**
```python
# ✅ GOOD
async def search_accounts(
    search_prefix: str, db: Session
) -> list[AccountItem]:
    pass

# ❌ BAD
async def search_accounts(search_prefix, db):
    pass
```

### Pydantic Models

**Request Models:**
```python
from pydantic import BaseModel, Field

class CreateQuoteRequest(BaseModel):
    accountNumber: str
    origin: Location
    destination: Location
    details: list[FreightDetail]
    discountPercentage: Decimal | None = Field(None, ge=0, le=100)
```

**Response Models:**
```python
class AccountItem(BaseModel):
    id: int
    accountNumber: str
    accountName: str
    address: str | None = None
    city: str | None = None
    state: str | None = None
    postalCode: str | None = None
```

### Type Unions

```python
# ✅ GOOD - Use | for unions (Python 3.10+)
def process_data(value: str | int | None) -> dict:
    pass

# ✅ GOOD - Use Optional for backward compatibility if needed
from typing import Optional
def process_data(value: Optional[str]) -> dict:
    pass
```

### Generic Types

```python
from typing import Generic, TypeVar

T = TypeVar("T")

class ResponseWrapper(BaseModel, Generic[T]):
    success: bool
    item: T
```

---

## 🚩 Feature Flags (Split.io)

```python
from src.backoffice.utils.feature_flags import is_enabled, get_treatment

async def my_endpoint(
    user_id: user_id_dependency,
    db: db_dependency,
) -> ResponseWrapper:
    # Check if feature is enabled
    if is_enabled(user_id, "my-feature-flag-name"):
        # New feature logic
        return new_implementation()
    else:
        # Legacy logic
        return legacy_implementation()

# Get treatment value
treatment = get_treatment(user_id, "my-feature-flag-name", default="control")
if treatment == "on":
    # Feature enabled
    pass
```

**Naming convention**: `{domain}-{ticket}-{description}-server`

- Example: `"inbound-3697-refresh-after-auto-sequence-server"`

**All flags defined in**: Split.io dashboard (not in code)

---

## 📝 Exception Handling

### Custom Exception Hierarchy

```python
# src/backoffice/exceptions/exception.py
class BackOfficeError(Exception):
    """Base class for all custom exceptions."""
    
    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        status_code: int | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code

class ClientsServiceError(BackOfficeError):
    """Raised when clients service encounters an error."""
    pass

class DatabaseError(BackOfficeError):
    """Raised when database operations fail."""
    pass
```

### Exception Usage

```python
# ✅ GOOD - Raise with context
if not search_prefix:
    raise ClientsServiceError(
        "Search prefix cannot be empty",
        error_code="INVALID_SEARCH_PREFIX",
        status_code=400,
    )

# ✅ GOOD - Chain exceptions
try:
    result = db.execute(stmt).all()
except Exception as e:
    logger.error(f"Database query failed: {str(e)}")
    raise ClientsServiceError(
        f"Failed to fetch account data: {str(e)}",
        error_code="DATABASE_ERROR",
        status_code=500,
    ) from e
```

### Global Exception Handlers

```python
# src/backoffice/exceptions/global_exception_handler.py
@app.exception_handler(ClientsServiceError)
async def clients_service_error_handler(
    _: Request, exc: ClientsServiceError
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code or 500,
        content={
            "success": False,
            "message": str(exc),
            "errorCode": exc.error_code,
            "item": [],
        },
    )
```

---

## 📋 Logging

### Logging Configuration

```python
# src/backoffice/logging.py
import logging
import sys

def setup_logging() -> logging.Logger:
    logger = logging.getLogger("backoffice")
    
    if settings["IS_LOCAL"]:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        "%(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    )
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logging()
```

### Logging Usage

```python
from src.backoffice.logging import logger

# ✅ GOOD - Structured logging
logger.info(f"Searching accounts with prefix: {search_prefix}")
logger.error(f"Database query failed: {str(e)}")
logger.warning("Empty search prefix provided")

# ✅ GOOD - Performance logging
start_time = time.time()
results = await perform_operation()
end_time = time.time()
duration = (end_time - start_time) * 1000
logger.info(f"✅ Operation completed in {duration:.2f}ms")
```

**Log Format**: `LEVEL - filename.py:line - message`

**Note**: CloudWatch provides timestamps, so we don't include them in the log message format.

---

## 🧪 Testing Patterns

### Unit Tests (pytest)

```python
# src/tests/clients/test_account_api.py
from unittest.mock import patch
from fastapi.testclient import TestClient

def test_get_accounts_by_prefix_success(client: TestClient) -> None:
    """Test successful account search API endpoint"""
    mock_response = [
        {
            "id": 1,
            "accountNumber": "ACME001",
            "accountName": "ACME Corporation",
        }
    ]
    
    with patch(
        "src.backoffice.clients.api.account_api.search_accounts_by_prefix",
        return_value=mock_response,
    ):
        response = client.get("/backoffice/secured/api/v1/accounts/ACME")
    
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["success"] is True
    assert len(json_response["item"]) == 1
```

### Service Layer Tests

```python
# src/tests/clients/test_account_service.py
import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from src.backoffice.clients.service import search_accounts_by_prefix
from src.backoffice.exceptions import ClientsServiceError

@pytest.mark.asyncio
async def test_search_accounts_by_prefix_success():
    """Test successful account search"""
    mock_db = Mock(spec=Session)
    mock_result = Mock()
    mock_result.id = 1
    mock_result.ref_client_code = "ACME001"
    # ... setup mock
    
    mock_db.execute.return_value.all.return_value = [mock_result]
    
    result = await search_accounts_by_prefix("ACME", mock_db)
    
    assert len(result) == 1
    assert result[0].accountNumber == "ACME001"
```

### Test Conventions

- Use `pytest.mark.asyncio` for async tests
- Mock external dependencies (database, APIs)
- Test both success and error cases
- Use descriptive test function names
- Colocate tests with source structure

### Running Tests

```bash
# Run all tests
pytest -v

# Run with coverage
pytest --cov=src/backoffice --cov-report=html

# Run specific test file
pytest src/tests/clients/test_account_api.py

# Run specific test
pytest src/tests/clients/test_account_api.py::test_get_accounts_by_prefix_success
```

---

## 🔧 Environment Variables & Configuration

### Configuration Pattern

```python
# src/backoffice/core/config.py
import os
from dotenv import load_dotenv

load_dotenv()

def get_settings() -> dict:
    """Get application settings from environment variables"""
    return {
        "HOST": os.getenv("HOST", "localhost"),
        "PORT": int(os.getenv("PORT", "8080")),
        "APP_NAME": os.getenv("APP_NAME", "APEX Back Office System"),
        "ENVIRONMENT": os.getenv("ENVIRONMENT", "development"),
        "DEBUG": os.getenv("DEBUG", "False").lower() == "true",
        "IS_LOCAL": os.getenv("IS_LOCAL", "false").lower() == "true",
        "DB_SECRET_NAME": os.getenv("DB_SECRET_NAME", ""),
        # ... more settings
    }

settings = get_settings()
```

### AWS Secrets Manager

```python
# src/backoffice/utils/aws_secrets.py
import boto3
from src.backoffice.logging import logger

def get_secret_value(secret_id: str) -> dict:
    """Retrieve secret from AWS Secrets Manager"""
    try:
        client = boto3.client("secretsmanager", region_name=settings["REGION"])
        response = client.get_secret_value(SecretId=secret_id)
        return json.loads(response["SecretString"])
    except Exception as e:
        logger.error(f"Failed to retrieve secret {secret_id}: {str(e)}")
        raise UtilsError(...) from e
```

---

## 🚀 Deployment & Infrastructure

### Lambda Handler

```python
# src/backoffice/lambda_handler.py
from mangum import Mangum
from src.backoffice.main import app

# Add CORS middleware
app.add_middleware(CORSMiddleware, ...)

# Create the handler
handler = Mangum(app)
```

### CDK Infrastructure

```python
# stacks/apex_back_office_stack.py
from aws_cdk import Stack
from aws_cdk_lib import aws_lambda as _lambda

class BackOfficeStack(Stack):
    def __init__(self, scope, construct_id, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        
        # Define Lambda function
        # Define API Gateway
        # Define RDS Proxy
        # etc.
```

---

## 🛠️ Utility Functions

### Common Utilities

```python
# src/backoffice/utils/common_utils.py
def safe_str(value: str | None) -> str:
    """Safely convert value to string, handling None."""
    return str(value) if value is not None else ""

def format_currency(amount: Decimal | None) -> str:
    """Format decimal as currency string."""
    if amount is None:
        return "0.00"
    return f"{amount:.2f}"
```

---

## 📋 Import Organization

```python
# 1. Standard library
from collections.abc import AsyncGenerator
from typing import Annotated
import time

# 2. Third-party libraries
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

# 3. Local imports (absolute from src/)
from src.backoffice.core import db_dependency
from src.backoffice.logging import logger
from src.backoffice.models import AccountResponseWrapper
from src.backoffice.exceptions import ClientsServiceError
```

---

## ⚠️ Common Pitfalls & Best Practices

### Strictly Enforced

1. ❌ Missing type hints → ✅ Always use type annotations
2. ❌ Direct database queries in API routes → ✅ Use service layer
3. ❌ Synchronous I/O operations → ✅ Use async/await for I/O
4. ❌ Hardcoded secrets → ✅ Use AWS Secrets Manager
5. ❌ Missing error handling → ✅ Use custom exceptions with error codes

### Strongly Recommended

6. ⚠️ Missing performance logging for database queries
7. ⚠️ Not using read-only connections for SELECT queries
8. ⚠️ Missing input validation in service layer
9. ⚠️ Not chaining exceptions with `from e`
10. ⚠️ Missing docstrings for public functions
11. ⚠️ Not using feature flags for new features
12. ⚠️ Hardcoded configuration values

### Code Quality

- **Ruff**: Linting and formatting (configured in `pyproject.toml`)
- **mypy**: Type checking (strict mode enabled)
- **pytest**: Testing framework
- **pre-commit**: Git hooks for quality checks

---

## ✅ New Code Checklist

Before submitting:

**Required:**

- [ ] Type hints on all functions
- [ ] Service layer separation (API → Service → Database)
- [ ] Custom exceptions with error codes
- [ ] Performance logging for database queries
- [ ] Proper use of read-only vs write database connections
- [ ] Ruff linting passes
- [ ] mypy type checking passes
- [ ] Tests written and passing

**Strongly Recommended:**

- [ ] Feature flags for new features
- [ ] Input validation in service layer
- [ ] Docstrings for public functions
- [ ] Error handling with exception chaining
- [ ] No hardcoded secrets or configuration
- [ ] Async/await for I/O operations
- [ ] SQLAlchemy 2.0 core-style queries

**Good Practices:**

- [ ] Use `readonly_db_dependency` for SELECT queries
- [ ] Use `db_dependency` for INSERT/UPDATE/DELETE
- [ ] Log query performance with timing
- [ ] Use Pydantic models for request/response validation
- [ ] Chain exceptions with `from e` for better debugging

---

## 📚 Key Files Reference

- **Main App**: `src/backoffice/main.py`
- **Config**: `src/backoffice/core/config.py`
- **Dependencies**: `src/backoffice/core/deps.py`
- **Database**: `src/backoffice/database/db.py`
- **Exceptions**: `src/backoffice/exceptions/exception.py`
- **Logging**: `src/backoffice/logging.py`
- **Lambda Handler**: `src/backoffice/lambda_handler.py`
- **Models**: `src/backoffice/models/`
- **Feature Flags**: `src/backoffice/utils/feature_flags.py`
- **AWS Secrets**: `src/backoffice/utils/aws_secrets.py`
- **Project Config**: `pyproject.toml`
- **CDK Stack**: `stacks/apex_back_office_stack.py`

---

## 🔍 Code Quality Tools

### Ruff (Linting & Formatting)

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Auto-fix issues
ruff check --fix .
```

**Configuration**: `pyproject.toml` → `[tool.ruff]`

### mypy (Type Checking)

```bash
# Type check
mypy src/backoffice

# Type check with strict mode (already enabled in config)
mypy src/backoffice --strict
```

**Configuration**: `pyproject.toml` → `[tool.mypy]`

### pytest (Testing)

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/backoffice --cov-report=html

# Run specific test file
pytest src/tests/clients/test_account_api.py
```

**Configuration**: `pyproject.toml` → `[tool.pytest.ini_options]`

---

## 🪝 Git Hooks & Pre-commit

**pre-commit** runs on `git commit`:

```yaml
# .pre-commit-config.yaml (if configured)
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    hooks:
      - id: mypy
```

**Setup**: Run `pre-commit install` after cloning

---

## 📝 Pull Request Checklist

**Required:**

- [ ] Code wrapped in Feature Flag (except bugs)
- [ ] Feature flag requested from APEX Release team
- [ ] Comprehensive tests (pytest)
- [ ] Manual testing completed
- [ ] Type hints on all functions
- [ ] Ruff linting passes
- [ ] mypy type checking passes
- [ ] Remove commented-out code (or justify with explanation)
- [ ] TODOs reference JIRA tickets when tracking specific work
- [ ] Acceptance criteria covered

---

**Last Updated**: January 2025

**Recent Changes:**

- Initial documentation creation
- Based on existing codebase patterns and conventions
- Aligned with frontend AGENTS.md structure for consistency
