"""기본 서비스 모듈."""
from datetime import datetime
from typing import TypeVar, Generic, Dict, Any, List, Optional, Type, Union
from sqlalchemy.orm import DeclarativeBase, Load
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from .database import DatabaseService
from .exceptions import CustomException, ErrorCode
from .base_repository import BaseRepository
from .security import hash_password
from fastapi import Request
from ulid import ULID

ModelType = TypeVar("ModelType", bound=DeclarativeBase)

class BaseService(Generic[ModelType]):

    ##################
    # 1. 초기화 영역 #
    ##################
    def __init__(
        self,
        repository: BaseRepository[ModelType],
        additional_models: Dict[str, Type[DeclarativeBase]] = None
    ):
        """
        Args:
            repository (BaseRepository[ModelType]): 레포지토리 인스턴스
            additional_models (Dict[str, Type[DeclarativeBase]], optional): 추가 모델 매핑. Defaults to None.
        """
        self.repository = repository
        self.model = repository.model
        self.additional_models = additional_models or {}
        self.db_service = repository.db_service
        self.searchable_fields = {
            "name": {"type": "text", "description": "이름"},
            "organization_ulid": {"type": "exact", "description": "조직 ID"}
        }

    #########################
    # 2. 이벤트 처리 메서드 #
    #########################
    async def pre_save(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """저장 전 처리를 수행합니다.

        Args:
            data (Dict[str, Any]): 저장할 데이터

        Returns:
            Dict[str, Any]: 처리된 데이터
        """
        return data

    async def post_save(self, entity: ModelType) -> None:
        """저장 후 처리를 수행합니다.

        Args:
            entity (ModelType): 저장된 엔티티
        """
        pass

    async def pre_delete(self, ulid: str) -> None:
        """삭제 전 처리를 수행합니다.

        Args:
            ulid (str): 삭제할 엔티티의 ULID
        """
        pass

    async def post_delete(self, ulid: str) -> None:
        """삭제 후 처리를 수행합니다.

        Args:
            ulid (str): 삭제된 엔티티의 ULID
        """
        pass

    ######################
    # 3. 캐시 관리 메서드 #
    ######################
    async def get_from_cache(self, key: str) -> Optional[Any]:
        """캐시에서 데이터를 조회합니다.

        Args:
            key (str): 캐시 키

        Returns:
            Optional[Any]: 캐시된 데이터 또는 None
        """
        return None

    async def set_to_cache(self, key: str, value: Any, ttl: int = 3600) -> None:
        """데이터를 캐시에 저장합니다.

        Args:
            key (str): 캐시 키
            value (Any): 저장할 값
            ttl (int, optional): 캐시 유효 시간(초). Defaults to 3600.
        """
        pass

    async def invalidate_cache(self, key: str) -> None:
        """캐시를 무효화합니다.

        Args:
            key (str): 캐시 키
        """
        pass
    
    ##########################
    # 4. 비즈니스 검증 메서드 #
    ##########################
    def _validate_business_rules(self, data: Dict[str, Any]) -> None:
        """비즈니스 규칙을 검증합니다.

        Args:
            data (Dict[str, Any]): 검증할 데이터

        Raises:
            CustomException: 비즈니스 규칙 위반 시
        """
        pass

    def _validate_permissions(self, request: Request, action: str) -> None:
        """권한을 검증합니다.

        Args:
            request (Request): FastAPI 요청 객체
            action (str): 수행할 작업

        Raises:
            CustomException: 권한이 없는 경우
        """
        pass

    ########################
    # 5. 응답 처리 메서드   #
    ########################
    def _handle_response_model(self, entity: ModelType, response_model: Any) -> Dict[str, Any]:
        """응답 모델에 맞게 데이터를 처리합니다.

        Args:
            entity (ModelType): 처리할 엔티티
            response_model (Any): 응답 모델

        Returns:
            Dict[str, Any]: 처리된 데이터
        """
        if not response_model:
            return self._process_response(entity)
            
        result = self._process_response(entity)
        
        # response_model에 없는 필드 제거
        keys_to_remove = [key for key in result if key not in response_model.model_fields]
        for key in keys_to_remove:
            result.pop(key)
            
        # 모델 검증
        return response_model(**result).model_dump()

    def _handle_exclude_fields(self, data: Dict[str, Any], exclude_fields: List[str]) -> Dict[str, Any]:
        """제외할 필드를 처리합니다.

        Args:
            data (Dict[str, Any]): 처리할 데이터
            exclude_fields (List[str]): 제외할 필드 목록

        Returns:
            Dict[str, Any]: 처리된 데이터
        """
        if not exclude_fields:
            return data
            
        return {k: v for k, v in data.items() if k not in exclude_fields}

    def _validate_ulid(self, ulid: str) -> bool:
        """ULID 형식을 검증합니다.

        Args:
            ulid (str): 검증할 ULID

        Returns:
            bool: 유효한 ULID 여부
        """
        try:
            ULID.from_str(ulid)
            return True
        except (ValueError, AttributeError):
            return False

    def _process_columns(self, entity: ModelType, exclude_extra_data: bool = True) -> Dict[str, Any]:
        """엔티티의 컬럼들을 처리합니다.

        Args:
            entity (ModelType): 처리할 엔티티
            exclude_extra_data (bool, optional): extra_data 컬럼 제외 여부. Defaults to True.

        Returns:
            Dict[str, Any]: 처리된 컬럼 데이터
        """
        result = {}
        for column in entity.__table__.columns:
            if exclude_extra_data and column.name == 'extra_data':
                continue
                
            # 필드 값 처리
            if hasattr(entity, column.name):
                value = getattr(entity, column.name)
                if isinstance(value, datetime):
                    value = value.isoformat()
                result[column.name] = value
            elif hasattr(entity, 'extra_data') and isinstance(entity.extra_data, dict):
                result[column.name] = entity.extra_data.get(column.name)
            else:
                result[column.name] = None
        
        # extra_data의 내용을 최상위 레벨로 업데이트
        if hasattr(entity, 'extra_data') and isinstance(entity.extra_data, dict):
            result.update(entity.extra_data or {})
                
        return result

    def _process_response(self, entity: ModelType, response_model: Any = None) -> Dict[str, Any]:
        """응답 데이터를 처리합니다.
        extra_data의 내용을 최상위 레벨로 변환하고, 라우터에서 선언한 응답 스키마에 맞게 데이터를 변환합니다.

        Args:
            entity (ModelType): 처리할 엔티티
            response_model (Any, optional): 응답 스키마. Defaults to None.

        Returns:
            Dict[str, Any]: 처리된 엔티티 데이터
        """
        if not entity:
            return None

        # 모든 필드 처리
        result = self._process_columns(entity)
        
        # Relationship 처리 (이미 로드된 관계만 처리)
        for relationship in entity.__mapper__.relationships:
            if not relationship.key in entity.__dict__:
                continue
                
            try:
                value = getattr(entity, relationship.key)
                # response_model이 있는 경우 해당 필드의 annotation type을 가져옴
                nested_response_model = None
                if response_model and relationship.key in response_model.model_fields:
                    field_info = response_model.model_fields[relationship.key]
                    nested_response_model = field_info.annotation
                
                if value is not None:
                    if isinstance(value, list):
                        result[relationship.key] = [
                            self._process_response(item, nested_response_model)
                            for item in value
                        ]
                    else:
                        result[relationship.key] = self._process_response(value, nested_response_model)
                else:
                    result[relationship.key] = None
            except Exception:
                result[relationship.key] = None

        # response_model이 있는 경우 필터링
        if response_model:
            # 현재 키 목록을 저장
            current_keys = list(result.keys())
            # response_model에 없는 키 제거
            for key in current_keys:
                if key not in response_model.model_fields:
                    result.pop(key)
            # 모델 검증 및 업데이트
            result.update(response_model(**result).model_dump())
                
        return result

    def _process_basic_fields(self, entity: ModelType) -> Dict[str, Any]:
        """엔티티의 기본 필드만 처리합니다.

        Args:
            entity (ModelType): 처리할 엔티티

        Returns:
            Dict[str, Any]: 기본 필드만 포함된 딕셔너리
        """
        if not entity:
            return None
            
        return self._process_columns(entity)

    async def _create_for_model(self, model_name: str, data: Dict[str, Any], exclude_fields: List[str] = None) -> DeclarativeBase:
        """지정된 모델에 대해 새로운 엔티티를 생성합니다.

        Args:
            model_name (str): 생성할 모델 이름
            data (Dict[str, Any]): 생성할 엔티티 데이터
            exclude_fields (List[str], optional): 제외할 필드 목록. Defaults to None.

        Returns:
            DeclarativeBase: 생성된 엔티티

        Raises:
            CustomException: 데이터베이스 작업 중 오류 발생 시
        """
        if model_name not in self.additional_models:
            raise CustomException(
                ErrorCode.INVALID_REQUEST,
                detail=f"Model {model_name} not registered",
                source_function=f"{self.__class__.__name__}._create_for_model"
            )

        try:
            # 제외할 필드 처리
            if exclude_fields:
                data = {k: v for k, v in data.items() if k not in exclude_fields}

            return await self.db_service.create_entity(self.additional_models[model_name], data)
        except CustomException as e:
            raise e
        except Exception as e:
            raise CustomException(
                ErrorCode.DB_CREATE_ERROR,
                detail=str(e),
                source_function=f"{self.__class__.__name__}._create_for_model",
                original_error=e
            )

    def _process_password(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """비밀번호 필드가 있는 경우 해시화합니다.

        Args:
            data (Dict[str, Any]): 처리할 데이터

        Returns:
            Dict[str, Any]: 처리된 데이터
        """
        if "password" in data:
            data["password"] = hash_password(data["password"])
        return data

    #######################
    # 6. CRUD 작업 메서드 #
    #######################
    async def create(self, data: Dict[str, Any], exclude_fields: List[str] = None, model_name: str = None) -> Union[ModelType, DeclarativeBase]:
        """새로운 엔티티를 생성합니다.

        Args:
            data (Dict[str, Any]): 생성할 엔티티 데이터
            exclude_fields (List[str], optional): 제외할 필드 목록. Defaults to None.
            model_name (str, optional): 생성할 모델 이름. Defaults to None.

        Returns:
            Union[ModelType, DeclarativeBase]: 생성된 엔티티

        Raises:
            CustomException: 데이터베이스 작업 중 오류 발생 시
        """
        try:
            # 비밀번호 해시화
            data = self._process_password(data)

            # 제외할 필드 처리
            if exclude_fields:
                data = {k: v for k, v in data.items() if k not in exclude_fields}

            if model_name:
                return await self._create_for_model(model_name, data)

            return await self.repository.create(data)
        except CustomException as e:
            raise e
        except Exception as e:
            raise CustomException(
                ErrorCode.DB_CREATE_ERROR,
                detail=str(e),
                source_function=f"{self.__class__.__name__}.create",
                original_error=e
            )

    async def update(
        self,
        ulid: str,
        data: Dict[str, Any],
        exclude_fields: List[str] = None,
        model_name: str = None
    ) -> Optional[ModelType]:
        """기존 엔티티를 수정합니다.

        Args:
            ulid (str): 수정할 엔티티의 ULID
            data (Dict[str, Any]): 수정할 데이터
            exclude_fields (List[str], optional): 제외할 필드 목록. Defaults to None.
            model_name (str, optional): 수정할 모델 이름. Defaults to None.

        Returns:
            Optional[ModelType]: 수정된 엔티티, 없으면 None

        Raises:
            CustomException: 데이터베이스 작업 중 오류 발생 시
        """
        try:
            # 비밀번호 해시화
            data = self._process_password(data)

            # 제외할 필드 처리
            if exclude_fields:
                data = {k: v for k, v in data.items() if k not in exclude_fields}

            async with self.db_service.transaction():
                if model_name:
                    if model_name not in self.additional_models:
                        raise CustomException(
                            ErrorCode.INVALID_REQUEST,
                            detail=f"Model {model_name} not registered",
                            source_function=f"{self.__class__.__name__}.update"
                        )
                    entity = await self.db_service.update_entity(
                        self.additional_models[model_name],
                        {"ulid": ulid},
                        data
                    )
                    if not entity:
                        raise CustomException(
                            ErrorCode.NOT_FOUND,
                            detail=f"{self.additional_models[model_name].__tablename__}|ulid|{ulid}",
                            source_function=f"{self.__class__.__name__}.update"
                        )
                    return entity

                entity = await self.repository.update(ulid, data)
                if not entity:
                    raise CustomException(
                        ErrorCode.NOT_FOUND,
                        detail=f"{self.model.__tablename__}|ulid|{ulid}",
                        source_function=f"{self.__class__.__name__}.update"
                    )
                return entity
        except CustomException as e:
            raise e
        except Exception as e:
            raise CustomException(
                ErrorCode.DB_UPDATE_ERROR,
                detail=str(e),
                source_function=f"{self.__class__.__name__}.update",
                original_error=e
            )

    async def delete(self, ulid: str, model_name: str = None) -> bool:
        """엔티티를 소프트 삭제합니다 (is_deleted = True).

        Args:
            ulid (str): 삭제할 엔티티의 ULID
            model_name (str, optional): 삭제할 모델 이름. Defaults to None.

        Returns:
            bool: 삭제 성공 여부

        Raises:
            CustomException: 데이터베이스 작업 중 오류 발생 시
        """
        try:
            if model_name:
                if model_name not in self.additional_models:
                    raise CustomException(
                        ErrorCode.INVALID_REQUEST,
                        detail=f"Model {model_name} not registered",
                        source_function=f"{self.__class__.__name__}.delete"
                    )
                entity = await self.db_service.soft_delete_entity(self.additional_models[model_name], ulid)
                if not entity:
                    raise CustomException(
                        ErrorCode.NOT_FOUND,
                        detail=f"{self.additional_models[model_name].__tablename__}|ulid|{ulid}",
                        source_function=f"{self.__class__.__name__}.delete"
                    )
                return True

            entity = await self.repository.delete(ulid)
            if not entity:
                raise CustomException(
                    ErrorCode.NOT_FOUND,
                    detail=f"{self.model.__tablename__}|ulid|{ulid}",
                    source_function=f"{self.__class__.__name__}.delete"
                )
            return True
        except CustomException as e:
            raise e
        except Exception as e:
            raise CustomException(
                ErrorCode.DB_DELETE_ERROR,
                detail=str(e),
                source_function=f"{self.__class__.__name__}.delete",
                original_error=e
            )

    async def real_row_delete(self, ulid: str, model_name: str = None) -> bool:
        """엔티티를 실제로 삭제합니다.

        Args:
            ulid (str): 삭제할 엔티티의 ULID
            model_name (str, optional): 삭제할 모델 이름. Defaults to None.

        Returns:
            bool: 삭제 성공 여부

        Raises:
            CustomException: 데이터베이스 작업 중 오류 발생 시
        """
        try:
            if model_name:
                if model_name not in self.additional_models:
                    raise CustomException(
                        ErrorCode.INVALID_REQUEST,
                        detail=f"Model {model_name} not registered",
                        source_function=f"{self.__class__.__name__}.real_row_delete"
                    )
                entity = await self.db_service.retrieve_entity(
                    self.additional_models[model_name],
                    {"ulid": ulid}
                )
                if entity:
                    await self.db_service.delete_entity(entity)
                    return True
                return False

            return await self.repository.real_row_delete(ulid)
        except CustomException as e:
            raise e
        except Exception as e:
            raise CustomException(
                ErrorCode.DB_DELETE_ERROR,
                detail=str(e),
                source_function=f"{self.__class__.__name__}.real_row_delete",
                original_error=e
            )

    #########################
    # 7. 조회 및 검색 메서드 #
    #########################
    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Dict[str, Any] | None = None,
        search_params: Dict[str, Any] | None = None,
        model_name: str | None = None,
        request: Request | None = None,
        response_model: Any = None
    ) -> List[Dict[str, Any]]:
        """엔티티 목록을 조회합니다.

        Args:
            skip (int, optional): 건너뛸 레코드 수. Defaults to 0.
            limit (int, optional): 조회할 최대 레코드 수. Defaults to 100.
            filters (Dict[str, Any] | None, optional): 필터링 조건. Defaults to None.
            search_params (Dict[str, Any] | None, optional): 검색 파라미터. Defaults to None.
            model_name (str | None, optional): 조회할 모델 이름. Defaults to None.
            request (Request | None, optional): 요청 객체. Defaults to None.
            response_model (Any, optional): 응답 스키마. Defaults to None.

        Returns:
            List[Dict[str, Any]]: 엔티티 목록
        """
        try:
            if model_name:
                if model_name not in self.additional_models:
                    raise CustomException(
                        ErrorCode.INVALID_REQUEST,
                        detail=f"Model {model_name} not registered",
                        source_function=f"{self.__class__.__name__}.list"
                    )
                entities = await self.db_service.list_entities(
                    self.additional_models[model_name],
                    skip=skip,
                    limit=limit,
                    filters=filters
                )
                return [self._process_response(entity, response_model) for entity in entities]

            entities = await self.repository.list(
                skip=skip,
                limit=limit,
                filters=filters,
                search_params=search_params
            )
            return [self._process_response(entity, response_model) for entity in entities]
            
        except CustomException as e:
            e.detail = f"Service list error for {self.repository.model.__tablename__}: {e.detail}"
            e.source_function = f"{self.__class__.__name__}.list -> {e.source_function}"
            raise e
        except Exception as e:
            raise CustomException(
                ErrorCode.INTERNAL_ERROR,
                detail=str(e),
                source_function=f"{self.__class__.__name__}.list",
                original_error=e
            )

    async def get(
        self,
        ulid: str,
        model_name: str | None = None,
        request: Request | None = None,
        response_model: Any = None
    ) -> Optional[Dict[str, Any]]:
        """특정 엔티티를 조회합니다.

        Args:
            ulid (str): 조회할 엔티티의 ULID
            model_name (str | None, optional): 조회할 모델 이름. Defaults to None.
            request (Request | None, optional): 요청 객체. Defaults to None.
            response_model (Any, optional): 응답 스키마. Defaults to None.

        Returns:
            Optional[Dict[str, Any]]: 조회된 엔티티, 없으면 None
            
        Raises:
            CustomException: 데이터베이스 작업 중 오류 발생 시
        """
        try:
            # ULID 검증
            if not self._validate_ulid(ulid):
                raise CustomException(
                    ErrorCode.VALIDATION_ERROR,
                    detail=f"Invalid ULID format: {ulid}",
                    source_function=f"{self.__class__.__name__}.get"
                )

            if model_name:
                if model_name not in self.additional_models:
                    raise CustomException(
                        ErrorCode.INVALID_REQUEST,
                        detail=f"Model {model_name} not registered",
                        source_function=f"{self.__class__.__name__}.get"
                    )
                entity = await self.db_service.retrieve_entity(
                    self.additional_models[model_name],
                    {"ulid": ulid, "is_deleted": False}
                )
                if not entity:
                    raise CustomException(
                        ErrorCode.NOT_FOUND,
                        detail=f"{self.additional_models[model_name].__tablename__}|ulid|{ulid}",
                        source_function=f"{self.__class__.__name__}.get"
                    )
                return self._process_response(entity, response_model)

            entity = await self.repository.get(ulid)
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
                ErrorCode.INTERNAL_ERROR,
                detail=str(e),
                source_function=f"{self.__class__.__name__}.get",
                original_error=e
            ) 