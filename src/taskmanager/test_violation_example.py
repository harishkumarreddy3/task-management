"""
TEST FILE - Intentionally violates AGENTS.md guidelines for testing PR Agent
Use this file to create a PR and verify the agent catches guideline violations.

EXPECTED VIOLATIONS:
1. Missing type hints (AGENTS.md requires type hints on all functions)
2. Using legacy ORM query style instead of SQLAlchemy 2.0 core-style
3. Missing performance logging for database query
4. Direct database query in API route (should use service layer)
5. Missing docstring
6. Not using custom exception with error_code
7. Missing input validation
8. Hardcoded configuration value
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# VIOLATION: Missing type hints, missing docstring
router = APIRouter()

# VIOLATION: Direct database query in API route (should be in service layer)
# VIOLATION: Missing response_model
# VIOLATION: Missing type hints on parameters and return type
@router.get("/accounts/{prefix}")
async def get_accounts(prefix, db: Session = Depends()):
    # VIOLATION: No input validation
    # VIOLATION: Using legacy ORM-style query (should use SQLAlchemy 2.0 select())
    accounts = db.query(Account).filter_by(prefix=prefix).all()
    
    # VIOLATION: No performance logging for database query
    # VIOLATION: Hardcoded limit instead of configuration
    if len(accounts) > 100:
        accounts = accounts[:100]
    
    return accounts


# VIOLATION: No type hints on function parameters or return type
# VIOLATION: Missing docstring
def process_data(value):
    # VIOLATION: Using generic Exception instead of custom exception
    if not value:
        raise Exception("Value cannot be empty")
    
    return {"result": value}


# VIOLATION: Synchronous I/O operation (should be async)
# VIOLATION: Missing type hints
def fetch_external_data(url):
    import requests  # VIOLATION: Should use httpx for async
    response = requests.get(url)
    return response.json()


# CORRECT EXAMPLE (for comparison):
# This follows the guidelines:
"""
from sqlalchemy import select
from src.backoffice.logging import logger
from src.backoffice.exceptions import ClientsServiceError

async def search_accounts_by_prefix(
    search_prefix: str, db: Session
) -> list[AccountItem]:
    '''Search accounts by prefix with performance logging.'''
    start_time = time.time()
    logger.info(f"Searching accounts with prefix: {search_prefix}")
    
    if not search_prefix.strip():
        raise ClientsServiceError(
            "Search prefix cannot be empty",
            error_code="INVALID_SEARCH_PREFIX",
            status_code=400,
        )
    
    stmt = select(ShippingEntity).where(
        ShippingEntity.ref_client_code.ilike(f"{search_prefix}%")
    ).limit(100)
    
    results = db.execute(stmt).all()
    
    query_duration = (time.time() - start_time) * 1000
    logger.info(f"Database query completed in {query_duration:.2f}ms")
    
    return results
"""

