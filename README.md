# Test MCP Server

간단한 MCP 서버 구현 (FastMCP + LangGraph)

## 프로젝트 구조

```
test-mcp/
├── app/
│   ├── core/
│   │   ├── agents/
│   │   │   └── simple_agent.py    # LangGraph 에이전트
│   │   └── config.py               # 설정 관리
│   ├── routers/
│   │   └── tool_router.py          # MCP 도구 등록
│   └── server.py                   # FastMCP 서버
├── entrypoint.py                   # 실행 진입점
├── pyproject.toml                  # 프로젝트 메타데이터
└── .env                            # 환경 변수 (직접 생성 필요)
```

## 주요 기능

1. **FastMCP 서버**: MCP 프로토콜 기반 서버
2. **LangGraph 에이전트**: OpenAI를 사용한 간단한 AI 에이전트
3. **2개의 도구**:
   - `ask_question`: AI 에이전트에게 질문
   - `get_greeting`: 인사말 받기

## 설치 및 실행

### 1. 환경 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집 (OPENAI_API_KEY 필수!)
nano .env
```

### 2. 의존성 설치

```bash
# Python 3.12 이상 필요
python -m pip install -e .

# 또는 uv 사용 (권장)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
```

### 3. 서버 실행

```bash
# 직접 실행
python entrypoint.py

# 또는 uv로 실행
uv run python entrypoint.py
```

## MCP 도구 사용법

### Claude Desktop과 연동

`claude_desktop_config.json`에 추가:

```json
{
  "mcpServers": {
    "test-agent": {
      "command": "python",
      "args": ["/home/ignakio/project/test-mcp/entrypoint.py"]
    }
  }
}
```

### 사용 가능한 도구

#### 1. ask_question
AI 에이전트에게 질문합니다.

**파라미터:**
- `query` (str): 질문 내용

**예시:**
```
ask_question("Python에서 비동기 프로그래밍이 뭐야?")
```

#### 2. get_greeting
개인화된 인사말을 받습니다.

**파라미터:**
- `name` (str, optional): 이름 (기본값: "User")

**예시:**
```
get_greeting("홍길동")
# 출력: "Hello, 홍길동! How can I help you today?"
```

## 코드 설명

### SimpleAgent (app/core/agents/simple_agent.py)

LangGraph를 사용한 간단한 에이전트:

```python
# 워크플로우
START → call_llm → END

# 상태 정의
class AgentState(TypedDict):
    messages: list[BaseMessage]
    user_query: str
    final_response: str | None
```

### 주요 특징

- **단일 LLM 호출**: 복잡한 루프 없이 한 번만 호출
- **OpenAI 통합**: ChatOpenAI 사용
- **비동기 처리**: async/await 패턴

## 환경 변수

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `HOST` | 0.0.0.0 | 서버 호스트 |
| `PORT` | 8000 | 서버 포트 |
| `AGENT_NAME` | test-agent | 에이전트 이름 |
| `OPENAI_API_KEY` | (필수) | OpenAI API 키 |
| `OPENAI_MODEL` | gpt-4o-mini | 사용할 모델 |
| `OPENAI_TEMPERATURE` | 0.7 | 생성 온도 |
| `LOG_LEVEL` | INFO | 로그 레벨 |

## 확장 방법

### 새로운 도구 추가

`app/routers/tool_router.py`에 추가:

```python
@mcp.tool()
async def my_new_tool(param: str) -> str:
    """도구 설명

    Args:
        param: 파라미터 설명

    Returns:
        결과 설명
    """
    # 도구 로직
    return result
```

### 에이전트에 도구 바인딩

`app/core/agents/simple_agent.py` 수정:

```python
# LLM에 도구 바인딩
from langchain_core.tools import tool

@tool
def calculator(expression: str) -> float:
    """Calculate mathematical expressions"""
    return eval(expression)

# call_llm 메서드에서
tools = [calculator]
response = await self.llm.bind_tools(tools).ainvoke(messages)
```

## 문제 해결

### OpenAI API 키 오류
```bash
# .env 파일 확인
cat .env | grep OPENAI_API_KEY
```

### 의존성 오류
```bash
# 재설치
pip install -e . --force-reinstall
```

### 로그 확인
```bash
# 환경 변수 설정
export LOG_LEVEL=DEBUG
python entrypoint.py
```

## 참고 자료

- [FastMCP 문서](https://github.com/jlowin/fastmcp)
- [LangGraph 튜토리얼](https://python.langchain.com/docs/langgraph)
- [MCP 프로토콜](https://modelcontextprotocol.io/)
