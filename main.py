from mcp.server.fastmcp import FastMCP

# FastMCPのアプリインスタンスを作成
mcp = FastMCP('mcp_test')

def main():
    print("Hello from mcp-test!")


if __name__ == "__main__":
    # サーバーを起動
    mcp.run()
