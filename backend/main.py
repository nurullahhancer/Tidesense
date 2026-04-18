from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from pydantic import BaseModel
from database import get_db
import uvicorn

app = FastAPI(title="TideSense API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    username: str
    password: str
    role: str

@app.post("/login")
def login_user(req: LoginRequest, db: Session = Depends(get_db)):
    try:
        if req.role == 'admin':
            query = text("SELECT first_name, last_name FROM admins WHERE first_name = :user AND passwords = :pass")
        elif req.role == 'researcher':
            query = text("SELECT first_name, last_name FROM researchers WHERE first_name = :user AND passwords = :pass")
        else:
            query = text("SELECT first_name, last_name FROM users WHERE first_name = :user AND passwords = :pass")
            
        result = db.execute(query, {"user": req.username, "pass": req.password}).fetchone()
        
        if result:
            return {"success": True, "user": {"first_name": result[0], "last_name": result[1]}}
        else:
            return {"success": False, "detail": "Geçersiz kullanıcı adı veya şifre"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/readings/latest")
def get_latest_readings(db: Session = Depends(get_db)):
    try:
        query = text("""
            SELECT time, sensor_id, water_level, temperature, humidity
            FROM sensor_readings ORDER BY time DESC LIMIT 10
        """)
        result = db.execute(query).fetchall()
        
        readings = []
        for row in result:
            readings.append({
                "time": row[0], "sensor_id": row[1], "water_level": row[2],
                "temperature": row[3], "humidity": row[4],
                "status": "Kritik" if row[2] > 150 else "Normal"
            })
        return readings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
