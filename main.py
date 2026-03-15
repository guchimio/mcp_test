import base64
import os
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp import Context
from mcp.server.fastmcp.exceptions import ResourceError
from mcp.server.fastmcp.exceptions import ToolError
from mcp.server.fastmcp.exceptions import ValidationError
from typing import Tuple
from typing import List
from pydantic import AnyUrl
from mcp.types import ListResourcesResult, Resource

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

@mcp.resource("mcp://template/{file_name}")
async def get_template_file(ctx: Context, file_name: str) -> str:
    """
    templateディレクトリから、指定されたファイル名のテンプレートを読み込みます。
    """
    # ファイル名からディレクトリトラバーサルの試みを除去
    safe_file_name = file_name.replace("..", "")
    file_path = f"templates/{safe_file_name}"

    await ctx.info(f"リソースを読み込みます: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        await ctx.error(f"リソースファイルが見つかりません: {file_path}")
        raise ResourceError(f"テンプレートファイル「{file_name}」は見つかりませんでした。")

@mcp.resource(
    uri = "mcp://image/{image_name}",
    name = "Get Image",
    mime_type="image/png"
)
async def get_image(ctx: Context, image_name: str) -> str:
    """
    imagesディレクトリから、指定された画像ファイルをバイナリデータとして読み込みます。
    """
    # ファイル名からディレクトリトラバーサルの試みを除去
    safe_file_name = image_name.replace("..", "")
    # 今回はpng形式のみ
    file_path = f"images/{safe_file_name}.png"
    await ctx.info("画像リソースを読み込みます: {file_path}")

    try:
        with open(file_path, "rb") as f:
            content = f.read()
            base64_byte = base64.b64encode(content)
            return base64_byte.decode('utf-8')
    except FileNotFoundError:
        await ctx.error(f"画像ファイルが見つかりません: {file_path}")
        raise ResourceError(f"画像ファイル「{image_name}」は見つかりませんでした。")

@mcp.tool()
async def list_all_templates(ctx: Context) -> List[str]:
    """
    templatesディレクトリ内のすべてのファイル名をリストで返します。
    """
    try:
        return sorted(os.listdir("templates"))
    except Exception as e:
        raise ToolError(f"テンプレート一覧の取得中にエラーが発生しました: {e}")

@mcp.tool()
async def list_templates(ctx: Context, cursor: str = '0') -> ListResourcesResult:
    """
    templatesディレクトリ内のファイル一覧をページネーション付きで取得します。
    """
    await ctx.info(f"テンプレート一覧を取得します (cursor: {cursor})")

    page_size = 2   # 1ページあたりの項目数


    # カーソルを解釈し、ページの開始位置を決定
    try:
        if cursor is None:
            start = 0
        else:
            start = int(cursor)
    except ValueError:
        raise ValidationError("無効なカーソルです。数値を指定してください。")

    end = start + page_size

    try:
        all_files = sorted(os.listdir("templates")) # 順序を安定させた状態で取得する

        total_files = len(all_files)
        paginated_files = all_files[start:end]

        # 現在のページのアイテムをResourceオブジェクトのリストとして作成
        page_items = [
            Resource(uri = AnyUrl(f"mcp://templates/{file_name}"),
                     name = file_name,
                     description = f"{file_name}"
                     )
                     for file_name in paginated_files
        ]

        has_more = end < total_files    # 表示すべき項目がまだあるか
        # 次のページが存在する場合、次のカーソルを生成
        if has_more:
            next_cursor = str(end)
        else:
            next_cursor = None

        return ListResourcesResult(resources=page_items, nextCursor=next_cursor)

    except Exception as e:
        await ctx.error(f"テンプレート一覧の取得中にエラーが発生しました: {e}")
        raise ToolError(f"テンプレート一覧の取得中にエラーが発生しました: {e}")


if __name__ == "__main__":
    # サーバーを起動
    mcp.run()
