from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp import Context


# FastMCPのアプリインスタンスを作成
mcp = FastMCP('mcp_test')

@mcp.prompt()
async def process_with_resource(ctx: Context, instruction: str) -> str:
    """
        MCPサーバーが保持するテンプレートリソースを活用し、ユーザーの指示を実行するためのプロンプトを生成する
    """
    # ロギング
    await ctx.info(f"Prompt機能が呼び出されました: '{instruction}'")

    # あとで記述

    return f"mcp_test MCPサーバー上のリソースを利用して、以下の指示を実行してください。 \n {instruction}"

@mcp.prompt()
async def suggest_template(ctx: Context, theme: str) -> str:
    """
        指定されたテーマに適したテンプレートを調査・提案し、選択後に作成・保存するワークフローを案内する
    """
    await ctx.info(f"2つ目のPrompt機能が呼び出されました: '{theme}")

    # あとで記述

    return f"""以下の順で処理を行ってください。
    {theme}のファイルについて、必要な項目を洗い出し、推奨されるテンプレートやフォーマットをWebで検索してください。
    調査された内容を整理し、3つのパターンを提示してください。
    提示されたパターンから選ばれたら、そのテンプレートファイルを作成してください。
    このMCPサーバーの登録ツールを作成して、作成したファイルの保存をしてください。
    """

# @mcp.resource()
# async def


if __name__ == "__main__":
    # サーバーを起動
    mcp.run()
