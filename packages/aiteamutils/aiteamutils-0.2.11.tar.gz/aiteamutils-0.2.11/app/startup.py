async def shutdown_event() -> None:
    """Application shutdown event handler."""
    db_service = get_database_service()
    await db_service.engine.dispose() 