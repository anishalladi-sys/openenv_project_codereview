from fastapi import FastAPI
from environment import CodeReviewEnvironment

app = FastAPI()
env = CodeReviewEnvironment()

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/reset")
def reset():
    obs = env.reset()
    return {"status": "ok", "observation": obs}

@app.post("/step")
def step(action: dict):
    obs, reward, done, info = env.step(action)
    return {"observation": obs, "reward": reward, "done": done, "info": info}

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)