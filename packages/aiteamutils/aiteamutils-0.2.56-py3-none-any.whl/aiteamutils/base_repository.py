"""기본 레포지토리 모듈."""
from typing import TypeVar, Generic, Dict, Any, List, Optional, Type, Union
from sqlalchemy.orm import DeclarativeBase, Load
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import select, or_, and_
from .exceptions import CustomException, ErrorCode
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import Select
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType", bound=DeclarativeBase)

class BaseRepository(Generic[ModelType]):
    ##################
    # 1. 초기화 영역 #
    ##################
    def __init__(self, session: AsyncSession, model: Type[ModelType]):
        """
        Args:
            session (AsyncSession): 데이터베이스 세션
            model (Type[ModelType]): 모델 클래스
        """
        self.session = session
        self.model = model
    
    @property
    def session(self):
        """현재 세션을 반환합니다."""
        if self._session is None:
            raise CustomException(
                ErrorCode.DB_CONNECTION_ERROR,
                detail="Database session is not set",
                source_function=f"{self.__class__.__name__}.session"
            )
        return self._session
    
    @session.setter
    def session(self, value):
        """세션을 설정합니다."""
        self._session = value

    #######################
    # 2. CRUD 작업     #
    #######################
    async def get(
        self,
        ulid: str
    ) -> Optional[Dict[str, Any]]:
        """ULID로 엔티티를 조회합니다."""
        try:
            stmt = select(self.model).filter_by(ulid=ulid, is_deleted=False)
            result = await self.session.execute(stmt)
            entity = result.scalars().unique().first()
            
            if not entity:
                raise CustomException(
                    ErrorCode.DB_NO_RESULT,
                    detail=f"{self.model.__tablename__}|ulid|{ulid}",
                    source_function=f"{self.__class__.__name__}.get"
                )
            return entity
        except CustomException as e:
            e.detail = f"Repository error for {self.model.__tablename__}: {e.detail}"
            e.source_function = f"{self.__class__.__name__}.get -> {e.source_function}"
            raise e
        except SQLAlchemyError as e:
            raise CustomException(
                ErrorCode.DB_QUERY_ERROR,
                detail=f"Database error in {self.model.__tablename__}: {str(e)}",
                source_function=f"{self.__class__.__name__}.get",
                original_error=e
            )

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Dict[str, Any] | None = None,
        search_params: Dict[str, Any] | None = None
    ) -> List[Any]:
        """엔티티 목록을 조회합니다."""
        try:
            stmt = select(self.model).where(self.model.is_deleted == False)

            # 필터 적용
            if filters:
                stmt = self._apply_filters(stmt, filters)

            # 검색 적용
            if search_params:
                stmt = self._apply_search_params(stmt, search_params)

            # 페이지네이션 적용
            stmt = stmt.limit(limit).offset(skip)

            result = await self.session.execute(stmt)
            return result.scalars().unique().all()

        except SQLAlchemyError as e:
            raise CustomException(
                ErrorCode.DB_QUERY_ERROR,
                detail=f"Unexpected repository list error in {self.model.__tablename__}: {str(e)}",
                source_function=f"{self.__class__.__name__}.list",
                original_error=e,
            )

    async def create(self, data: Dict[str, Any]) -> ModelType:
        """새로운 엔티티를 생성합니다."""
        try:
            entity = self.model(**data)
            self.session.add(entity)
            await self.session.flush()
            await self.session.refresh(entity)
            return entity
        except IntegrityError as e:
            await self.session.rollback()
            self._handle_integrity_error(e, "create", data)
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise CustomException(
                ErrorCode.DB_CREATE_ERROR,
                detail=f"Database create error in {self.model.__tablename__}: {str(e)}",
                source_function=f"{self.__class__.__name__}.create",
                original_error=e
            )

    async def update(self, ulid: str, data: Dict[str, Any]) -> Optional[ModelType]:
        """기존 엔티티를 수정합니다."""
        try:
            stmt = select(self.model).filter_by(ulid=ulid, is_deleted=False)
            result = await self.session.execute(stmt)
            entity = result.scalars().first()
            
            if not entity:
                raise CustomException(
                    ErrorCode.DB_NO_RESULT,
                    detail=f"{self.model.__tablename__}|ulid|{ulid}",
                    source_function=f"{self.__class__.__name__}.update"
                )

            for key, value in data.items():
                setattr(entity, key, value)
            
            await self.session.flush()
            await self.session.refresh(entity)
            return entity
            
        except IntegrityError as e:
            await self.session.rollback()
            self._handle_integrity_error(e, "update", data)
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise CustomException(
                ErrorCode.DB_UPDATE_ERROR,
                detail=f"Database update error in {self.model.__tablename__}: {str(e)}",
                source_function=f"{self.__class__.__name__}.update",
                original_error=e
            )

    async def delete(self, ulid: str) -> bool:
        """엔티티를 소프트 삭제합니다."""
        try:
            stmt = select(self.model).filter_by(ulid=ulid, is_deleted=False)
            result = await self.session.execute(stmt)
            entity = result.scalars().first()
            
            if not entity:
                raise CustomException(
                    ErrorCode.DB_NO_RESULT,
                    detail=f"{self.model.__tablename__}|ulid|{ulid}",
                    source_function=f"{self.__class__.__name__}.delete"
                )

            entity.is_deleted = True
            await self.session.flush()
            return True
            
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise CustomException(
                ErrorCode.DB_DELETE_ERROR,
                detail=f"Database delete error in {self.model.__tablename__}: {str(e)}",
                source_function=f"{self.__class__.__name__}.delete",
                original_error=e
            )

    async def real_delete(self, ulid: str) -> bool:
        """엔티티를 실제로 삭제합니다."""
        try:
            stmt = select(self.model).filter_by(ulid=ulid)
            result = await self.session.execute(stmt)
            entity = result.scalars().first()
            
            if entity:
                await self.session.delete(entity)
                await self.session.flush()
                return True
            return False
            
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise CustomException(
                ErrorCode.DB_DELETE_ERROR,
                detail=f"Database real delete error in {self.model.__tablename__}: {str(e)}",
                source_function=f"{self.__class__.__name__}.real_delete",
                original_error=e
            ) 