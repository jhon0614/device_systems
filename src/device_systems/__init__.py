def main() -> None:
    import uvicorn

    uvicorn.run("device_systems.main:app", host="127.0.0.1", port=8000)
