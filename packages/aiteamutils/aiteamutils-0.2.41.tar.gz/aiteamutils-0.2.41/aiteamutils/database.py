from typing import Any, Dict, Optional, Type, AsyncGenerator, TypeVar, List, Union
from sqlalchemy import select, update, and_, Table
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker, Load, joinedload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.pool import QueuePool
from contextlib import asynccontextmanager
from sqlalchemy import or_
from fastapi import Request, Depends
from ulid import ULID
from sqlalchemy.sql import Select
import logging

from .exceptions import ErrorCode, CustomException
from .base_model import Base, BaseColumn
from .enums import ActivityType

T = TypeVar("T", bound=BaseColumn)

# 전역 데이터베이스 서비스 인스턴스
_database_service: Union['DatabaseService', None] = None

def get_database_service() -> 'DatabaseService':
    """DatabaseService 인스턴스를 반환하는 함수
    
    Returns:
        DatabaseService: DatabaseService 인스턴스
        
    Raises:
        CustomException: DatabaseService가 초기화되지 않은 경우
    """
    if _database_service is None:
        raise CustomException(
            ErrorCode.DB_CONNECTION_ERROR,
            detail="Database service is not initialized. Call init_database_service() first.",
            source_function="get_database_service"
        )
    return _database_service

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """데이터베이스 세션을 생성하고 반환하는 비동기 제너레이터.
    
    Yields:
        AsyncSession: 데이터베이스 세션
        
    Raises:
        CustomException: 세션 생성 실패 시
    """
    db_service = get_database_service()
    try:
        async with db_service.get_session() as session:
            yield session
    except Exception as e:
        raise CustomException(
            ErrorCode.DB_CONNECTION_ERROR,
            detail=f"Failed to get database session: {str(e)}",
            source_function="get_db",
            original_error=e
        )
    finally:
        if 'session' in locals():
            await session.close()

def get_database_session(db: AsyncSession = Depends(get_db)) -> 'DatabaseService':
    """DatabaseService 의존성

    Args:
        db (AsyncSession): 데이터베이스 세션

    Returns:
        DatabaseService: DatabaseService 인스턴스
    """
    return DatabaseService(session=db)

class DatabaseService:
    def __init__(
        self,
        db_url: str = None,
        session: AsyncSession = None,
        db_echo: bool = False,
        db_pool_size: int = 5,
        db_max_overflow: int = 10,
        db_pool_timeout: int = 30,
        db_pool_recycle: int = 1800
    ):
        """DatabaseService 초기화.
        
        Args:
            db_url (str, optional): 데이터베이스 URL
            session (AsyncSession, optional): 기존 세션
            db_echo (bool, optional): SQL 로깅 여부
            db_pool_size (int, optional): DB 커넥션 풀 크기
            db_max_overflow (int, optional): 최대 초과 커넥션 수
            db_pool_timeout (int, optional): 커넥션 풀 타임아웃
            db_pool_recycle (int, optional): 커넥션 재활용 시간
        """
        if db_url:
            self.engine = create_async_engine(
                db_url,
                echo=db_echo,
                pool_size=db_pool_size,
                max_overflow=db_max_overflow,
                pool_timeout=db_pool_timeout,
                pool_recycle=db_pool_recycle,
                pool_pre_ping=True,
                poolclass=QueuePool,
            )
            self.session_factory = sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            self.db = None
        elif session:
            self.engine = session.bind
            self.session_factory = sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            self.db = session
        else:
            raise CustomException(
                ErrorCode.DB_CONNECTION_ERROR,
                detail="db_url|session",
                source_function="DatabaseService.__init__"
            )

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """데이터베이스 세션을 생성하고 반환하는 비동기 컨텍스트 매니저."""
        if self.session_factory is None:
            raise CustomException(
                ErrorCode.DB_CONNECTION_ERROR,
                detail="session_factory",
                source_function="DatabaseService.get_session"
            )
        
        async with self.session_factory() as session:
            try:
                yield session
            finally:
                await session.close()

    def preprocess_data(self, model: Type[Base], input_data: Dict[str, Any], existing_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """입력 데이터를 전처리하여 extra_data로 분리
        
        Args:
            model (Type[Base]): SQLAlchemy 모델 클래스
            input_data (Dict[str, Any]): 입력 데이터
            existing_data (Dict[str, Any], optional): 기존 데이터. Defaults to None.
            
        Returns:
            Dict[str, Any]: 전처리된 데이터
        """
        model_attrs = {
            attr for attr in dir(model)
            if not attr.startswith('_') and not callable(getattr(model, attr))
        }
        model_data = {}
        extra_data = {}

        # 기존 extra_data가 있으면 복사
        if existing_data and "extra_data" in existing_data:
            extra_data = existing_data["extra_data"].copy()

        # 스웨거 자동생성 필드 패턴
        swagger_patterns = {"additionalProp1", "additionalProp2", "additionalProp3"}

        # 모든 필드와 extra_data 분리
        for key, value in input_data.items():
            # 스웨거 자동생성 필드는 무시
            if key in swagger_patterns:
                continue
            
            if key in model_attrs:
                model_data[key] = value
            else:
                extra_data[key] = value

        # extra_data가 있고, 모델이 extra_data 속성을 가지고 있으면 추가
        if extra_data and "extra_data" in model_attrs:
            model_data["extra_data"] = extra_data
        
        return model_data

    ############################
    # 2. 트랜잭션 및 세션 관리 #
    ############################
    @asynccontextmanager
    async def transaction(self):
        """트랜잭션 컨텍스트 매니저

        트랜잭션 범위를 명시적으로 관리합니다.
        with 문을 벗어날 때 자동으로 commit 또는 rollback됩니다.

        Example:
            async with db_service.transaction():
                await db_service.create_entity(...)
                await db_service.update_entity(...)
        """
        try:
            yield
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            raise e

    #######################
    # 3. 데이터 처리     #
    #######################
    async def create_entity(self, model: Type[Base], entity_data: Dict[str, Any]) -> Any:
        """새로운 엔티티를 생성합니다.
        
        Args:
            model (Type[Base]): 생성할 모델 클래스
            entity_data (Dict[str, Any]): 엔티티 데이터
            
        Returns:
            Any: 생성된 엔티티
            
        Raises:
            CustomException: 데이터베이스 오류 발생
        """
        try:
            # 데이터 전처리 및 모델 인스턴스 생성
            processed_data = self.preprocess_data(model, entity_data)
            
            # 외래 키 필드 검증
            foreign_key_fields = {
                field: value for field, value in processed_data.items()
                if any(fk.parent.name == field for fk in model.__table__.foreign_keys)
            }
            if foreign_key_fields:
                await self.validate_foreign_key_fields(model, foreign_key_fields)
            
            entity = model(**processed_data)
            
            self.db.add(entity)
            await self.db.flush()
            await self.db.commit()
            await self.db.refresh(entity)
            return entity
        except IntegrityError as e:
            await self.db.rollback()
            error_str = str(e)
            
            if "duplicate key" in error_str.lower():
                # 중복 키 에러 처리
                field = None
                value = None
                
                # 에러 메시지에서 필드와 값 추출
                if "Key (" in error_str and ") already exists" in error_str:
                    field_value = error_str.split("Key (")[1].split(") already exists")[0]
                    if "=" in field_value:
                        field, value = field_value.split("=")
                        field = field.strip("() ")
                        value = value.strip("() ")
                
                if not field:
                    field = "id"  # 기본값
                    value = str(entity_data.get(field, ""))
                
                raise CustomException(
                    ErrorCode.DUPLICATE_ERROR,
                    detail=f"{model.__tablename__}|{field}|{value}",
                    source_function="DatabaseService.create_entity",
                    original_error=e
                )
            elif "violates foreign key constraint" in error_str.lower():
                # 외래키 위반 에러는 validate_foreign_key_fields에서 이미 처리됨
                raise CustomException(
                    ErrorCode.FOREIGN_KEY_VIOLATION,
                    detail=error_str,
                    source_function="DatabaseService.create_entity",
                    original_error=e
                )
            else:
                raise CustomException(
                    ErrorCode.DB_CREATE_ERROR,
                    detail=f"Failed to create {model.__name__}: {str(e)}",
                    source_function="DatabaseService.create_entity",
                    original_error=e
                )
        except CustomException as e:
            await self.db.rollback()
            raise e
        except Exception as e:
            await self.db.rollback()
            raise CustomException(
                ErrorCode.UNEXPECTED_ERROR,
                detail=f"Unexpected error while creating {model.__name__}: {str(e)}",
                source_function="DatabaseService.create_entity",
                original_error=e
            )

    async def retrieve_entity(
        self,
        model: Type[T],
        conditions: Dict[str, Any],
        join_options: Optional[Union[Load, List[Load]]] = None
    ) -> Optional[T]:
        """조건에 맞는 단일 엔티티를 조회합니다.
        
        Args:
            model: 모델 클래스
            conditions: 조회 조건
            join_options: SQLAlchemy의 joinedload 옵션 또는 옵션 리스트
            
        Returns:
            Optional[T]: 조회된 엔티티 또는 None
            
        Raises:
            CustomException: 데이터베이스 작업 중 오류 발생 시
        """
        try:
            stmt = select(model)
            
            # Join 옵션 적용
            if join_options is not None:
                if isinstance(join_options, list):
                    stmt = stmt.options(*join_options)
                else:
                    stmt = stmt.options(join_options)
            
            # 조건 적용
            for key, value in conditions.items():
                stmt = stmt.where(getattr(model, key) == value)
            
            result = await self.execute_query(stmt)
            return result.unique().scalar_one_or_none()
            
        except Exception as e:
            raise CustomException(
                ErrorCode.DB_QUERY_ERROR,
                detail=str(e),
                source_function="DatabaseService.retrieve_entity",
                original_error=e
            )

    async def update_entity(
        self,
        model: Type[Base],
        conditions: Dict[str, Any],
        update_data: Dict[str, Any]
    ) -> Optional[Base]:
        """엔티티를 업데이트합니다.

        Args:
            model (Type[Base]): 엔티티 모델 클래스
            conditions (Dict[str, Any]): 업데이트할 엔티티 조회 조건
            update_data (Dict[str, Any]): 업데이트할 데이터

        Returns:
            Optional[Base]: 업데이트된 엔티티

        Raises:
            CustomException: 데이터베이스 오류 발생
        """
        try:
            # 엔티티 조회
            stmt = select(model)
            for key, value in conditions.items():
                stmt = stmt.where(getattr(model, key) == value)
            
            result = await self.db.execute(stmt)
            entity = result.scalar_one_or_none()
            
            if not entity:
                return None

            # 기존 데이터를 딕셔너리로 변환
            existing_data = {
                column.name: getattr(entity, column.name)
                for column in entity.__table__.columns
            }

            # 데이터 전처리
            processed_data = self.preprocess_data(model, update_data, existing_data)
            
            # UPDATE 문 생성 및 실행
            update_stmt = (
                update(model)
                .where(and_(*[getattr(model, key) == value for key, value in conditions.items()]))
                .values(**processed_data)
                .returning(model)
            )
            
            result = await self.db.execute(update_stmt)
            await self.db.commit()
            
            # 업데이트된 엔티티 반환
            updated_entity = result.scalar_one()
            return updated_entity
            
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise CustomException(
                ErrorCode.DB_UPDATE_ERROR,
                detail=f"Failed to update {model.__name__}: {str(e)}",
                source_function="DatabaseService.update_entity",
                original_error=e
            )
        except Exception as e:
            await self.db.rollback()
            raise CustomException(
                ErrorCode.UNEXPECTED_ERROR,
                detail=f"Unexpected error while updating {model.__name__}: {str(e)}",
                source_function="DatabaseService.update_entity",
                original_error=e
            )

    async def delete_entity(self, entity: T) -> None:
        """엔티티를 실제로 삭제합니다.

        Args:
            entity (T): 삭제할 엔티티

        Raises:
            CustomException: 데이터베이스 오류 발생
        """
        try:
            await self.db.delete(entity)
            await self.db.flush()
            await self.db.commit()
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise CustomException(
                ErrorCode.DB_DELETE_ERROR,
                detail=f"Failed to delete entity: {str(e)}",
                source_function="DatabaseService.delete_entity",
                original_error=e
            )
        except Exception as e:
            await self.db.rollback()
            raise CustomException(
                ErrorCode.UNEXPECTED_ERROR,
                detail=f"Unexpected error while deleting entity: {str(e)}",
                source_function="DatabaseService.delete_entity",
                original_error=e
            )

    async def soft_delete_entity(self, model: Type[T], ulid: str) -> Optional[T]:
        """엔티티를 소프트 삭제합니다 (is_deleted = True).

        Args:
            model (Type[T]): 엔티티 모델
            ulid (str): 삭제할 엔티티의 ULID

        Returns:
            Optional[T]: 삭제된 엔티티, 없으면 None

        Raises:
            CustomException: 데이터베이스 오류 발생
        """
        try:
            # 1. 엔티티 조회
            stmt = select(model).where(
                and_(
                    model.ulid == ulid,
                    model.is_deleted == False
                )
            )
            result = await self.db.execute(stmt)
            entity = result.scalar_one_or_none()
            
            if not entity:
                return None
            
            # 2. 소프트 삭제 처리
            stmt = update(model).where(
                model.ulid == ulid
            ).values(
                is_deleted=True
            )
            await self.db.execute(stmt)
            await self.db.commit()
            
            # 3. 업데이트된 엔티티 반환
            return entity
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise CustomException(
                ErrorCode.DB_DELETE_ERROR,
                detail=f"Failed to soft delete {model.__name__}: {str(e)}",
                source_function="DatabaseService.soft_delete_entity",
                original_error=e
            )
        except Exception as e:
            await self.db.rollback()
            raise CustomException(
                ErrorCode.UNEXPECTED_ERROR,
                detail=f"Unexpected error while soft deleting {model.__name__}: {str(e)}",
                source_function="DatabaseService.soft_delete_entity",
                original_error=e
            )

    async def list_entities(
        self,
        model: Type[T],
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        joins: Optional[List[Any]] = None
    ) -> List[T]:
        """엔티티 목록을 조회합니다.
        
        Args:
            model (Type[T]): 엔티티 모델
            skip (int): 건너뛸 레코드 수
            limit (int): 조회할 최대 레코드 수
            filters (Optional[Dict[str, Any]]): 필터 조건
                - field: value -> field = value
                - field__ilike: value -> field ILIKE value
                - search: [(field, pattern), ...] -> OR(field ILIKE pattern, ...)
            joins (Optional[List[Any]]): 조인할 관계들 (joinedload 객체 리스트)
            
        Returns:
            List[T]: 조회된 엔티티 목록
            
        Raises:
            CustomException: 데이터베이스 오류 발생
        """
        try:
            query = select(model)
            conditions = []

            if filters:
                for key, value in filters.items():
                    if key == "search" and isinstance(value, list):
                        # 전체 검색 조건
                        search_conditions = []
                        for field_name, pattern in value:
                            field = getattr(model, field_name)
                            search_conditions.append(field.ilike(pattern))
                        if search_conditions:
                            conditions.append(or_(*search_conditions))
                    elif "__ilike" in key:
                        # ILIKE 검색
                        field_name = key.replace("__ilike", "")
                        field = getattr(model, field_name)
                        conditions.append(field.ilike(value))
                    else:
                        # 일반 필터
                        field = getattr(model, key)
                        conditions.append(field == value)

            if conditions:
                query = query.where(and_(*conditions))
            
            if joins:
                for join_option in joins:
                    query = query.options(join_option)
            
            query = query.offset(skip).limit(limit)
            result = await self.db.execute(query)
            return result.scalars().unique().all()
        except SQLAlchemyError as e:
            raise CustomException(
                ErrorCode.DB_READ_ERROR,
                detail=f"Failed to list {model.__name__}: {str(e)}",
                source_function="DatabaseService.list_entities",
                original_error=e
            )
        except Exception as e:
            raise CustomException(
                ErrorCode.UNEXPECTED_ERROR,
                detail=f"Unexpected error while listing {model.__name__}: {str(e)}",
                source_function="DatabaseService.list_entities",
                original_error=e
            )

    ######################
    # 4. 검증           #
    ######################
    async def validate_unique_fields(
        self,
        table_or_model: Union[Table, Type[Any]],
        fields: Dict[str, Any],
        source_function: str,
        error_code: ErrorCode = ErrorCode.DUPLICATE_ERROR
    ) -> None:
        """
        데이터베이스에서 필드의 유일성을 검증합니다.

        Args:
            table_or_model: 검증할 테이블 또는 모델 클래스
            fields: 검증할 필드와 값의 딕셔너리 {"field_name": value}
            source_function: 호출한 함수명
            error_code: 사용할 에러 코드 (기본값: DUPLICATE_ERROR)

        Raises:
            CustomException: 중복된 값이 존재할 경우
        """
        try:
            conditions = []
            for field_name, value in fields.items():
                conditions.append(getattr(table_or_model, field_name) == value)
            
            query = select(table_or_model).where(or_(*conditions))
            result = await self.db.execute(query)
            existing = result.scalar_one_or_none()

            if existing:
                table_name = table_or_model.name if hasattr(table_or_model, 'name') else table_or_model.__tablename__
                # 단일 필드인 경우
                if len(fields) == 1:
                    field_name, value = next(iter(fields.items()))
                    detail = f"{table_name}|{field_name}|{value}"
                # 복수 필드인 경우
                else:
                    fields_str = "|".join(f"{k}:{v}" for k, v in fields.items())
                    detail = f"{table_name}|{fields_str}"

                raise CustomException(
                    error_code,
                    detail=detail,
                    source_function="DatabaseService.validate_unique_fields"
                )

        except CustomException as e:
            raise CustomException(
                e.error_code,
                detail=e.detail,
                source_function="DatabaseService.validate_unique_fields",
                original_error=e.original_error,
                parent_source_function=e.source_function
            )
        except Exception as e:
            raise CustomException(
                ErrorCode.DB_QUERY_ERROR,
                detail=str(e),
                source_function="DatabaseService.validate_unique_fields",
                original_error=e
            )

    async def validate_foreign_key_fields(
        self,
        model: Type[T],
        fields: Dict[str, Any]
    ) -> None:
        """외래 키 필드를 검증합니다.
        
        Args:
            model (Type[T]): 검증할 모델 클래스
            fields (Dict[str, Any]): 검증할 외래 키 필드와 값
            
        Raises:
            CustomException: 참조하는 레코드가 존재하지 않는 경우
        """
        for field, value in fields.items():
            # 외래 키 관계 정보 가져오기
            foreign_key = next(
                (fk for fk in model.__table__.foreign_keys if fk.parent.name == field),
                None
            )
            if foreign_key and value:
                # 참조하는 테이블에서 레코드 존재 여부 확인
                referenced_table = foreign_key.column.table
                query = select(referenced_table).where(
                    and_(
                        foreign_key.column == value,
                        getattr(referenced_table.c, 'is_deleted', None) == False
                    )
                )
                result = await self.db.execute(query)
                if not result.scalar_one_or_none():
                    raise CustomException(
                        ErrorCode.FOREIGN_KEY_VIOLATION,
                        detail=f"{referenced_table.name}|{field}|{value}",
                        source_function="DatabaseService.validate_foreign_key_fields"
                    )

    #######################
    # 5. 쿼리 실행      #
    #######################
    async def create_log(self, model: Type[Base], log_data: Dict[str, Any], request: Request = None) -> None:
        """로그를 생성합니다.
        
        Args:
            model: 로그 모델 클래스
            log_data: 로그 데이터
            request: FastAPI 요청 객체
        
        Returns:
            생성된 로그 엔티티
        
        Raises:
            CustomException: 로그 생성 실패 시
        """
        try:
            # 공통 필드 추가 (ULID를 문자열로 변환)
            log_data["ulid"] = str(ULID())
            
            # request가 있는 경우 user-agent와 ip 정보 추가
            if request:
                log_data["user_agent"] = request.headers.get("user-agent")
                log_data["ip_address"] = request.headers.get("x-forwarded-for")
            
            # 데이터 전처리
            processed_data = self.preprocess_data(model, log_data)
            entity = model(**processed_data)
            
            # 로그 엔티티 저장
            self.db.add(entity)
            await self.db.flush()
            
            return entity
            
        except Exception as e:
            logging.error(f"Failed to create log: {str(e)}")
            # 로그 생성 실패는 원래 작업에 영향을 주지 않도록 함
            return None

    async def soft_delete(
        self,
        model: Type[T],
        entity_id: str,
        source_function: str = None,
        request: Request = None
    ) -> None:
        """엔티티를 소프트 삭제합니다.
        
        Args:
            model: 모델 클래스
            entity_id: 삭제할 엔티티의 ID
            source_function: 호출한 함수명
            request: FastAPI 요청 객체
            
        Raises:
            CustomException: 데이터베이스 작업 실패 시
        """
        try:
            # 1. 엔티티 조회
            stmt = select(model).where(
                and_(
                    model.ulid == entity_id,
                    model.is_deleted == False
                )
            )
            result = await self.db.execute(stmt)
            entity = result.scalar_one_or_none()
            
            if not entity:
                raise CustomException(
                    ErrorCode.NOT_FOUND,
                    detail=f"{model.__name__}|{entity_id}",
                    source_function=source_function or "DatabaseService.soft_delete"
                )
            
            # 2. 소프트 삭제 처리
            stmt = update(model).where(
                model.ulid == entity_id
            ).values(
                is_deleted=True
            )
            await self.db.execute(stmt)
            await self.db.commit()
            
            # 3. 삭제 로그 생성
            if request:
                activity_type = f"{model.__tablename__.upper()}_DELETED"
                await self.create_log({
                    "type": activity_type,
                    "fk_table": model.__tablename__,
                    "extra_data": {
                        f"{model.__tablename__}_ulid": entity_id
                    }
                }, request)
                
        except CustomException as e:
            await self.db.rollback()
            raise CustomException(
                e.error_code,
                detail=e.detail,
                source_function=source_function or "DatabaseService.soft_delete",
                original_error=e.original_error,
                parent_source_function=e.source_function
            )
        except Exception as e:
            await self.db.rollback()
            raise CustomException(
                ErrorCode.DB_DELETE_ERROR,
                detail=str(e),
                source_function=source_function or "DatabaseService.soft_delete",
                original_error=e
            )

    async def get_entity(self, model: Type[T], ulid: str) -> Optional[T]:
        """ULID로 엔티티를 조회합니다.
        
        Args:
            model (Type[T]): 엔티티 모델
            ulid (str): 조회할 엔티티의 ULID
            
        Returns:
            Optional[T]: 조회된 엔티티 또는 None
            
        Raises:
            CustomException: 데이터베이스 오류 발생
        """
        try:
            query = select(model).where(
                and_(
                    model.ulid == ulid,
                    model.is_deleted == False
                )
            )
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise CustomException(
                ErrorCode.DB_READ_ERROR,
                detail=f"Failed to get {model.__name__}: {str(e)}",
                source_function="DatabaseService.get_entity",
                original_error=e
            )
        except Exception as e:
            raise CustomException(
                ErrorCode.UNEXPECTED_ERROR,
                detail=f"Unexpected error while getting {model.__name__}: {str(e)}",
                source_function="DatabaseService.get_entity",
                original_error=e
            )

    async def execute_query(self, query: Select) -> Any:
        """SQL 쿼리를 실행하고 결과를 반환합니다.

        Args:
            query (Select): 실행할 SQLAlchemy 쿼리

        Returns:
            Any: 쿼리 실행 결과

        Raises:
            CustomException: 데이터베이스 작업 중 오류 발생 시
        """
        try:
            if self.db is not None:
                return await self.db.execute(query)
            
            async with self.get_session() as session:
                result = await session.execute(query)
                return result
        except Exception as e:
            raise CustomException(
                ErrorCode.DB_QUERY_ERROR,
                detail=str(e),
                source_function=f"{self.__class__.__name__}.execute_query",
                original_error=e
            )

    async def execute(self, stmt):
        """SQL 문을 실행합니다.
        
        Args:
            stmt: 실행할 SQL 문
            
        Returns:
            Result: 실행 결과
            
        Raises:
            CustomException: 데이터베이스 오류 발생
        """
        try:
            return await self.db.execute(stmt)
        except SQLAlchemyError as e:
            raise CustomException(
                ErrorCode.DB_QUERY_ERROR,
                detail=str(e),
                source_function="DatabaseService.execute",
                original_error=e
            )
        except Exception as e:
            raise CustomException(
                ErrorCode.UNEXPECTED_ERROR,
                detail=str(e),
                source_function="DatabaseService.execute",
                original_error=e
            )

    async def commit(self) -> None:
        """현재 세션의 변경사항을 데이터베이스에 커밋합니다."""
        try:
            await self.db.commit()
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise CustomException(
                ErrorCode.DB_QUERY_ERROR,
                detail=str(e),
                source_function="DatabaseService.commit",
                original_error=e
            )

    async def rollback(self) -> None:
        """현재 세션의 변경사항을 롤백합니다."""
        try:
            await self.db.rollback()
        except SQLAlchemyError as e:
            raise CustomException(
                ErrorCode.DB_QUERY_ERROR,
                detail=str(e),
                source_function="DatabaseService.rollback",
                original_error=e
            )

    async def flush(self) -> None:
        """현재 세션의 변경사항을 데이터베이스에 플러시합니다."""
        try:
            await self.db.flush()
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise CustomException(
                ErrorCode.DB_QUERY_ERROR,
                detail=str(e),
                source_function="DatabaseService.flush",
                original_error=e
            )

    async def refresh(self, entity: Any) -> None:
        """엔티티를 데이터베이스의 최신 상태로 리프레시합니다.

        Args:
            entity: 리프레시할 엔티티
        """
        try:
            await self.db.refresh(entity)
        except SQLAlchemyError as e:
            raise CustomException(
                ErrorCode.DB_QUERY_ERROR,
                detail=str(e),
                source_function="DatabaseService.refresh",
                original_error=e
            )

def init_database_service(
    db_url: str,
    db_echo: bool = False,
    db_pool_size: int = 5,
    db_max_overflow: int = 10,
    db_pool_timeout: int = 30,
    db_pool_recycle: int = 1800
) -> DatabaseService:
    """데이터베이스 서비스를 초기화합니다.
    
    Args:
        db_url (str): 데이터베이스 URL
        db_echo (bool, optional): SQL 로깅 여부
        db_pool_size (int, optional): DB 커넥션 풀 크기
        db_max_overflow (int, optional): 최대 초과 커넥션 수
        db_pool_timeout (int, optional): 커넥션 풀 타임아웃
        db_pool_recycle (int, optional): 커넥션 재활용 시간
        
    Returns:
        DatabaseService: 초기화된 데이터베이스 서비스 인스턴스
        
    Raises:
        CustomException: 데이터베이스 초기화 실패 시
    """
    try:
        global _database_service
        if _database_service is not None:
            logging.info("Database service already initialized")
            return _database_service
            
        logging.info(f"Initializing database service with URL: {db_url}")
        _database_service = DatabaseService(
            db_url=db_url,
            db_echo=db_echo,
            db_pool_size=db_pool_size,
            db_max_overflow=db_max_overflow,
            db_pool_timeout=db_pool_timeout,
            db_pool_recycle=db_pool_recycle
        )
        
        if not _database_service.engine:
            raise CustomException(
                ErrorCode.DB_CONNECTION_ERROR,
                detail="Database engine initialization failed",
                source_function="init_database_service"
            )
            
        logging.info("Database service initialized successfully")
        return _database_service
    except Exception as e:
        logging.error(f"Failed to initialize database service: {str(e)}")
        raise CustomException(
            ErrorCode.DB_CONNECTION_ERROR,
            detail=f"Failed to initialize database service: {str(e)}",
            source_function="init_database_service",
            original_error=e
        )