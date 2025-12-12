"""
애플리케이션 설정 (Application Configuration)

이 파일은 애플리케이션의 모든 설정값을 관리합니다.
Java의 application.properties 또는 application.yml과 동일한 역할입니다.

Pydantic이란?
- Python의 데이터 검증 라이브러리입니다.
- Java의 Bean Validation (@Valid, @NotNull 등)과 유사합니다.
- 타입 체크와 환경변수 자동 로딩 기능을 제공합니다.
"""

# pydantic_settings: 환경변수를 자동으로 읽어서 클래스 속성에 매핑해주는 라이브러리
# Java Spring Boot의 @ConfigurationProperties와 유사한 기능입니다.
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    """
    애플리케이션 설정 클래스

    Java로 비유하면:
    @Configuration
    @ConfigurationProperties
    public class AppConfig { ... }

    특징:
    - BaseSettings를 상속받아 환경변수 자동 로딩 기능을 사용합니다.
    - .env 파일에서 환경변수를 읽어옵니다.
    - 타입 힌트(str, int, float)를 통해 자동으로 타입 변환이 일어납니다.
    """

    # model_config: Pydantic의 설정을 정의합니다.
    # Java의 @PropertySource와 비슷한 역할입니다.
    model_config = SettingsConfigDict(
        env_file=".env",              # .env 파일에서 환경변수를 읽습니다. (Java의 .properties 파일과 유사)
        env_file_encoding="utf-8",    # 파일 인코딩 설정 (한글 지원을 위해 UTF-8 사용)
        extra="ignore",               # .env에 정의되지 않은 추가 환경변수는 무시합니다.
    )

    # ========================================
    # 서버 설정 (Server Settings)
    # ========================================

    # HOST: 서버가 바인딩될 IP 주소
    # "0.0.0.0" = 모든 네트워크 인터페이스에서 접속 허용 (Java의 server.address와 동일)
    # Python의 타입 힌트: 변수명: 타입 = 기본값
    # Java로 비유하면: private String HOST = "0.0.0.0";
    HOST: str = "0.0.0.0"

    # PORT: 서버가 사용할 포트 번호
    # Java의 server.port와 동일합니다.
    PORT: int = 8000

    # AGENT_NAME: MCP 에이전트의 이름
    # 클라이언트(AI 모델)가 이 서버를 식별할 때 사용합니다.
    AGENT_NAME: str = "test-agent"

    # ========================================
    # OpenAI API 설정 (OpenAI Settings)
    # ========================================
    # 참고: 이름은 OPENAI지만 실제로는 Google의 Gemini API를 사용하고 있습니다.
    # LangChain의 ChatOpenAI는 OpenAI 호환 API라면 어떤 것이든 사용할 수 있습니다.

    # OPENAI_API_KEY: API 인증 키
    # 보안 주의: 실제 운영 환경에서는 코드에 직접 넣지 말고 .env 파일이나 환경변수로 관리해야 합니다!
    # Java의 @Value("${api.key}") 와 유사합니다.
    OPENAI_API_KEY: str = "AIzaSyBgqJeWCI8NG7gQ_8jwGFmmQEvPOZUFpeU"

    # OPENAI_MODEL: 사용할 AI 모델의 이름
    # 예: "gpt-4", "gpt-3.5-turbo", "gemini-2.5-flash" 등
    OPENAI_MODEL: str = "gemini-2.5-flash"

    # OPENAI_TEMPERATURE: 응답의 창의성/무작위성 조절 (0.0 ~ 2.0)
    # - 0.0에 가까울수록: 일관되고 예측 가능한 답변 (결정론적)
    # - 2.0에 가까울수록: 창의적이고 다양한 답변 (무작위적)
    # - 0.7은 균형잡힌 중간값입니다.
    OPENAI_TEMPERATURE: float = 0.7

    # ========================================
    # 로깅 설정 (Logging)
    # ========================================

    # LOG_LEVEL: 로그 출력 레벨
    # Python의 logging 레벨: DEBUG < INFO < WARNING < ERROR < CRITICAL
    # Java의 log4j 레벨(TRACE, DEBUG, INFO, WARN, ERROR)과 거의 동일합니다.
    LOG_LEVEL: str = "INFO"


# ========================================
# 전역 설정 인스턴스 (Global Config Instance)
# ========================================

# config: AppConfig의 싱글톤 인스턴스를 생성합니다.
# Java로 비유하면:
#   public static final AppConfig config = new AppConfig();
# 또는 Spring의 @Bean과 유사합니다.
#
# 이 시점에 .env 파일이 자동으로 읽혀서 환경변수들이 로딩됩니다.
config = AppConfig()


def get_config() -> AppConfig:
    """
    설정 객체를 반환하는 함수

    Java의 getter 메서드와 동일합니다:
    public static AppConfig getConfig() {
        return config;
    }

    반환값 (Returns):
        AppConfig: 애플리케이션 설정 객체

    Python의 타입 힌트 -> AppConfig는 반환 타입을 명시합니다.
    Java의 메서드 시그니처에서 반환 타입을 앞에 쓰는 것과 동일하지만,
    Python에서는 화살표(->) 뒤에 씁니다.
    """
    return config
