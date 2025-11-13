import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Portfolio

app = FastAPI(title="Clockwork Portfolio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

COLLECTION = "portfolio"


# Helpers
class PortfolioUpdate(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    accent: Optional[str] = None
    monochrome: Optional[bool] = None
    socials: Optional[list] = None
    projects: Optional[list] = None


def serialize(doc: dict):
    if not doc:
        return doc
    d = doc.copy()
    if "_id" in d:
        d["id"] = str(d.pop("_id"))
    return d


@app.get("/")
async def root():
    return {"status": "ok", "service": "Clockwork Portfolio API"}


@app.get("/api/portfolio")
async def get_portfolio():
    # Singleton: slug == "main"
    doc = db[COLLECTION].find_one({"slug": "main"}) if db else None
    if not doc:
        # Seed a default document if missing
        default = Portfolio(
            username="clockwork",
            role="Roblox UI Designer",
            avatar_url=None,
            bio="Designing intuitive, high-polish Roblox interfaces.",
            accent="#ffffff",
            monochrome=True,
            socials=[],
            projects=[],
        )
        inserted_id = create_document(COLLECTION, default)
        doc = db[COLLECTION].find_one({"_id": ObjectId(inserted_id)})
    return serialize(doc)


@app.put("/api/portfolio")
async def update_portfolio(payload: PortfolioUpdate):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    existing = db[COLLECTION].find_one({"slug": "main"})
    if not existing:
        create_document(COLLECTION, Portfolio(username="clockwork"))
        existing = db[COLLECTION].find_one({"slug": "main"})

    update_data = {k: v for k, v in payload.model_dump(exclude_none=True).items()}
    if not update_data:
        return serialize(existing)

    db[COLLECTION].update_one({"_id": existing["_id"]}, {"$set": update_data})
    updated = db[COLLECTION].find_one({"_id": existing["_id"]})
    return serialize(updated)


@app.get("/test")
async def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
                response["connection_status"] = "Connected"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
