"""기본 레포지토리 모듈."""
from typing import TypeVar, Generic, Dict, Any, List, Optional, Type, Union
from sqlalchemy.orm import DeclarativeBase, Load
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import select, or_, and_
from .database import DatabaseService
from .exceptions import CustomException, ErrorCode
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import Select
from fastapi import Request

ModelType = TypeVar("ModelType", bound=DeclarativeBase)

class BaseRepository(Generic[ModelType]):
   ##################
    # 1. 초기화 영역 #
    ##################
    def __init__(self, db_service: DatabaseService, model: Type[ModelType]):
        """
        Args:
            db_service (DatabaseService): 데이터베이스 서비스 인스턴스
            model (Type[ModelType]): 모델 클래스
        """
        self.db_service = db_service
        self.model = model

    #######################
    # 2. 쿼리 빌딩      #
    #######################
    def _build_base_query(self) -> Select:
        """기본 쿼리를 생성합니다.

        Returns:
            Select: 기본 쿼리
        """
        return select(self.model)

    #######################
    # 3. 전차리 영역    #
    #######################
    def _apply_exact_match(self, stmt: Select, field_name: str, value: Any) -> Select:
        """정확한 값 매칭 조건을 적용합니다.

        Args:
            stmt (Select): 쿼리문
            field_name (str): 필드명
            value (Any): 매칭할 값

        Returns:
            Select: 조건이 적용된 쿼리
        """
        return stmt.where(getattr(self.model, field_name) == value)

    def _apply_like_match(self, stmt: Select, field_name: str, value: str) -> Select:
        """LIKE 검색 조건을 적용합니다.

        Args:
            stmt (Select): 쿼리문
            field_name (str): 필드명
            value (str): 검색할 값

        Returns:
            Select: 조건이 적용된 쿼리
        """
        return stmt.where(getattr(self.model, field_name).ilike(f"%{value}%"))

    def _apply_relation_match(self, stmt: Select, relations: List[str], field_name: str, operator: str, value: Any) -> Select:
        """관계 테이블 검색 조건을 적용합니다."""
        current = self.model
        
        # 관계 체인 따라가기
        for i in range(len(relations)-1):
            current = getattr(current, relations[i]).property.mapper.class_
        
        # 마지막 모델과 필드
        final_model = getattr(current, relations[-1]).property.mapper.class_
        
        # 중첩된 EXISTS 절 생성
        current = self.model
        subq = select(1)
        
        # 첫 번째 관계
        next_model = getattr(current, relations[0]).property.mapper.class_
        subq = subq.where(getattr(next_model, 'ulid') == getattr(current, f"{relations[0]}_ulid"))
        
        # 중간 관계들
        for i in range(1, len(relations)):
            prev_model = next_model
            next_model = getattr(prev_model, relations[i]).property.mapper.class_
            subq = subq.where(getattr(next_model, 'ulid') == getattr(prev_model, f"{relations[i]}_ulid"))
        
        # 최종 검색 조건
        subq = subq.where(getattr(final_model, field_name).__getattribute__(operator)(value))
        
        return stmt.where(subq.exists())

    def _apply_ordering(self, stmt: Select, order_by: List[str]) -> Select:
        """정렬 조건을 적용합니다.

        Args:
            stmt (Select): 쿼리문
            order_by (List[str]): 정렬 기준 필드 목록 (예: ["name", "-created_at"])

        Returns:
            Select: 정렬이 적용된 쿼리
        """
        for field in order_by:
            if field.startswith("-"):
                field_name = field[1:]
                stmt = stmt.order_by(getattr(self.model, field_name).desc())
            else:
                stmt = stmt.order_by(getattr(self.model, field).asc())
        return stmt

    def _apply_pagination(self, stmt: Select, skip: int = 0, limit: int = 100) -> Select:
        """페이징을 적용합니다.

        Args:
            stmt (Select): 쿼리문
            skip (int): 건너뛸 레코드 수
            limit (int): 조회할 최대 레코드 수

        Returns:
            Select: 페이징이 적용된 쿼리
        """
        return stmt.offset(skip).limit(limit)

    def _apply_joins(self, stmt: Select, joins: List[str]) -> Select:
        """조인을 적용합니다.

        Args:
            stmt (Select): 쿼리문
            joins (List[str]): 조인할 관계명 목록

        Returns:
            Select: 조인이 적용된 쿼리
        """
        for join in joins:
            stmt = stmt.options(joinedload(getattr(self.model, join)))
        return stmt

    def _build_jsonb_condition(self, model: Any, field_path: str, value: str) -> Any:
        """JSONB 필드에 대한 검색 조건을 생성합니다.

        Args:
            model: 대상 모델
            field_path (str): JSONB 키 경로 (예: "address", "name.first")
            value (str): 검색할 값

        Returns:
            Any: SQLAlchemy 검색 조건
        """
        # JSONB 경로가 중첩된 경우 (예: "name.first")
        if "." in field_path:
            path_parts = field_path.split(".")
            jsonb_path = "{" + ",".join(path_parts) + "}"
            return model.extra_data[jsonb_path].astext.ilike(f"%{value}%")
        # 단일 키인 경우
        return model.extra_data[field_path].astext.ilike(f"%{value}%")

    def _apply_jsonb_match(self, stmt: Select, relations: List[str], json_key: str, value: str) -> Select:
        """JSONB 필드 검색 조건을 적용합니다.

        Args:
            stmt (Select): 쿼리문
            relations (List[str]): 관계 테이블 경로
            json_key (str): JSONB 키 경로
            value (str): 검색할 값

        Returns:
            Select: 조건이 적용된 쿼리
        """
        current = self.model
        
        # 단일 모델 검색
        if not relations:
            condition = self._build_jsonb_condition(current, json_key, value)
            return stmt.where(condition)
            
        # 관계 모델 검색
        for i in range(len(relations)-1):
            current = getattr(current, relations[i]).property.mapper.class_
            
        final_model = getattr(current, relations[-1]).property.mapper.class_
        
        # 관계 체인 구성
        if len(relations) == 1:
            condition = getattr(self.model, relations[0]).has(
                self._build_jsonb_condition(final_model, json_key, value)
            )
        else:
            condition = getattr(self.model, relations[0]).has(
                getattr(final_model, relations[-1]).has(
                    self._build_jsonb_condition(final_model, json_key, value)
                )
            )
            
        return stmt.where(condition)

    def _apply_search_params(self, stmt, search_params: Dict[str, Any]):
        """검색 파라미터를 적용합니다."""
        if not search_params:
            return stmt
            
        for key, value in search_params.items():
            if not value.get("value"):
                continue
                
            conditions = []
            for field in value.get("fields", []):
                parts = field.split('.')
                
                if len(parts) == 1:
                    # 직접 필드 검색
                    condition = self._apply_like_match(stmt, parts[0], value["value"]).whereclause
                elif 'extra_data' in parts:
                    # JSONB 필드 검색
                    extra_data_idx = parts.index('extra_data')
                    tables = parts[:extra_data_idx]
                    json_key = ".".join(parts[extra_data_idx + 1:])
                    condition = self._apply_jsonb_match(
                        stmt,
                        tables,
                        json_key,
                        value["value"]
                    ).whereclause
                else:
                    # 관계 테이블 검색
                    condition = self._apply_relation_match(
                        stmt,
                        parts[:-1],
                        parts[-1],
                        "ilike",
                        f"%{value['value']}%"
                    ).whereclause
                
                conditions.append(condition)
                    
            if conditions:
                stmt = stmt.where(or_(*conditions))
                    
        return stmt

    def _apply_filters(self, stmt, filters: Dict[str, Any]):
        """일반 필터를 적용합니다."""
        for key, value in filters.items():
            if value is None:
                continue
                
            if "." in key:
                # 관계 테이블 필터
                relation, field = key.split(".")
                stmt = self._apply_relation_match(stmt, relation, field, "__eq__", value)
            else:
                # 일반 필드 필터
                stmt = stmt.where(getattr(self.model, key) == value)
                
        return stmt

    #######################
    # 4. CRUD 작업     #
    #######################
    async def get(
        self,
        ulid: str
    ) -> Optional[Dict[str, Any]]:
        """ULID로 엔티티를 조회합니다.

        Args:
            ulid (str): 조회할 엔티티의 ULID

        Returns:
            Optional[Dict[str, Any]]: 조회된 엔티티, 없으면 None

        Raises:
            CustomException: 데이터베이스 작업 중 오류 발생 시
        """
        try:
            stmt = select(self.model).filter_by(ulid=ulid, is_deleted=False)
            result = await self.db_service.execute(stmt)
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
        except Exception as e:
            raise CustomException(
                ErrorCode.DB_QUERY_ERROR,
                detail=f"Unexpected repository error in {self.model.__tablename__}: {str(e)}",
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

            result = await self.db_service.db.execute(stmt)
            return result.scalars().unique().all()

        except SQLAlchemyError as e:
            raise CustomException(
                ErrorCode.DB_QUERY_ERROR,
                detail=f"Unexpected repository list error in {self.model.__tablename__}: {str(e)}",
                source_function=f"{self.__class__.__name__}.list",
                original_error=e,
            )

    async def create(self, data: Dict[str, Any]) -> ModelType:
        """새로운 엔티티를 생성합니다.

        Args:
            data (Dict[str, Any]): 생성할 엔티티 데이터

        Returns:
            ModelType: 생성된 엔티티

        Raises:
            CustomException: 데이터베이스 작업 중 오류 발생 시
        """
        try:
            return await self.db_service.create_entity(self.model, data)
        except CustomException as e:
            e.detail = f"Repository create error for {self.model.__tablename__}: {e.detail}"
            e.source_function = f"{self.__class__.__name__}.create -> {e.source_function}"
            raise e
        except IntegrityError as e:
            self._handle_integrity_error(e, "create", data)
        except SQLAlchemyError as e:
            raise CustomException(
                ErrorCode.DB_CREATE_ERROR,
                detail=f"Database create error in {self.model.__tablename__}: {str(e)}",
                source_function=f"{self.__class__.__name__}.create",
                original_error=e
            )
        except Exception as e:
            raise CustomException(
                ErrorCode.DB_CREATE_ERROR,
                detail=f"Unexpected repository create error in {self.model.__tablename__}: {str(e)}",
                source_function=f"{self.__class__.__name__}.create",
                original_error=e
            )

    async def update(self, ulid: str, data: Dict[str, Any]) -> Optional[ModelType]:
        """기존 엔티티를 수정합니다.

        Args:
            ulid (str): 수정할 엔티티의 ULID
            data (Dict[str, Any]): 수정할 데이터

        Returns:
            Optional[ModelType]: 수정된 엔티티, 없으면 None

        Raises:
            CustomException: 데이터베이스 작업 중 오류 발생 시
        """
        try:
            entity = await self.db_service.update_entity(
                self.model,
                {"ulid": ulid, "is_deleted": False},
                data
            )
            if not entity:
                raise CustomException(
                    ErrorCode.DB_NO_RESULT,
                    detail=f"{self.model.__tablename__}|ulid|{ulid}",
                    source_function=f"{self.__class__.__name__}.update"
                )
            return entity
        except CustomException as e:
            e.detail = f"Repository update error for {self.model.__tablename__}: {e.detail}"
            e.source_function = f"{self.__class__.__name__}.update -> {e.source_function}"
            raise e
        except IntegrityError as e:
            self._handle_integrity_error(e, "update", data)
        except SQLAlchemyError as e:
            raise CustomException(
                ErrorCode.DB_UPDATE_ERROR,
                detail=f"Database update error in {self.model.__tablename__}: {str(e)}",
                source_function=f"{self.__class__.__name__}.update",
                original_error=e
            )
        except Exception as e:
            raise CustomException(
                ErrorCode.DB_UPDATE_ERROR,
                detail=f"Unexpected repository update error in {self.model.__tablename__}: {str(e)}",
                source_function=f"{self.__class__.__name__}.update",
                original_error=e
            )

    async def delete(self, ulid: str) -> bool:
        """엔티티를 소프트 삭제합니다 (is_deleted = True).

        Args:
            ulid (str): 삭제할 엔티티의 ULID

        Returns:
            bool: 삭제 성공 여부

        Raises:
            CustomException: 데이터베이스 작업 중 오류 발생 시
        """
        try:
            entity = await self.db_service.soft_delete_entity(self.model, ulid)
            if not entity:
                raise CustomException(
                    ErrorCode.DB_NO_RESULT,
                    detail=f"{self.model.__tablename__}|ulid|{ulid}",
                    source_function=f"{self.__class__.__name__}.delete"
                )
            return True
        except CustomException as e:
            e.detail = f"Repository delete error for {self.model.__tablename__}: {e.detail}"
            e.source_function = f"{self.__class__.__name__}.delete -> {e.source_function}"
            raise e
        except IntegrityError as e:
            self._handle_integrity_error(e, "delete")
        except SQLAlchemyError as e:
            raise CustomException(
                ErrorCode.DB_DELETE_ERROR,
                detail=f"Database delete error in {self.model.__tablename__}: {str(e)}",
                source_function=f"{self.__class__.__name__}.delete",
                original_error=e
            )
        except Exception as e:
            raise CustomException(
                ErrorCode.DB_DELETE_ERROR,
                detail=f"Unexpected repository delete error in {self.model.__tablename__}: {str(e)}",
                source_function=f"{self.__class__.__name__}.delete",
                original_error=e
            )

    async def real_row_delete(self, ulid: str) -> bool:
        """엔티티를 실제로 삭제합니다.

        Args:
            ulid (str): 삭제할 엔티티의 ULID

        Returns:
            bool: 삭제 성공 여부

        Raises:
            CustomException: 데이터베이스 작업 중 오류 발생 시
        """
        try:
            entity = await self.db_service.retrieve_entity(
                self.model,
                {"ulid": ulid}
            )
            if entity:
                await self.db_service.delete_entity(entity)
                return True
            return False
        except CustomException as e:
            e.detail = f"Repository real delete error for {self.model.__tablename__}: {e.detail}"
            e.source_function = f"{self.__class__.__name__}.real_row_delete -> {e.source_function}"
            raise e
        except SQLAlchemyError as e:
            raise CustomException(
                ErrorCode.DB_DELETE_ERROR,
                detail=f"Database real delete error in {self.model.__tablename__}: {str(e)}",
                source_function=f"{self.__class__.__name__}.real_row_delete",
                original_error=e
            )
        except Exception as e:
            raise CustomException(
                ErrorCode.DB_DELETE_ERROR,
                detail=f"Unexpected repository real delete error in {self.model.__tablename__}: {str(e)}",
                source_function=f"{self.__class__.__name__}.real_row_delete",
                original_error=e
            ) 