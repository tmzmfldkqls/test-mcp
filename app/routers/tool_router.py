"""
MCP 도구 라우터 (MCP Tool Router)

이 파일은 MCP 서버에 도구(tool)들을 등록하는 역할을 합니다.
Java의 @RestController와 유사하게, AI가 호출할 수 있는 함수들을 정의합니다.

도구(Tool)란?
- MCP 서버가 AI 모델에게 제공하는 기능/함수입니다.
- AI는 필요할 때 이 도구들을 호출할 수 있습니다.
- Java로 비유하면:
  @RestController의 @GetMapping, @PostMapping 메서드와 유사합니다.
  AI가 HTTP 요청 대신 MCP 프로토콜로 이 함수들을 호출합니다.

예시:
- ask_question: AI 에이전트에게 질문을 하는 도구
- get_greeting: 인사말을 생성하는 도구
"""

import logging

# FastMCP: MCP 서버 클래스
from fastmcp import FastMCP

# agent: 이미 생성된 SimpleAgent 인스턴스를 가져옵니다.
# Java의 @Autowired나 의존성 주입과 유사합니다.
from app.core.agents.simple_agent import agent

# 로거 생성
logger = logging.getLogger(__name__)


def register_tools(mcp: FastMCP) -> None:
    """
    MCP 서버에 도구들을 등록하는 함수

    이 함수는 server.py의 create_app()에서 호출됩니다.
    여기에서 정의된 모든 함수(@mcp.tool() 데코레이터가 있는)가 MCP 도구로 등록됩니다.

    매개변수 (Parameters):
        mcp (FastMCP): MCP 서버 인스턴스

    반환값 (Returns):
        None: 반환값 없음 (void와 동일)

    -> None은 Java의 void와 동일합니다:
    public void registerTools(FastMCP mcp) { ... }

    데코레이터(Decorator)란?
    - @mcp.tool()은 Python의 데코레이터입니다.
    - Java의 어노테이션(@GetMapping, @PostMapping)과 매우 유사합니다.
    - 함수를 MCP 도구로 등록하고, 메타데이터를 추가합니다.
    """

    # ========================================
    # 도구 1: ask_question
    # ========================================

    # @mcp.tool() 데코레이터:
    # - 이 함수를 MCP 도구로 등록합니다.
    # - AI가 이 도구의 이름("ask_question")과 설명(docstring)을 보고 필요할 때 호출할 수 있습니다.
    #
    # Java로 비유하면:
    #   @PostMapping("/ask_question")
    #   @ApiOperation(value = "Ask a question to the AI agent")
    #   public String askQuestion(@RequestParam String query) { ... }
    @mcp.tool()
    async def ask_question(query: str) -> str:
        """
        AI 에이전트에게 질문하는 도구

        이 함수는 사용자의 질문을 받아서 AI 에이전트에게 전달하고,
        AI의 응답을 반환합니다.

        동작 흐름:
        1. 사용자(또는 AI)가 이 도구를 호출하면서 질문(query)을 전달합니다.
        2. 로그에 질문을 기록합니다.
        3. SimpleAgent의 invoke() 메서드를 호출하여 AI 응답을 받습니다.
        4. 로그에 응답(처음 100자)을 기록합니다.
        5. 전체 응답을 반환합니다.

        매개변수 (Args):
            query (str): AI에게 할 질문

        반환값 (Returns):
            str: AI 에이전트의 응답

        async/await:
        - 이 함수는 비동기 함수입니다.
        - AI 모델 호출은 네트워크 I/O가 발생하므로, 비동기로 처리하여 효율을 높입니다.
        - Java의 CompletableFuture 또는 Spring WebFlux의 Mono와 유사합니다.
        """

        # ========================================
        # 1. 로그 기록: 받은 질문
        # ========================================

        # logger.info(): INFO 레벨 로그를 출력합니다.
        # Java의 logger.info()와 동일합니다.
        # f-string을 사용하여 query 변수를 로그 메시지에 삽입합니다.
        logger.info(f"Received query: {query}")

        # ========================================
        # 2. AI 에이전트 호출
        # ========================================

        # await agent.invoke(query):
        # - agent: simple_agent.py에서 import한 SimpleAgent 인스턴스
        # - invoke(): 에이전트의 메인 실행 메서드 (비동기)
        # - await: 비동기 함수의 완료를 기다립니다.
        #
        # Java로 비유하면:
        #   String response = agent.invoke(query).get(); // CompletableFuture
        #   또는
        #   String response = agentService.askQuestion(query); // 일반 동기 호출
        #
        # 이 과정에서:
        # 1. SimpleAgent가 LangGraph 워크플로우를 실행합니다.
        # 2. AI 모델(Gemini)에게 질문을 보냅니다.
        # 3. AI의 응답을 받아서 반환합니다.
        response = await agent.invoke(query)

        # ========================================
        # 3. 로그 기록: 생성된 응답
        # ========================================

        # response[:100]:
        # - Python의 문자열 슬라이싱입니다.
        # - 응답의 처음 100자만 가져옵니다.
        # - Java의 response.substring(0, Math.min(100, response.length()))와 유사합니다.
        #
        # 왜 100자만 로그에 남기나요?
        # - 응답이 매우 길 수 있으므로, 로그 파일이 너무 커지는 것을 방지하기 위해서입니다.
        # - 전체 응답은 반환되므로, 로그에는 요약만 남깁니다.
        logger.info(f"Generated response: {response[:100]}...")

        # ========================================
        # 4. 응답 반환
        # ========================================

        # AI의 전체 응답을 반환합니다.
        # MCP 프로토콜을 통해 호출자(AI 또는 사용자)에게 전달됩니다.
        return response

    # ========================================
    # 도구 2: get_greeting
    # ========================================

    # 또 다른 MCP 도구를 정의합니다.
    # 이것은 간단한 예제 도구로, AI 에이전트 없이 직접 인사말을 생성합니다.
    @mcp.tool()
    async def get_greeting(name: str = "User") -> str:
        """
        개인화된 인사말을 생성하는 도구

        이 도구는 간단한 예제입니다.
        AI 에이전트를 호출하지 않고, 직접 문자열을 생성하여 반환합니다.

        매개변수 (Args):
            name (str): 인사할 사람의 이름 (기본값: "User")

        반환값 (Returns):
            str: 인사말 메시지

        기본값(Default Value):
        - name: str = "User"는 name 매개변수의 기본값이 "User"임을 의미합니다.
        - 호출할 때 name을 생략하면 "User"가 사용됩니다.
        - Java로 비유하면:
          public String getGreeting(String name) {
              if (name == null) name = "User";
              ...
          }
          또는 메서드 오버로딩:
          public String getGreeting() {
              return getGreeting("User");
          }
          public String getGreeting(String name) { ... }

        async 키워드를 사용하는 이유:
        - MCP 도구는 모두 async 함수여야 합니다.
        - 이 함수는 실제로 비동기 작업을 하지 않지만, MCP 프로토콜 규격에 맞추기 위해 async를 사용합니다.
        """

        # f-string을 사용하여 name을 포함한 인사말을 생성합니다.
        # Java로 비유하면:
        #   return String.format("Hello, %s! How can I help you today?", name);
        #   또는
        #   return "Hello, " + name + "! How can I help you today?";
        return f"Hello, {name}! How can I help you today?"

    # ========================================
    # 추가 도구 정의 가능
    # ========================================
    #
    # 이곳에 더 많은 @mcp.tool() 함수를 정의할 수 있습니다.
    # 예를 들어:
    #
    # @mcp.tool()
    # async def calculate_sum(a: int, b: int) -> int:
    #     """두 숫자의 합을 계산합니다"""
    #     return a + b
    #
    # @mcp.tool()
    # async def get_current_time() -> str:
    #     """현재 시각을 반환합니다"""
    #     from datetime import datetime
    #     return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #
    # 각 도구는 AI가 필요할 때 선택하여 사용할 수 있는 기능입니다.
