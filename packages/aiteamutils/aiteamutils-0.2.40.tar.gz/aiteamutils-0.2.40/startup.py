async def startup_event() -> None:
    """Application startup event handler."""
    try:
        # 1. 설정 및 DB 초기화
        init_settings(
            jwt_secret=settings.JWT_SECRET,
            jwt_algorithm=settings.JWT_ALGORITHM,
            db_url=settings.CORE_DB_URL,
            db_echo=settings.DB_ECHO,
            db_pool_size=settings.DB_POOL_SIZE,
            db_max_overflow=settings.DB_MAX_OVERFLOW,
            db_pool_timeout=settings.DB_POOL_TIMEOUT,
            db_pool_recycle=settings.DB_POOL_RECYCLE
        )
        db_service = get_database_service()

        if not db_service or not db_service.engine:
            raise RuntimeError("데이터베이스 서비스 초기화 실패")
            
        # 2. DB 연결 테스트
        async with db_service.engine.begin() as conn:
            await conn.run_sync(lambda _: None)
            logging.info("데이터베이스 연결 성공")
            
        # 3. 테이블 생성
        async with db_service.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logging.info("데이터베이스 테이블 생성 완료")
        
        # 4. 서비스 등록
        register_services()
        service_registry.set_initialized()  # 서비스 등록 완료 표시

        logging.info("서비스 등록 완료")
        
    except Exception as e:
        logging.error(f"애플리케이션 시작 실패: {str(e)}")
        raise RuntimeError(f"애플리케이션 시작 실패: {str(e)}")

async def shutdown_event() -> None:
    """Application shutdown event handler."""
    try:
        # 1. 서비스 레지스트리 초기화
        service_registry.clear()
        logging.info("서비스 레지스트리 초기화 완료")
        
        # 2. 데이터베이스 연결 종료
        db_service = get_database_service()
        if db_service and db_service.engine:
            await db_service.engine.dispose()
            logging.info("데이터베이스 연결 종료")
    except Exception as e:
        logging.error(f"애플리케이션 종료 중 오류 발생: {str(e)}")
        raise 