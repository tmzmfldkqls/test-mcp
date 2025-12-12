"""
FastMCP 서버 초기화 (FastMCP Server Initialization)

이 파일은 MCP 서버의 핵심 설정과 초기화를 담당합니다.
Java로 비유하면 Spring Boot의 @SpringBootApplication이 있는 메인 클래스와 유사합니다.

FastMCP란?
- MCP(Model Context Protocol) 서버를 쉽게 만들 수 있게 해주는 Python 프레임워크입니다.
- Java의 Spring Framework처럼 서버 구축을 간편하게 해줍니다.
- AI 모델(Claude 등)이 사용할 수 있는 도구(tools)를 등록하고 관리합니다.
"""

# logging: Python의 표준 로깅 라이브러리 (Java의 log4j, slf4j와 동일)
import logging

# FastMCP: MCP 서버를 만들기 위한 메인 클래스
# Java의 @SpringBootApplication과 유사한 역할입니다.
from fastmcp import FastMCP

# 설정 파일과 도구 등록 함수를 import
from app.core.config import config
from app.routers.tool_router import register_tools

# ========================================
# 로깅 설정 (Logging Configuration)
# ========================================

# logging.basicConfig(): 로깅 시스템의 기본 설정을 합니다.
# Java의 log4j.properties 또는 logback.xml 설정과 동일한 역할입니다.
logging.basicConfig(
    level=config.LOG_LEVEL,  # 로그 레벨 설정 (예: INFO, DEBUG, ERROR)
    # format: 로그 메시지의 형식을 정의합니다.
    # %(asctime)s = 시간 (Java의 %d{yyyy-MM-dd HH:mm:ss}와 유사)
    # %(name)s = 로거 이름 (보통 모듈 이름)
    # %(levelname)s = 로그 레벨 (INFO, ERROR 등)
    # %(message)s = 실제 로그 메시지
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# logger: 이 모듈(파일)에서 사용할 로거 인스턴스를 생성합니다.
# __name__은 현재 모듈의 이름을 자동으로 가져옵니다. (예: "app.server")
# Java로 비유하면:
#   private static final Logger logger = LoggerFactory.getLogger(ServerClass.class);
logger = logging.getLogger(__name__)


def create_app() -> FastMCP:
    """
    FastMCP 애플리케이션을 생성하고 설정합니다.

    Java Spring Boot로 비유하면:
    @Bean
    public Application createApp() { ... }

    실행 흐름:
    1. FastMCP 인스턴스를 생성합니다. (서버 객체 생성)
    2. 도구(tools)를 등록합니다. (API 엔드포인트 등록과 유사)
    3. 설정이 완료된 서버 인스턴스를 반환합니다.

    반환값 (Returns):
        FastMCP: 설정이 완료된 MCP 서버 인스턴스

    MCP의 "도구(Tool)"란?
    - AI 모델이 호출할 수 있는 함수/기능입니다.
    - Java의 REST API 엔드포인트(@GetMapping, @PostMapping)와 비슷한 개념입니다.
    - 예: "ask_question"이라는 도구를 등록하면, AI가 이 함수를 호출해서 질문을 할 수 있습니다.
    """

    # 로그 출력: 서버 생성 시작을 알립니다.
    # logger.info()는 Java의 logger.info()와 완전히 동일합니다.
    logger.info(f"Creating FastMCP server: {config.AGENT_NAME}")

    # ========================================

    # FastMCP 인스턴스 생성
    # ========================================

    # FastMCP 객체를 생성합니다. 생성자에 에이전트 이름을 전달합니다.
    # Java로 비유하면:
    #   FastMCP mcp = new FastMCP(config.getAgentName());
    #
    # 이 객체가 실제 MCP 서버의 핵심입니다.
    # 모든 도구(tool) 등록, 요청 처리 등이 이 객체를 통해 이루어집니다.
    mcp = FastMCP(config.AGENT_NAME)

    # ========================================
    # 도구 등록 (Tool Registration)
    # ========================================

    # register_tools() 함수를 호출하여 AI가 사용할 수 있는 도구들을 등록합니다.
    # Java Spring으로 비유하면:
    #   - @RestController 클래스의 @GetMapping, @PostMapping 메서드들을 등록하는 것과 유사합니다.
    #
    # tool_router.py 파일에서 @mcp.tool() 데코레이터로 정의된 함수들이 등록됩니다.
    # 예: ask_question(), get_greeting() 같은 함수들
    register_tools(mcp)

    # 로그 출력: 서버 생성 완료를 알립니다.
    logger.info("FastMCP server created successfully")

    # 설정이 완료된 MCP 서버 인스턴스를 반환합니다.
    return mcp


# ========================================
# 전역 MCP 인스턴스 (Global MCP Instance)
# ========================================

# create_app()을 호출하여 MCP 서버 인스턴스를 생성하고 전역 변수에 저장합니다.
# 이것은 싱글톤 패턴과 유사합니다.
#
# Java로 비유하면:
#   public static final FastMCP mcp = createApp();
#
# 왜 전역 변수로 만드나요?
# - 애플리케이션 전체에서 하나의 MCP 서버 인스턴스만 사용하기 위해서입니다.
# - entrypoint.py에서 이 mcp 인스턴스를 import해서 서버를 실행합니다.
#
# Python의 모듈 시스템:
# - Python에서는 모듈(파일)을 import할 때, 그 파일의 최상위 코드가 한 번만 실행됩니다.
# - 따라서 이 mcp 변수는 프로그램이 실행되는 동안 딱 한 번만 생성됩니다.
mcp = create_app()
