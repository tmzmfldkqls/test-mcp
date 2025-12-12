"""
애플리케이션 진입점 (Application Entrypoint)

이 파일은 Java의 main() 메서드가 있는 클래스와 동일한 역할을 합니다.
프로그램이 시작될 때 가장 먼저 실행되는 파일입니다.

MCP (Model Context Protocol)란?
- Claude나 다른 AI 모델이 외부 도구/데이터에 접근할 수 있게 해주는 프로토콜입니다.
- Java로 비유하면: REST API 서버를 만들어서 AI가 HTTP로 우리의 기능을 호출할 수 있게 하는 것과 비슷합니다.
- 하지만 MCP는 HTTP 대신 stdio(표준 입출력)를 사용해서 AI와 직접 통신합니다.
"""

# Python의 import는 Java의 import와 동일합니다.
# 다른 모듈(파일)에서 클래스나 함수를 가져옵니다.
from app.core.config import get_config  # 설정 정보를 가져오는 함수 (Java의 ConfigLoader와 유사)
from app.server import mcp  # FastMCP 서버 인스턴스 (Java의 싱글톤 객체와 유사)


def main():
    """
    메인 함수 - 서버를 시작합니다.

    Java의 public static void main(String[] args)와 동일한 역할입니다.
    Python에서는 함수로 정의되며, 클래스 안에 있을 필요가 없습니다.

    실행 흐름:
    1. 설정 파일(.env)에서 환경 변수를 읽어옵니다.
    2. 서버 시작 메시지를 콘솔에 출력합니다.
    3. FastMCP 서버를 실행합니다.
    """

    # get_config()를 호출하여 설정 객체를 가져옵니다.
    # Java의 Config config = ConfigLoader.getInstance(); 와 유사합니다.
    config = get_config()

    # f-string: Python의 문자열 포맷팅 방법입니다.
    # Java의 String.format() 또는 "문자열 " + 변수 연결과 동일합니다.
    # {} 안에 변수를 넣으면 자동으로 문자열로 변환되어 삽입됩니다.
    print(f"Starting {config.AGENT_NAME} on {config.HOST}:{config.PORT}")

    # MCP 서버를 실행합니다.
    # Java로 비유하면: server.start()를 호출하는 것과 같습니다.
    mcp.run(
        host=config.HOST,        # 서버가 바인딩될 호스트 주소 (예: "0.0.0.0" = 모든 네트워크 인터페이스)
        port=config.PORT,        # 서버가 사용할 포트 번호 (예: 8000)
        transport="stdio",       # 전송 방식: stdio = 표준 입출력 (콘솔 입출력을 통해 통신)
                                # HTTP 대신 stdio를 사용하여 AI 모델과 직접 통신합니다.
    )


# Python의 관용구: 이 파일이 직접 실행될 때만 main() 함수를 호출합니다.
# Java로 비유하면:
#   if (isMainClass) {
#       main();
#   }
# 이렇게 하면 이 파일을 다른 곳에서 import 했을 때는 main()이 자동 실행되지 않습니다.
if __name__ == "__main__":
    main()
