import asyncio
import aiohttp
import json
import yaml
import threading
import time
import datetime
import os
import csv

FUNCTION_ID_RTN_STRATEGY_LOG = 11004

gstop_event = asyncio.Event()


class WebSocketClient:
    def __init__(self, uri, user, passwd, strategy_name, strategy_param):
        self.uri = uri
        self.user = user
        self.passwd = passwd
        self.strategy_name = strategy_name
        self.strategy_param = strategy_param
        self.session = None
        self.websocket = None
        self.connected = False
        self.strategy_id = -1
        self.select_strategy = ""
        self.results = {"position": [], "trades": []}
        self.condition = threading.Condition()
        self.lock = asyncio.Lock()  # 创建一个锁
        self.ready = False
        self._isFinish = False

        self.func_map = {
            10001: self.handle_login_response,
            10005: self.handle_create_strategy_response,
            10020: self.handle_rtn_strategy_status,
            12029: self.handle_query_trade_list,
            11004: self.handle_rtn_strategy_log,
            12030: self.handle_query_position_list
        }

        # 日志级别映射ƒ
        self.log_levels = {
            0: 'Verbose',
            1: 'Debug',
            2: 'Info',
            3: 'Warn',
            4: 'Error',
            5: 'Fatal'
        }

    async def update_positions(self, new_data):
        # 处理接收到的新数据并更新结果
        for item in new_data:
            self.results["position"].extend(item['positionList'])
            # position_list = item['positionList']
            # date_dict = {}
            # for i in range(len(position_list)):
            #     # 相同交易日
            #     position = position_list[i]
            #     date_dict[position['tradingDay']].append(position)

            # for key, value in date_dict.items():
            #     print(f"date key:{key}")

    async def isFinish(self):
        async with self.lock:  # 加锁以确保线程安全
            return self._isFinish

    async def setFinish(self, value):
        async with self.lock:  # 加锁以确保线程安全
            self._isFinish = value

    def wait_for_condition(self):
        with self.condition:
            while not self.ready:
                self.condition.wait()

    def set_condition(self):
        time.sleep(2)  # 模拟一些工作
        with self.condition:
            self.ready = True
            self.condition.notify_all()  # 通知所有等待的线程

    async def connect(self):
        """建立 WebSocket 连接并保持活动状态"""
        self.session = aiohttp.ClientSession()
        try:
            self.websocket = await self.session.ws_connect(self.uri)
            self.connected = True

            # 登录请求
            await self.login_request()

            # 监听消息
            await self.listen()

        except Exception as e:
            print(f"连接失败: {e}")
            await self.close_session()  # 确保关闭会话
            await self.reconnect()

    async def reconnect(self):
        """尝试重新连接"""
        print("尝试重新连接...")
        await asyncio.sleep(1)  # 等待 1 秒后重新连接
        await self.connect()

    async def listen(self):
        """监听服务器消息"""
        try:
            async for msg in self.websocket:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    await self.process_response(msg.data)
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    print(f"WebSocket 错误: {self.websocket.exception()}")
                    break
        except Exception as e:
            print(f"监听时发生异常: {e}")
        finally:
            self.connected = False

    async def process_response(self, response):
        """处理接收到的消息"""
        try:
            data = json.loads(response)
            funcion_id = data.get("funcionId")
            err_id = data.get("errId")
            err_msg = data.get("errMsg")
            response_data = data.get("data")

            if err_id != 0:
                print(f"错误代码 {err_id}: {err_msg}")
                return

            # 处理对应的 funcionId
            if funcion_id in self.func_map:
                await self.func_map[funcion_id](response_data)
            else:
                print(f"未找到处理函数 funcionId: {funcion_id}")

        except json.JSONDecodeError:
            print("接收到的消息不是有效的 JSON 格式")

    async def send_request(self, request_data):
        """发送请求"""
        if self.connected:
            await self.websocket.send_str(json.dumps(request_data))
        else:
            print("WebSocket 尚未连接，无法发送请求")

    async def sub_strategy_log(self):
        request_data = {
            "funcionId": 12014,
            "finished": True,
            "dataType": 1,
            "requestId": 1,
            "errId": 0,
            "errMsg": "",
            "data": [
                {
                    "userId": f"{self.user}"
                }
            ]
        }
        await self.send_request(request_data)

    async def login_request(self):
        """发送登录请求"""
        request_data = {
            "funcionId": 10001,
            "finished": True,
            "dataType": 1,
            "requestId": 1,
            "errId": 0,
            "errMsg": "",
            "data": [
                {
                    "userName": self.user,
                    "passWord": self.passwd
                }
            ]
        }
        await self.send_request(request_data)

    async def handle_login_response(self, data):
        """处理登录响应"""
        if isinstance(data, list) and data:
            response_data = data[0]
            if response_data.get("msg") == "welcome":
                print("登录成功！")
                await self.sub_strategy_log()

                await self.create_strategy()

            else:
                print("登录失败！")
        else:
            print("无效的响应数据格式")

    async def convert_to_json(self, data):
        """将 Python 对象转换为 JSON 字符串"""
        return json.dumps(data, ensure_ascii=False, indent=4)

    async def create_strategy(self):
        """创建策略请求"""
        param = await self.convert_to_json(self.strategy_param)
        request = {
            "funcionId": 10005,
            "finished": True,
            "dataType": 1,
            "requestId": 2,
            "errId": 0,
            "errMsg": "",
            "data": [
                {
                    "soName": self.strategy_name,
                    "param": param,
                    "operationType": 1,
                    "strategyId": 0,
                    "strategyType": 2,
                    "frequencyType": 1,
                    "status": 0,
                    "userId": self.user
                }
            ]
        }
        await self.send_request(request)

    async def query_trade_list(self):

        request_data = {
            "funcionId": 12029,
            "finished": True,
            "dataType": 1,
            "requestId": 1,
            "errId": 0,
            "errMsg": "",
            "data": [{
                "strategyId": self.select_strategy["strategyId"]
            }]
        }
        await self.send_request(request_data)

    async def query_position_list(self):

        request_data = {
            "funcionId": 12030,
            "finished": True,
            "dataType": 1,
            "requestId": 1,
            "errId": 0,
            "errMsg": "",
            "data": [{
                "strategyId": self.select_strategy["strategyId"]
            }]
        }
        await self.send_request(request_data)

    async def start_strategy(self):
        """ 开始策略请求 """
        param = await self.convert_to_json(self.strategy_param)
        request = {
            "funcionId": 10005,
            "finished": True,
            "dataType": 1,
            "requestId": 2,
            "errId": 0,
            "errMsg": "",
            "data": [
                {
                    "soName": self.strategy_name,
                    "param": self.select_strategy["param"],
                    "operationType": 5,
                    "strategyId": self.select_strategy["strategyId"],
                    "strategyType": 2,
                    "frequencyType": 1,
                    "status": self.select_strategy["status"],
                    "userId": self.user
                }
            ]
        }

        await self.send_request(request)

    async def handle_create_strategy_response(self, data):
        """处理创建策略响应"""
        # print(f"处理创建策略响应: {data}")
        # 过滤出 soName 为 self.strategy_name 的对象

        filtered_data = [item for item in data if item['soName'] == self.strategy_name]

        # 如果有匹配的对象，则找到 strategyid 最大的对象
        if filtered_data:
            self.select_strategy = max(filtered_data, key=lambda x: x['strategyId'])

            if self.select_strategy["status"] == 2:
                await self.start_strategy()
                self.strategy_id = int(self.select_strategy["strategyId"])
        else:
            print("没有找到匹配的对象")

    async def close_session(self):
        """关闭客户端会话"""
        try:
            if self.websocket and not self.websocket.closed:
                await self.websocket.close()
            if self.session and not self.session.closed:
                await self.session.close()
                self.session = None
            print("客户端会话已关闭")
        except Exception as e:
            print(f"关闭会话时发生错误: {e}")

    async def handle_rtn_strategy_status(self, data):
        filtered_data = [item for item in data if item['strategyId'] == self.strategy_id]
        if filtered_data:
            self.select_strategy = filtered_data[0]

            if self.select_strategy["status"] == 6:
                await self.query_trade_list()

    # 秒级时间戳转换
    def convert_millisecond_time_stamp(self, timestamp):
        datetime_str = ''
        datetime_str = datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S.%f")
        return datetime_str

    async def handle_query_trade_list(self, data):
        for item in data:
            trade_list = item["tradeList"]
            # 处理成交字段信息
            for i in range(len(trade_list)):
                timestamp = trade_list[i]["exchangeTradeTime"] / 1000.0  # 毫秒转成秒
                trade_list[i]["exchangeTradeTime"] = self.convert_millisecond_time_stamp(timestamp)
            self.results["trades"] = trade_list

        await self.query_position_list()

    async def handle_rtn_strategy_log(self, data):
        param = self.strategy_param
        log_file_name = self.strategy_name.split(".")[0] + str(self.strategy_id) + ".log"
        log_file_path = os.path.join(param["env"]["log_path"], log_file_name)  # 替换为实际的日志文件路径
        log_to_terminal = param["env"]["stdout"]

        # 如果日志文件所在目录不存在，则创建目录
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        file_handler = open(log_file_path, 'a', encoding='utf-8')  # 以追加模式打开文件

        for entry in data:
            if "logLevel" not in entry:
                continue

            log_level = entry['logLevel']
            log_message = entry['logMessage']
            log_time = entry['logTime']

            # 转换 logTime 为可视化时间
            # 假设 logTime 是以微秒为单位的时间戳
            readable_time = datetime.datetime.fromtimestamp(log_time / 1_000_000).strftime('%Y-%m-%d %H:%M:%S')

            # 将日志信息写入到日志文件
            file_handler.write(f"时间: {readable_time}\n")
            file_handler.write(f"日志级别: {self.log_levels.get(log_level, 'Unknown')}\n")
            file_handler.write("日志信息:\n")
            file_handler.write(log_message.strip() + "\n\n")

            # 打印格式化的日志信息
            if log_to_terminal == "yes":
                print(f"时间: {readable_time}")
                print(f"日志级别: {self.log_levels.get(log_level, 'Unknown')}")
                print("日志信息:")
                print(log_message.strip())  # 去除首尾空白

        if file_handler:
            file_handler.close()

    async def save_results(self, config):
        """
        保存结果到CSV文件
        :param config: 配置文件路径
        """
        try:
            # 读取配置文件
            with open(config, 'r', encoding='utf-8') as file:
                config_data = yaml.safe_load(file)

            # 确保结果中有数据
            if not self.results.get("trades") or not self.results.get("position"):
                print("没有可保存的结果数据")
                return

            # 构建保存路径
            strategy_id = str(self.results["trades"][0]["strategyId"])
            result_dir = config_data["env"].get("result_path", "results")

            # 保存持仓数据
            await self._save_positions(result_dir, strategy_id)

            # 保存交易数据
            await self._save_trades(result_dir, strategy_id)

        except Exception as e:
            print(f"保存结果失败: {e}")
            raise

    async def _save_positions(self, result_dir, strategy_id):
        """保存持仓数据"""
        try:
            positions = self.results.get("position", [])
            if not positions:
                return

            csv_file_path = os.path.join(result_dir, f"{strategy_id}_positions.csv")
            os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)

            with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
                # 获取表头
                headers = list(positions[0].keys())
                writer = csv.DictWriter(csvfile, fieldnames=headers)

                # 写入表头
                csvfile.write(','.join(headers) + '\n')

                # 写入数据
                for position in positions:
                    csvfile.write(','.join(str(position[header]) for header in headers) + '\n')
        except Exception as e:
            print(f"保存持仓数据失败: {e}")
            raise

    async def _save_trades(self, result_dir, strategy_id):
        """保存交易数据"""
        try:
            trades = self.results.get("trades", [])
            if not trades:
                return

            csv_file_path = os.path.join(result_dir, f"{strategy_id}_trades.csv")
            os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)

            with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
                headers = list(trades[0].keys())
                writer = csv.DictWriter(csvfile, fieldnames=headers)

                csvfile.write(','.join(headers) + '\n')

                for trade in trades:
                    csvfile.write(','.join(str(trade[header]) for header in headers) + '\n')
        except Exception as e:
            print(f"保存交易数据失败: {e}")
            raise

    async def handle_query_position_list(self, data):
        # print(f"处理策略持仓推送: ", data)
        await self.update_positions(data)
        # self.results["position"] = data
        gstop_event.set()
        self.set_condition()
        await self.setFinish(True)


uri = ""
user = ""
passwd = ""
strategy_name = ""
strategy_param = ""

gclient = WebSocketClient("", "", "", "", "")


def read_yaml_file(filepath):
    """读取 YAML 文件"""
    with open(filepath, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)


async def run_func(config):
    """运行函数，读取配置并执行相关逻辑"""
    try:
        config_data = read_yaml_file(config)
        env_config = config_data.get("env", {})
        uri = env_config.get("uri")
        user = env_config.get("user")
        passwd = env_config.get("passwd")
        strategy_name = env_config.get("pystrategy")
        strategy_param = config_data

        global gclient
        gclient = WebSocketClient(uri, user, passwd, strategy_name, strategy_param)
        await gclient.connect()
    except FileNotFoundError:
        print(f"文件 {config} 不存在！")
    except yaml.YAMLError as e:
        print("解析 YAML 文件时出错:", e)


async def monitor_condition():
    global gclient
    while True:
        # 检查 gclient.isFinish() 的返回值
        if await gclient.isFinish():
            print("Condition met, stopping the execution.")
            gstop_event.set()  # 设置事件，通知 run_func 停止
            break  # 退出循环
        await asyncio.sleep(0.5)  # 每 0.5 秒检查一次


async def run_strategy(config):
    global gclient
    try:
        # 创建任务
        task = asyncio.create_task(run_func(config))
        monitor_task = asyncio.create_task(monitor_condition())

        # 等待任务完成或条件满足
        done, pending = await asyncio.wait(
            [task, monitor_task],
            return_when=asyncio.FIRST_COMPLETED
        )

        # 如果条件满足，取消任务
        if gstop_event.is_set():
            # 取消未完成的任务
            for t in pending:
                t.cancel()
            # 等待取消完成
            await asyncio.gather(*pending, return_exceptions=True)

            # 保存结果
            if gclient:
                await gclient.save_results(config)

    except asyncio.CancelledError:
        print("run_func was cancelled.")
    finally:
        # 确保关闭 session
        if gclient and gclient.session:
            await gclient.close_session()


def run_unitrade(config):
    global gclient
    try:
        asyncio.run(run_strategy(config))
        gclient.wait_for_condition()

        return gclient.results
    finally:
        # 清理全局变量
        if gclient:
            gclient = None
