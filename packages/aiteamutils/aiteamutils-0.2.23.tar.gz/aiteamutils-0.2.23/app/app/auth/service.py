async def login(self, username: str, password: str, request: Request = None) -> Dict[str, str]:
        """사용자 로그인을 처리합니다.
        
        Args:
            username (str): 사용자명
            password (str): 비밀번호
            request (Request, optional): FastAPI 요청 객체
            
        Returns:
            Dict[str, str]: 액세스 토큰과 리프레시 토큰
            
        Raises:
            CustomException: 인증 실패 시 예외
        """
        # 사용자 조회
        user = await self.repository.get_user(username, by="username")
        if not user:
            raise CustomException(
                ErrorCode.INVALID_CREDENTIALS,
                source_function="AuthService.login"
            )
        
        # 비밀번호 검증
        if not verify_password(password, user.password):
            raise CustomException(
                ErrorCode.INVALID_CREDENTIALS,
                source_function="AuthService.login"
            )
        
        # 토큰 생성
        user_data = {
            "username": user.username,
            "ulid": user.ulid,
            "email": user.email
        }
        
        access_token = await create_jwt_token(
            user_data=user_data,
            token_type="access",
            db_service=self.db_service,
            log_model=self.log_model,
            request=request
        )
        
        refresh_token = await create_jwt_token(
            user_data=user_data,
            token_type="refresh",
            db_service=self.db_service,
            log_model=self.log_model,
            request=request
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        } 