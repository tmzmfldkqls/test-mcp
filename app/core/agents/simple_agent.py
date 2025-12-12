"""
간단한 LangGraph 에이전트 구현 (Simple LangGraph Agent Implementation)

이 파일은 AI 에이전트의 핵심 로직을 구현합니다.
사용자의 질문을 받아서 AI 모델(LLM)에게 전달하고, 응답을 반환하는 역할을 합니다.

LangGraph란?
- AI 에이전트의 작업 흐름(workflow)을 그래프 구조로 정의할 수 있게 해주는 라이브러리입니다.
- Java로 비유하면: 상태 머신(State Machine) 또는 워크플로우 엔진과 유사합니다.
- 노드(Node)와 엣지(Edge)로 구성되며, 각 노드는 특정 작업을 수행합니다.

LangChain이란?
- AI 애플리케이션을 만들기 위한 프레임워크입니다.
- 다양한 AI 모델(OpenAI, Google Gemini 등)을 통합하여 사용할 수 있게 해줍니다.
- Java의 Spring Framework와 비슷한 역할입니다.
"""

import logging
import sys
# typing: Python의 타입 힌트를 위한 모듈 (Java의 제네릭과 유사)
# - Literal: 특정 값만 허용하는 타입 (예: Literal["end"]는 "end"만 가능)
# - TypedDict: 딕셔너리의 구조를 정의 (Java의 DTO 클래스와 유사)
from typing import Literal, TypedDict

# langchain_core.messages: AI와 대화할 때 사용하는 메시지 타입들
# - SystemMessage: 시스템 프롬프트 (AI의 역할/성격 정의)
# - HumanMessage: 사용자의 메시지
# - AIMessage: AI의 응답 메시지
# - BaseMessage: 모든 메시지의 기본 타입 (Java의 인터페이스와 유사)
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

# ChatOpenAI: OpenAI API (또는 호환 API)를 호출하는 클래스
# Java로 비유하면: RestTemplate 또는 HttpClient와 유사한 API 클라이언트입니다.
from langchain_openai import ChatOpenAI

# LangGraph 관련 import:
# - StateGraph: 상태 기반 워크플로우를 정의하는 클래스
# - END: 워크플로우의 종료를 나타내는 상수
# - CompiledStateGraph: 컴파일된(실행 가능한) 워크플로우
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

# 애플리케이션 설정을 가져옵니다.
from app.core.config import config

# ========================================
# 로거 설정 (Logger Configuration)
# ========================================

# 로거 인스턴스 생성
logger = logging.getLogger(__name__)

# StreamHandler: 로그를 어디로 출력할지 결정합니다.
# sys.stderr = 표준 에러 스트림 (콘솔의 에러 출력)
# Java의 System.err과 동일합니다.
# 참고: 일반 출력(sys.stdout)과 에러 출력(sys.stderr)을 분리하여 관리합니다.
handler = logging.StreamHandler(sys.stderr)

# Formatter: 로그 메시지의 형식을 지정합니다.
# Java의 PatternLayout과 동일한 역할입니다.
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)


# ========================================
# 에이전트 상태 정의 (Agent State Definition)
# ========================================

class AgentState(TypedDict):
    """
    에이전트의 상태를 정의하는 클래스

    TypedDict는 Python의 딕셔너리에 타입 정보를 추가한 것입니다.
    Java로 비유하면:
    public class AgentState {
        private List<BaseMessage> messages;
        private String userQuery;
        private String finalResponse;
    }

    워크플로우가 실행되는 동안 이 상태 객체가 각 노드를 거치면서 업데이트됩니다.
    마치 Java의 Context 객체나 DTO가 메서드 체인을 따라 전달되는 것과 비슷합니다.
    """

    # messages: 대화 히스토리를 저장하는 리스트
    # Java의 List<BaseMessage>와 동일합니다.
    messages: list[BaseMessage]

    # user_query: 사용자가 입력한 질문
    # Java의 String userQuery;와 동일합니다.
    user_query: str

    # final_response: AI의 최종 응답
    # str | None = Java의 String (nullable) 또는 Optional<String>과 유사합니다.
    # Python 3.10+에서는 | 연산자로 Union 타입을 표현합니다.
    final_response: str | None


# ========================================
# SimpleAgent 클래스
# ========================================

class SimpleAgent:
    """
    간단한 AI 에이전트 클래스

    역할:
    1. 사용자의 질문을 받습니다.
    2. AI 모델(LLM)에게 질문을 전달합니다.
    3. AI의 응답을 받아서 반환합니다.

    LangGraph 워크플로우 구조:
    [시작] -> [LLM 호출] -> [종료]

    Java로 비유하면 Service 클래스와 유사합니다:
    @Service
    public class SimpleAgent { ... }
    """

    def __init__(self):
        """
        생성자 (Constructor)

        Java의 생성자와 동일합니다:
        public SimpleAgent() { ... }

        초기화 작업:
        1. ChatOpenAI 클라이언트를 생성합니다. (AI 모델과 통신하는 객체)
        2. LangGraph 워크플로우를 정의하고 컴파일합니다.
        """

        # ========================================
        # LLM (Large Language Model) 클라이언트 생성
        # ========================================

        # ChatOpenAI: OpenAI API를 호출하는 클라이언트 객체
        # 실제로는 Gemini API를 사용하지만, OpenAI 호환 인터페이스로 호출합니다.
        #
        # Java로 비유하면:
        #   RestTemplate llm = new RestTemplate();
        #   llm.setUrl("https://api.openai.com/...");
        self.llm = ChatOpenAI(
            model=config.OPENAI_MODEL,              # 사용할 AI 모델 이름 (예: "gemini-2.5-flash")
            temperature=config.OPENAI_TEMPERATURE,  # 응답의 창의성 조절 (0.0 ~ 2.0)
            api_key=config.OPENAI_API_KEY,          # API 인증 키
        )

        # 로그 출력: LLM 객체 정보 확인
        logger.info(f"어떻게 나오는지 보자 : {self.llm}")

        # ========================================
        # LangGraph 워크플로우 생성
        # ========================================

        # StateGraph: 상태 기반 워크플로우를 생성합니다.
        # AgentState를 인자로 전달하여, 이 워크플로우가 AgentState 타입의 상태를 사용함을 명시합니다.
        #
        # Java로 비유하면:
        #   WorkflowBuilder<AgentState> workflow = new WorkflowBuilder<>();
        self.workflow = StateGraph(AgentState)

        # ========================================
        # 워크플로우 컴파일
        # ========================================

        # _compile() 메서드를 호출하여 워크플로우를 정의하고 컴파일합니다.
        # 컴파일된 워크플로우는 실행 가능한 상태가 됩니다.
        #
        # Java로 비유하면:
        #   CompiledWorkflow compiledWorkflow = workflow.build();
        #
        # 타입 힌트 : CompiledStateGraph는 이 변수의 타입을 명시합니다.
        self.compiled_workflow: CompiledStateGraph = self._compile()

    # ========================================
    # 메인 실행 메서드
    # ========================================

    async def invoke(self, user_query: str) -> str:
        """
        에이전트를 실행하고 응답을 반환합니다.

        이것이 외부에서 호출하는 메인 메서드입니다.
        Java로 비유하면:
        public String invoke(String userQuery) { ... }

        async/await란?
        - Python의 비동기 프로그래밍 키워드입니다.
        - Java의 CompletableFuture, Spring의 @Async와 유사합니다.
        - 네트워크 I/O 대기 시간 동안 다른 작업을 처리할 수 있게 해줍니다.

        매개변수 (Parameters):
            user_query (str): 사용자의 질문

        반환값 (Returns):
            str: AI의 응답

        실행 흐름:
        1. 초기 상태(initial_state)를 생성합니다.
        2. 워크플로우를 실행합니다. (ainvoke = async invoke)
        3. 최종 응답을 추출하여 반환합니다.
        """

        # ========================================
        # 초기 상태 생성
        # ========================================

        # AgentState 타입의 딕셔너리를 생성합니다.
        # Java로 비유하면:
        #   AgentState initialState = new AgentState();
        #   initialState.setMessages(new ArrayList<>());
        #   initialState.setUserQuery(userQuery);
        #   initialState.setFinalResponse(null);
        initial_state: AgentState = {
            "messages": [],              # 빈 메시지 리스트로 시작
            "user_query": user_query,    # 사용자 질문 저장
            "final_response": None,      # 아직 응답이 없으므로 None (Java의 null)
        }

        # ========================================
        # 워크플로우 실행
        # ========================================

        # await: 비동기 함수의 완료를 기다립니다.
        # Java의 future.get()이나 CompletableFuture.join()과 유사합니다.
        #
        # ainvoke(): 워크플로우를 비동기로 실행합니다.
        # - initial_state를 입력으로 전달
        # - 워크플로우의 각 노드를 순서대로 실행
        # - 최종 상태(result)를 반환
        result: AgentState = await self.compiled_workflow.ainvoke(initial_state)

        # ========================================
        # 최종 응답 반환
        # ========================================

        # result.get("final_response", "No response generated"):
        # - result 딕셔너리에서 "final_response" 키의 값을 가져옵니다.
        # - 만약 키가 없거나 None이면 "No response generated"를 기본값으로 반환합니다.
        #
        # Java로 비유하면:
        #   return Optional.ofNullable(result.getFinalResponse())
        #                  .orElse("No response generated");
        return result.get("final_response", "No response generated")

    # ========================================
    # LLM 호출 메서드 (워크플로우 노드)
    # ========================================

    async def call_llm(self, state: AgentState) -> AgentState:
        """
        AI 모델(LLM)을 호출하는 노드

        이 메서드는 워크플로우의 노드로 등록됩니다.
        워크플로우가 실행될 때 자동으로 호출됩니다.

        Java로 비유하면:
        public AgentState callLlm(AgentState state) { ... }

        매개변수 (Parameters):
            state (AgentState): 현재 워크플로우 상태

        반환값 (Returns):
            AgentState: 업데이트된 상태 (AI 응답이 추가됨)

        실행 흐름:
        1. 시스템 메시지와 사용자 메시지를 준비합니다.
        2. AI 모델을 호출합니다.
        3. 응답을 상태에 저장하고 반환합니다.
        """

        # ========================================
        # 메시지 준비
        # ========================================

        # AI에게 보낼 메시지 리스트를 생성합니다.
        # Java로 비유하면:
        #   List<Message> messages = new ArrayList<>();
        #   messages.add(new SystemMessage("You are..."));
        #   messages.add(new HumanMessage(userQuery));
        messages = [
            # SystemMessage: AI의 역할/성격을 정의하는 시스템 프롬프트
            # "당신은 도움이 되는 AI 어시스턴트입니다"라는 지시를 AI에게 줍니다.
            SystemMessage(content="You are a helpful AI assistant."),

            # HumanMessage: 사용자의 실제 질문
            # state["user_query"]에서 사용자가 입력한 질문을 가져옵니다.
            HumanMessage(content=state["user_query"]),
        ]

        # ========================================
        # AI 모델 호출
        # ========================================

        # await self.llm.ainvoke(messages):
        # - AI 모델에게 메시지를 보내고 응답을 기다립니다.
        # - 비동기 HTTP 요청을 보내는 것과 유사합니다.
        #
        # Java로 비유하면:
        #   AIMessage response = restTemplate.postForObject(
        #       "https://api.openai.com/chat/completions",
        #       messages,
        #       AIMessage.class
        #   );
        #
        # 반환 타입: AIMessage (AI의 응답 메시지 객체)
        response: AIMessage = await self.llm.ainvoke(messages)

        # ========================================
        # 상태 업데이트
        # ========================================

        # state["messages"]: 전체 대화 히스토리를 저장합니다.
        # messages + [response]: 기존 메시지 리스트에 AI 응답을 추가합니다.
        # Python의 리스트 연결: [a, b] + [c] = [a, b, c]
        state["messages"] = messages + [response]

        # state["final_response"]: AI의 응답 텍스트를 저장합니다.
        # response.content: AIMessage 객체에서 실제 텍스트 내용을 추출합니다.
        state["final_response"] = response.content

        # 업데이트된 상태를 반환합니다.
        # LangGraph가 이 상태를 다음 노드로 전달합니다.
        return state

    # ========================================
    # 종료 조건 판단 메서드
    # ========================================

    def should_end(self, state: AgentState) -> Literal["end"]:
        """
        워크플로우를 종료할지 결정하는 메서드

        Literal["end"]: 반환값이 정확히 "end" 문자열만 가능함을 의미합니다.
        Java의 enum과 비슷한 개념입니다:
        public enum Decision { END }
        public Decision shouldEnd(AgentState state) { return Decision.END; }

        이 간단한 예제에서는 항상 종료합니다.
        더 복잡한 에이전트에서는 조건에 따라 다른 노드로 이동할 수 있습니다.

        예를 들어:
        - "end": 종료
        - "continue": 다른 노드로 계속
        - "retry": 재시도
        """
        return "end"

    # ========================================
    # 워크플로우 컴파일 메서드
    # ========================================

    def _compile(self) -> CompiledStateGraph:
        """
        LangGraph 워크플로우를 정의하고 컴파일합니다.

        Java의 Builder 패턴과 유사합니다:
        return new WorkflowBuilder()
            .addNode("llm", this::callLlm)
            .setEntryPoint("llm")
            .addEdge("llm", END)
            .build();

        워크플로우 구조:
        [시작] -> "llm" 노드 (call_llm 실행) -> [종료]

        반환값 (Returns):
            CompiledStateGraph: 실행 가능한 워크플로우
        """

        # ========================================
        # 노드 추가
        # ========================================

        # add_node("이름", 함수):
        # - "llm"이라는 이름의 노드를 추가합니다.
        # - 이 노드가 실행되면 self.call_llm 메서드가 호출됩니다.
        #
        # Java로 비유하면:
        #   workflow.addNode("llm", this::callLlm);
        self.workflow.add_node("llm", self.call_llm)

        # ========================================
        # 시작점 설정
        # ========================================

        # set_entry_point("노드 이름"):
        # - 워크플로우가 시작될 때 가장 먼저 실행될 노드를 지정합니다.
        # - "llm" 노드부터 시작합니다.
        self.workflow.set_entry_point("llm")

        # ========================================
        # 조건부 엣지 추가
        # ========================================

        # add_conditional_edges():
        # - 특정 노드 실행 후, 조건에 따라 다음 노드를 결정합니다.
        #
        # 매개변수:
        # 1. "llm": 이 노드가 실행된 후
        # 2. self.should_end: 이 함수를 호출하여 다음 행동을 결정
        # 3. {"end": END}: should_end()가 "end"를 반환하면 워크플로우 종료
        #
        # Java로 비유하면:
        #   workflow.addConditionalEdge("llm", this::shouldEnd, Map.of("end", END));
        #
        # END: LangGraph의 특수 상수로, 워크플로우 종료를 의미합니다.
        self.workflow.add_conditional_edges(
            "llm",              # 출발 노드
            self.should_end,    # 조건 판단 함수
            {"end": END},       # 반환값에 따른 다음 노드 매핑
        )

        # ========================================
        # 컴파일
        # ========================================

        # compile(): 워크플로우를 실행 가능한 상태로 컴파일합니다.
        # Java의 build() 메서드와 유사합니다.
        # 컴파일 과정에서 워크플로우의 유효성을 검증하고 최적화합니다.
        return self.workflow.compile()


# ========================================
# 전역 에이전트 인스턴스 (Global Agent Instance)
# ========================================

# SimpleAgent의 싱글톤 인스턴스를 생성합니다.
# 애플리케이션 전체에서 하나의 에이전트 인스턴스만 사용합니다.
#
# Java로 비유하면:
#   public static final SimpleAgent agent = new SimpleAgent();
#
# 또는 Spring의 @Bean:
#   @Bean
#   public SimpleAgent agent() {
#       return new SimpleAgent();
#   }
#
# 이 인스턴스는 tool_router.py에서 import되어 사용됩니다.
agent = SimpleAgent()
