"""데이터베이스 유틸리티 모듈."""
from typing import Any, Dict, Optional, Type, List, Union
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from .exceptions import ErrorCode, CustomException
from .base_model import Base

class DatabaseService:
    def __init__(self, session: AsyncSession):
        """DatabaseService 초기화
        
        Args:
            session (AsyncSession): 외부에서 주입받은 데이터베이스 세션
        """
        self._session = session
    
    @property
    def session(self) -> AsyncSession:
        """현재 세션을 반환합니다."""
        if self._session is None:
            raise CustomException(
                ErrorCode.DB_CONNECTION_ERROR,
                detail="session",
                source_function="DatabaseService.session"
            )
        return self._session

    async def create_entity(
        self,
        model: Type[Base],
        entity_data: Dict[str, Any]
    ) -> Any:
        """엔티티를 생성합니다.
        
        Args:
            model: 모델 클래스
            entity_data: 생성할 엔티티 데이터
            
        Returns:
            생성된 엔티티
            
        Raises:
            CustomException: 엔티티 생성 실패 시
        """
        try:
            entity = model(**entity_data)
            self.session.add(entity)
            await self.session.flush()
            await self.session.refresh(entity)
            return entity
        except IntegrityError as e:
            await self.session.rollback()
            raise CustomException(
                ErrorCode.DB_INTEGRITY_ERROR,
                detail=str(e),
                source_function="DatabaseService.create_entity",
                original_error=e
            )
        except Exception as e:
            await self.session.rollback()
            raise CustomException(
                ErrorCode.DB_CREATE_ERROR,
                detail=str(e),
                source_function="DatabaseService.create_entity",
                original_error=e
            )

    async def get_entity(
        self,
        model: Type[Base],
        filters: Dict[str, Any]
    ) -> Optional[Any]:
        """필터 조건으로 엔티티를 조회합니다.
        
        Args:
            model: 모델 클래스
            filters: 필터 조건
            
        Returns:
            조회된 엔티티 또는 None
            
        Raises:
            CustomException: 조회 실패 시
        """
        try:
            stmt = select(model).filter_by(**filters)
            result = await self.session.execute(stmt)
            return result.scalars().first()
        except Exception as e:
            raise CustomException(
                ErrorCode.DB_QUERY_ERROR,
                detail=str(e),
                source_function="DatabaseService.get_entity",
                original_error=e
            )

    async def list_entities(
        self,
        model: Type[Base],
        filters: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Any]:
        """엔티티 목록을 조회합니다.
        
        Args:
            model: 모델 클래스
            filters: 필터 조건
            skip: 건너뛸 레코드 수
            limit: 조회할 최대 레코드 수
            
        Returns:
            엔티티 목록
            
        Raises:
            CustomException: 조회 실패 시
        """
        try:
            stmt = select(model)
            if filters:
                stmt = stmt.filter_by(**filters)
            stmt = stmt.offset(skip).limit(limit)
            result = await self.session.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            raise CustomException(
                ErrorCode.DB_QUERY_ERROR,
                detail=str(e),
                source_function="DatabaseService.list_entities",
                original_error=e
            )

    async def update_entity(
        self,
        entity: Base,
        update_data: Dict[str, Any]
    ) -> Any:
        """엔티티를 수정합니다.
        
        Args:
            entity: 수정할 엔티티
            update_data: 수정할 데이터
            
        Returns:
            수정된 엔티티
            
        Raises:
            CustomException: 수정 실패 시
        """
        try:
            for key, value in update_data.items():
                setattr(entity, key, value)
            await self.session.flush()
            await self.session.refresh(entity)
            return entity
        except IntegrityError as e:
            await self.session.rollback()
            raise CustomException(
                ErrorCode.DB_INTEGRITY_ERROR,
                detail=str(e),
                source_function="DatabaseService.update_entity",
                original_error=e
            )
        except Exception as e:
            await self.session.rollback()
            raise CustomException(
                ErrorCode.DB_UPDATE_ERROR,
                detail=str(e),
                source_function="DatabaseService.update_entity",
                original_error=e
            )

    async def delete_entity(
        self,
        entity: Base,
        soft_delete: bool = True
    ) -> bool:
        """엔티티를 삭제합니다.
        
        Args:
            entity: 삭제할 엔티티
            soft_delete: 소프트 삭제 여부
            
        Returns:
            삭제 성공 여부
            
        Raises:
            CustomException: 삭제 실패 시
        """
        try:
            if soft_delete:
                entity.is_deleted = True
                await self.session.flush()
            else:
                await self.session.delete(entity)
                await self.session.flush()
            return True
        except Exception as e:
            await self.session.rollback()
            raise CustomException(
                ErrorCode.DB_DELETE_ERROR,
                detail=str(e),
                source_function="DatabaseService.delete_entity",
                original_error=e
            )