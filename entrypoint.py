from mcp.server.fastmcp import FastMCP
mcp = FastMCP()

@mcp.tool()
def get_wether(city_name:str) -> str:
    """
    param : 도시이름
    return : 00의 날씨는 몹시 좋아요
    """
    result : str = "f{city_name의 날씨는 몹시 좋아요"
    return result

if __name__ == "__entrypoint__":
    print(f"Start MCP Server!!!")
    mcp.run(transport = "studio")
