from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter()
@router.get("/accounts/{prefix}")
async def get_accounts(prefix, db: Session = Depends()):

    accounts = db.query(Account).filter_by(prefix=prefix).all()
    
    if len(accounts) > 100:
        accounts = accounts[:100]
    
    return accounts

def process_data(value):

    if not value:
        raise Exception("Value cannot be empty")
    
    return {"result": value}


def fetch_external_data(url):
    import requests
    response = requests.get(url)
    return response.json()