import sys,os
import asyncio
import aiohttp
import gzip
from typing import Any
from lxml import etree
import i4srcm.lxmlutil as lx

class AsyncRCMFS_Client():
    """
    RCMFS クライアントクラス。

    このクラスは、指定されたURLとユーザー認証情報を使用してRCMFSと通信します。

    Attributes:
        _user_name (str): ユーザー名。
        _user_passwd (str): ユーザーパスワード。
        _user_info_id (UserInfoId): ユーザー情報ID。
        _user_id (UserId): ユーザーID。
        _project_id (ProjectId): カレントのプロジェクトID。
        _version (str): RCMFS(サーバ側)のバージョン情報。
        _buildTime (str): RCMFS(サーバ側)のビルド時間。
    """
    def __init__(self, url, *, logfile:str|None=None,tmpdir:str='tmp'):
        """
        RCMFS_Client のコンストラクタ。

        Args:
            url (str): 接続先のURL。
            username (str): ユーザー名。
            passwd (str): ユーザーパスワード。
            logfile (str, optional): ログファイルのパス。デフォルトは None。
            tmpdir (str, optional): 一時ディレクトリのパス。デフォルトは 'tmp'。
        """
        self._url = f"{url}/RCM-Client/action/request.html"
        self._version:str = ''
        self._buildTime:str = ''
        self._logfile = logfile
        self._tmpdir = tmpdir

    async def getOs(self) -> str:
        """サーバーのOS名を取得します。

        Returns:
            str: サーバーのOS名
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self._url}/getOS") as response:
                if response.status == 200:
                    return await response.text()
                else:
                    raise Exception(f"Failed to get OS: {response.status}")

    async def echoBack(self, wait: int | None = None) -> str:
        """サーバーにechoBackリクエストを送信し、サーバーの情報を取得します。

        Args:
            wait (int | None, optional): サーバー側での待機時間（ミリ秒）。デフォルトはNone。

        Returns:
            str: サーバーから返されたXML形式の情報
        """
        params = {}
        if wait is not None:
            params['wait'] = str(wait)

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self._url}/echoBack", params=params) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    raise Exception(f"Failed to echo back: {response.status}")

    async def getRemoteTime(self):
        """サーバーの時刻を取得します。

        Returns:
            str: サーバーの時刻
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self._url}/getRemoteTime") as response:
                if response.status == 200:
                    return await response.text()
                else:
                    raise Exception(f"Failed to get OS: {response.status}")

    async def getVersion(self):
        """サーバーのバージョンを取得します。

        Returns:
            str: サーバーのバージョン
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self._url}/getRemoteTime") as response:
                if response.status == 200:
                    return await response.text()
                else:
                    raise Exception(f"Failed to get OS: {response.status}")

    async def config(self, config_xml: str | None = None) -> str:
        """サーバーのシステム設定を取得または更新します。

        Args:
            config_xml (str | None, optional): 更新する設定のXML文字列。
                Noneの場合は現在の設定を取得します。

        Returns:
            str: サーバーから返されたXML形式の設定情報
        """
        async with aiohttp.ClientSession() as session:
            if config_xml is None:
                # GET: 現在の設定を取得
                async with session.get(f"{self._url}/config") as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        raise Exception(f"Failed to get config: {response.status}")
            else:
                # POST: 設定を更新
                headers = {'Content-Type': 'application/xml'}
                async with session.post(
                    f"{self._url}/config",
                    data=config_xml,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        raise Exception(f"Failed to update config: {response.status}")

    async def getfilelist(self, path: str = "C:/", lowerlevel: int = 2) -> list[dict[str, Any]]:
        """
        指定されたパスのファイルリストを取得します。

        Args:
            path (str): 取得するディレクトリパス。デフォルトは "C:/"
            lowerlevel (int): 取得する階層の深さ。デフォルトは2

        Returns:
            list[dict[str, Any]]: ファイルとディレクトリの情報のリスト。各要素は以下のキーを含む辞書：
                - type (str): "file" または "directory"
                - path (str): パス
                - name (str): 名前
                - size (int): ファイルサイズ（バイト）（ファイルのみ）
                - modified (str): 最終更新日時
        """
        async with aiohttp.ClientSession() as session:
            data = {
                'path': path,
                'lowerlevel': str(lowerlevel)
            }
            headers = {
                'Accept-Encoding': 'gzip'
            }
            async with session.post(f"{self._url}/getFileList", data=data, headers=headers) as response:
                if response.status == 200:
                    # レスポンスの読み込みと解凍
                    content = await response.read()
                    # RCM-GZIPヘッダーまたはContent-Encodingがgzipの場合は解凍
                    if (response.headers.get('RCM-GZIP') == 'true' or 
                        response.headers.get('Content-Encoding') == 'gzip'):
                        content = gzip.decompress(content)
                    
                    # XMLのパース（エンコーディング宣言を除去）
                    content = content.decode('utf-8').replace('<?xml version="1.0" encoding="UTF-8"?>', '')
                    root = etree.fromstring(content.strip().encode('utf-8'))
                    result = []

                    # ディレクトリの処理
                    for dir_elem in root.findall('.//directories/directory'):
                        dir_info = {
                            'type': 'directory',
                            'path': lx.xpath_to_str(dir_elem, 'path'),
                            'name': lx.xpath_to_str(dir_elem, 'name'),
                            'modified': lx.xpath_to_str(dir_elem, 'modifiedTime')
                        }
                        result.append(dir_info)

                    # ファイルの処理
                    for file_elem in root.findall('.//files/file'):
                        file_info = {
                            'type': 'file',
                            'path': lx.xpath_to_str(file_elem, 'path'),
                            'name': lx.xpath_to_str(file_elem, 'name'),
                            'size': lx.xpath_to_int(file_elem, 'bytes'),
                            'modified': lx.xpath_to_str(file_elem, 'modifiedTime')
                        }
                        result.append(file_info)

                    return result
                else:
                    raise Exception(f"Failed to get file list: {response.status}")

    async def getFileInfo(self, path: str, name: str) -> dict[str, Any] | None:
        """指定されたファイルの情報を取得します。

        Args:
            path (str): ファイルのディレクトリパス
            name (str): ファイル名

        Returns:
            dict[str, Any] | None: ファイル情報を含む辞書。ファイルが存在しない場合はNone。
            辞書には以下のキーが含まれます：
                - path (str): ディレクトリパス
                - name (str): ファイル名
                - size (int): ファイルサイズ（バイト）
                - modified (str): 最終更新時刻
        """
        params = { 'path': path, 'name': name }
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self._url}/getFileInfo", params=params) as response:
                if response.status == 200:
                    content = await response.text()
                    if not content:  # ファイルが存在しない場合は空のレスポンス
                        return None
                    
                    # XMLのパース（エンコーディング宣言を除去）
                    content = content.replace('<?xml version="1.0" encoding="UTF-8"?>', '')
                    file_elem = etree.fromstring(content.strip().encode('utf-8'))
                    if file_elem is not None and file_elem.tag=="file":
                        return {
                            'path': lx.xpath_to_str(file_elem, 'path'),
                            'name': lx.xpath_to_str(file_elem, 'name'),
                            'size': lx.xpath_to_int(file_elem, 'bytes'),
                            'modified': lx.xpath_to_str(file_elem, 'modifiedTime')
                        }
                    raise Exception(f"Failed to get file info")
                else:
                    raise Exception(f"Failed to get file info: {response.status}")

    async def createDirectory(self, path: str ) -> None:
        await self._directory( path, "create" )

    async def removeDirectory(self, path: str ) -> None:
        await self._directory( path, "delete" )

    async def _directory(self, path: str, operation: str) -> None:
        """ディレクトリの作成または削除を行います。

        Args:
            path (str): 操作対象のディレクトリパス
            operation (str): 操作種別。"create"または"delete"

        Raises:
            ValueError: 操作種別が不正な場合
            Exception: サーバーエラーが発生した場合
        """
        if operation not in ["create", "delete"]:
            raise ValueError('operation must be either "create" or "delete"')

        # リクエストボディの作成
        request_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<directory>
    <path>{path}</path>
    <operation>{operation}</operation>
</directory>"""

        async with aiohttp.ClientSession() as session:
            headers = {'Content-Type': 'application/xml'}
            async with session.post(
                f"{self._url}/directory",
                data=request_xml,
                headers=headers
            ) as response:
                if response.status != 200:
                    error_msg = await response.text()
                    raise Exception(f"Failed to {operation} directory: {error_msg}")

    async def getFile(self, file_paths: list[str]) -> list[tuple[str, bytes | str]]:
        """指定されたファイルを取得します。

        Args:
            file_paths (list[str]): 取得するファイルのパスのリスト

        Returns:
            list[tuple[str, bytes | str]]: 各ファイルの結果のリスト。
            タプルの形式：(ファイルパス, バイナリデータ | エラーメッセージ)
            - 成功時: (パス, バイナリデータ)
            - 失敗時: (パス, エラーメッセージ)

        Raises:
            Exception: サーバーエラーが発生した場合
        """
        params = []
        for path in file_paths:
            params.append(('filePath', path))

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self._url}/getFile", params=params) as response:
                if response.status not in [200, 500]:  # 500はファイル単位のエラーを含む
                    raise Exception(f"Failed to get files: {response.status}")

                # レスポンスの読み取り
                content = await response.read()
                results: list[tuple[str, bytes | str]] = []
                pos = 0

                while pos < len(content):
                    # ステータスとサイズの読み取り
                    header = content[pos:].split(b',', 2)
                    if len(header) != 3:
                        break

                    status = header[0] == b'1'  # 1:成功, 0:失敗
                    size = int(header[1])
                    pos += len(header[0]) + len(header[1]) + 2  # +2 for two commas

                    # ファイル名の読み取り
                    name_end = content.find(b'\0', pos)
                    if name_end == -1:
                        break
                    file_path = content[pos:name_end].decode('utf-8')
                    pos = name_end + 1

                    if status:
                        # 成功：バイナリデータの読み取り
                        file_data = content[pos:pos + size]
                        results.append((file_path, file_data))
                        pos += size + 1  # +1 for trailing null
                    else:
                        # 失敗：エラーメッセージの読み取り
                        error_end = content.find(b'\0', pos)
                        if error_end == -1:
                            break
                        error_msg = content[pos:error_end].decode('utf-8')
                        results.append((file_path, error_msg))
                        pos = error_end + 1

                return results

    async def touch(self, file_path: str) -> bool:
        """指定されたファイルの最終更新時刻を更新、またはファイルを新規作成します。

        Args:
            file_path (str): 対象ファイルのパス

        Returns:
            bool: 操作が成功した場合はTrue、失敗した場合はFalse

        Raises:
            Exception: サーバーエラーが発生した場合
        """
        params = {'filePath': file_path}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self._url}/touch", params=params) as response:
                if response.status == 200:
                    result = await response.text()
                    return result == "OK"
                else:
                    raise Exception(f"Failed to touch file: {response.status}")

    async def uploadFile(self, files: list[tuple[str, str | bytes]], uncompress: bool = False) -> None:
        """ファイルをサーバーにアップロードします。

        Args:
            files (list[tuple[str, str | bytes]]): アップロードするファイルのリスト。
                各タプルは (アップロード先のパス, ファイルデータ) の形式。
                ファイルデータは文字列（ファイルパス）またはバイトデータ。
            uncompress (bool, optional): gzip圧縮されたファイルを解凍するかどうか。デフォルトはFalse。

        Raises:
            ValueError: 不正なファイルパスが指定された場合
            Exception: アップロードに失敗した場合
        """
        async with aiohttp.ClientSession() as session:
            # multipart/form-dataの準備
            data = aiohttp.FormData()
            
            for dest_path, file_data in files:
                # ファイルパスの追加
                data.add_field('filePath', dest_path)
                
                # ファイルデータの追加
                if isinstance(file_data, str):
                    # ファイルパスが指定された場合
                    with open(file_data, 'rb') as f:
                        file_content = f.read()
                else:
                    # バイトデータが直接指定された場合
                    file_content = file_data
                
                data.add_field('file', file_content, filename=os.path.basename(dest_path))
            
            # 解凍オプションの追加
            if uncompress:
                data.add_field('uncompress', 'gzip')
            
            async with session.post(f"{self._url}/uploadFile", data=data) as response:
                if response.status != 200:
                    error_msg = await response.text()
                    raise Exception(f"Failed to upload files: {error_msg}")

    async def removeFile(self, file_path: str):
        """指定されたファイルを削除します。

        Args:
            file_path (str): 対象ファイルのパス

        Returns:
            bool: 操作が成功した場合はTrue、失敗した場合はFalse

        Raises:
            Exception: サーバーエラーが発生した場合
        """
        try:
            cmd = None
            msg = None
            os_name = await self.getOs()
            if os_name is not None:
                os_name = os_name.lower()
                if os_name.find('linux')>=0:
                    escpath = "'"+file_path.replace("'","'\"'\"'")+"'"
                    cmd = f"\\rm -f {file_path}"
                elif os_name.find('windows')>=0:
                    escpath = file_path
                    cmd = f"del {escpath}"
            if cmd:
                code,msg = await self.cmdExec(cmd)
                if code == 0:
                    return True
            raise Exception(msg if msg else 'OS名取得エラー')
        except Exception as e:
            print(f"failed to remove file {file_path}: {e}")

    async def cmdExec(self, command: str, *, cancel_id: str | None = None) -> tuple[int, str]:
        """サーバー上でコマンドを実行します。

        Args:
            command (str): 実行するコマンド
            cancel_id (str | None, optional): キャンセル用のID。
                このIDを使用して実行中のコマンドをキャンセルできます。

        Returns:
            tuple[int, str]: (終了コード, 標準出力) のタプル

        Raises:
            Exception: コマンド実行に失敗した場合
        """
        # リクエストボディの作成
        request_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<command>
    <cmd><![CDATA[{command}]]></cmd>{f'''
    <id>{cancel_id}</id>''' if cancel_id else ''}
</command>"""

        async with aiohttp.ClientSession() as session:
            headers = {'Content-Type': 'application/xml'}
            async with session.post(
                f"{self._url}/cmdExec",
                data=request_xml,
                headers=headers
            ) as response:
                if response.status == 200:
                    # 終了コードの取得
                    status = int(response.headers.get('cmdStatus', '-1'))
                    # 標準出力の取得
                    output = await response.text()
                    return status, output
                else:
                    raise Exception(f"Failed to execute command: {response.status}")

    async def cancelCommand(self, cancel_id: str) -> None:
        """実行中のコマンドをキャンセルします。

        Args:
            cancel_id (str): キャンセル対象のコマンドID

        Raises:
            Exception: キャンセルに失敗した場合
        """
        request_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<command>
    <cancel>{cancel_id}</cancel>
</command>"""

        async with aiohttp.ClientSession() as session:
            headers = {'Content-Type': 'application/xml'}
            async with session.post(
                f"{self._url}/cmdExec",
                data=request_xml,
                headers=headers
            ) as response:
                if response.status != 200:
                    raise Exception(f"Failed to cancel command: {response.status}")
