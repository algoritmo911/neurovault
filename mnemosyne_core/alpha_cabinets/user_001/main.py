import json
import os
from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


class MemoryCreate(BaseModel):
    title: str
    content: str


class Memory(MemoryCreate):
    id: int


# File-based persistence
MEMORIES_FILE = os.path.join(os.path.dirname(__file__), "memories.json")


def load_memories() -> List[Memory]:
    if not os.path.exists(MEMORIES_FILE):
        return []
    try:
        with open(MEMORIES_FILE, "r") as f:
            data = json.load(f)
            return [Memory(**item) for item in data]
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_memories(memories: List[Memory]):
    with open(MEMORIES_FILE, "w") as f:
        json.dump([mem.model_dump() for mem in memories], f, indent=4)


def get_next_id(memories: List[Memory]) -> int:
    if not memories:
        return 1
    return max(mem.id for mem in memories) + 1


app = FastAPI(
    title="Alpha User 001 Cabinet API",
    description="API for managing personal memories for user 001.",
    version="0.1.0",
)


@app.get("/")
def read_root():
    return {"message": "Welcome to your personal Alpha Cabinet, User 001."}


@app.post("/memories/", response_model=Memory)
def create_memory(memory: MemoryCreate):
    memories = load_memories()
    new_id = get_next_id(memories)
    new_memory = Memory(id=new_id, **memory.model_dump())
    memories.append(new_memory)
    save_memories(memories)
    return new_memory


@app.get("/memories/", response_model=List[Memory])
def get_memories():
    return load_memories()


@app.get("/memories/{memory_id}", response_model=Memory)
def get_memory(memory_id: int):
    memories = load_memories()
    for memory in memories:
        if memory.id == memory_id:
            return memory
    raise HTTPException(status_code=404, detail="Memory not found")


@app.put("/memories/{memory_id}", response_model=Memory)
def update_memory(memory_id: int, updated_memory: MemoryCreate):
    memories = load_memories()
    memory_to_update = None
    for mem in memories:
        if mem.id == memory_id:
            memory_to_update = mem
            break

    if not memory_to_update:
        raise HTTPException(status_code=404, detail="Memory not found")

    memory_to_update.title = updated_memory.title
    memory_to_update.content = updated_memory.content
    save_memories(memories)
    return memory_to_update


@app.delete("/memories/{memory_id}")
def delete_memory(memory_id: int):
    memories = load_memories()
    initial_len = len(memories)
    memories = [mem for mem in memories if mem.id != memory_id]

    if len(memories) == initial_len:
        raise HTTPException(status_code=404, detail="Memory not found")

    save_memories(memories)
    return {"message": "Memory deleted successfully"}
