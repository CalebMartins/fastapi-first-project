from fastapi import FastAPI
from .database import engine, Base
from .routers import post, user, authentication, vote
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

Base.metadata.create_all(bind=engine)

origins = ["*"]

app.add_middleware(
   CORSMiddleware,
   allow_origins=origins,
   allow_credentials=True,
   allow_methods=["*"],
   allow_headers=["*"], 
)

app.include_router(post.router)
app.include_router(user.router)
app.include_router(authentication.router)
app.include_router(vote.router)
       
@app.get('/')
def root():
   return {"detail": "/docs for documentation"}
