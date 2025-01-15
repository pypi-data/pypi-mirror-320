"""기본 서비스 모듈."""
from datetime import datetime
from typing import TypeVar, Generic, Dict, Any, List, Optional, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from fastapi import Request

from .database import DatabaseService
from .exceptions import CustomException, ErrorCode
from .base_repository import BaseRepository

ModelType = TypeVar("ModelType", bound=DeclarativeBase)

class BaseService(Generic[ModelType]):
    def __init__(
        self,
        db: DatabaseService,
        repository: Optional[BaseRepository] = None,
        request: Optional[Request] = None
    ):
        """BaseService 초기화
        
        Args:
            db: 데이터베이스 서비스
            repository: 레포지토리 인스턴스 (선택)
            request: FastAPI 요청 객체 (선택)
        """
        self.db = db
        self.repository = repository
        self.request = request
        self.model = repository.model if repository else None

    def _process_response(self, entity: ModelType, response_model: Any = None) -> Dict[str, Any]:
        """응답 데이터를 처리합니다.
        
        Args:
            entity: 처리할 엔티티
            response_model: 응답 모델 클래스
            
        Returns:
            처리된 데이터
        """
        if not entity:
            return None
            
        # 기본 데이터 변환
        result = {}
        
        # 테이블 컬럼 처리
        for column in entity.__table__.columns:
            value = getattr(entity, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        
        # Relationship 처리 (이미 로드된 관계만)
        for relationship in entity.__mapper__.relationships:
            if relationship.key not in entity.__dict__:
                continue
                
            try:
                value = getattr(entity, relationship.key)
                if value is not None:
                    if isinstance(value, list):
                        result[relationship.key] = [
                            self._process_response(item)
                            for item in value
                        ]
                    else:
                        result[relationship.key] = self._process_response(value)
                else:
                    result[relationship.key] = None
            except Exception:
                result[relationship.key] = None
        
        # response_model이 있는 경우 필터링
        if response_model:
            # response_model에 없는 필드 제거
            keys_to_remove = [key for key in result if key not in response_model.model_fields]
            for key in keys_to_remove:
                result.pop(key)
            # 모델 검증
            return response_model(**result).model_dump()
            
        return result

    async def create(
        self,
        data: Dict[str, Any],
        response_model: Any = None
    ) -> Dict[str, Any]:
        """엔티티를 생성합니다.
        
        Args:
            data: 생성할 데이터
            response_model: 응답 모델 클래스
            
        Returns:
            생성된 엔티티
            
        Raises:
            CustomException: 생성 실패 시
        """
        try:
            entity = await self.db.create_entity(self.model, data)
            return self._process_response(entity, response_model)
        except CustomException as e:
            raise e
        except Exception as e:
            raise CustomException(
                ErrorCode.DB_CREATE_ERROR,
                detail=str(e),
                source_function=f"{self.__class__.__name__}.create",
                original_error=e
            )

    async def get(
        self,
        ulid: str,
        response_model: Any = None
    ) -> Dict[str, Any]:
        """엔티티를 조회합니다.
        
        Args:
            ulid: 조회할 엔티티의 ULID
            response_model: 응답 모델 클래스
            
        Returns:
            조회된 엔티티
            
        Raises:
            CustomException: 조회 실패 시
        """
        try:
            entity = await self.db.get_entity(self.model, {"ulid": ulid, "is_deleted": False})
            if not entity:
                raise CustomException(
                    ErrorCode.NOT_FOUND,
                    detail=f"{self.model.__tablename__}|ulid|{ulid}",
                    source_function=f"{self.__class__.__name__}.get"
                )
            return self._process_response(entity, response_model)
        except CustomException as e:
            raise e
        except Exception as e:
            raise CustomException(
                ErrorCode.DB_QUERY_ERROR,
                detail=str(e),
                source_function=f"{self.__class__.__name__}.get",
                original_error=e
            )

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        response_model: Any = None
    ) -> List[Dict[str, Any]]:
        """엔티티 목록을 조회합니다.
        
        Args:
            skip: 건너뛸 레코드 수
            limit: 조회할 최대 레코드 수
            filters: 필터 조건
            response_model: 응답 모델 클래스
            
        Returns:
            엔티티 목록
            
        Raises:
            CustomException: 조회 실패 시
        """
        try:
            entities = await self.db.list_entities(
                self.model,
                filters=filters,
                skip=skip,
                limit=limit
            )
            return [self._process_response(entity, response_model) for entity in entities]
        except CustomException as e:
            raise e
        except Exception as e:
            raise CustomException(
                ErrorCode.DB_QUERY_ERROR,
                detail=str(e),
                source_function=f"{self.__class__.__name__}.list",
                original_error=e
            )

    async def update(
        self,
        ulid: str,
        data: Dict[str, Any],
        response_model: Any = None
    ) -> Dict[str, Any]:
        """엔티티를 수정합니다.
        
        Args:
            ulid: 수정할 엔티티의 ULID
            data: 수정할 데이터
            response_model: 응답 모델 클래스
            
        Returns:
            수정된 엔티티
            
        Raises:
            CustomException: 수정 실패 시
        """
        try:
            entity = await self.db.get_entity(self.model, {"ulid": ulid, "is_deleted": False})
            if not entity:
                raise CustomException(
                    ErrorCode.NOT_FOUND,
                    detail=f"{self.model.__tablename__}|ulid|{ulid}",
                    source_function=f"{self.__class__.__name__}.update"
                )
            updated = await self.db.update_entity(entity, data)
            return self._process_response(updated, response_model)
        except CustomException as e:
            raise e
        except Exception as e:
            raise CustomException(
                ErrorCode.DB_UPDATE_ERROR,
                detail=str(e),
                source_function=f"{self.__class__.__name__}.update",
                original_error=e
            )

    async def delete(self, ulid: str) -> bool:
        """엔티티를 삭제합니다.
        
        Args:
            ulid: 삭제할 엔티티의 ULID
            
        Returns:
            삭제 성공 여부
            
        Raises:
            CustomException: 삭제 실패 시
        """
        try:
            entity = await self.db.get_entity(self.model, {"ulid": ulid, "is_deleted": False})
            if not entity:
                raise CustomException(
                    ErrorCode.NOT_FOUND,
                    detail=f"{self.model.__tablename__}|ulid|{ulid}",
                    source_function=f"{self.__class__.__name__}.delete"
                )
            return await self.db.delete_entity(entity)
        except CustomException as e:
            raise e
        except Exception as e:
            raise CustomException(
                ErrorCode.DB_DELETE_ERROR,
                detail=str(e),
                source_function=f"{self.__class__.__name__}.delete",
                original_error=e
            ) 