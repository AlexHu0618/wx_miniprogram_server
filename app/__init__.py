from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config


# define but do not initialize
db = SQLAlchemy()
async_mode = None


# create factory function
def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])  # load configuration
    config[config_name].init_app(app)

    db.init_app(app=app)

    # register the route blueprint to the app
    from .main import main as main_blueprint
    from .api01 import api_bp as api_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(api_blueprint)

    return app


STATE_CODE = {'200': {'code': 200, 'message': 'successful'},
              '201': {'code': 201, 'message': 'successful'},
              '202': {'code': 202, 'message': 'accessed and handle but unfinished'},
              '203': {'code': 203, 'message': 'accessed and handle error'},
              '204': {'code': 204, 'message': 'accessed and return none'},
              '205': {'code': 205, 'message': 'successful'},
              '206': {'code': 206, 'message': 'sub successful'},
              '207': {'code': 207, 'message': 'the resource has been existed'},
              '400': {'code': 400, 'message': 'request error, wrong param'},
              '407': {'code': 407, 'message': 'request error, please login again'},
              '409': {'code': 409, 'message': 'DB error'},
              '600': {'code': 600, 'message': 'have not subscribe the offical account'}}


# 1xx：信息响应类，表示接收到请求并且继续处理
# 2xx：处理成功响应类，表示动作被成功接收、理解和接受
# 3xx：重定向响应类，为了完成指定的动作，必须接受进一步处理
# 4xx：客户端错误，客户请求包含语法错误或者是不能正确执行
# 5xx：服务端错误，服务器不能正确执行一个正确的请求
#
# 100——客户必须继续发出请求
# 101——客户要求服务器根据请求转换HTTP协议版本
#
# 200——交易成功
# 201——提示知道新文件的URL
# 202——接受和处理、但处理未完成
# 203——返回信息不确定或不完整
# 204——请求收到，但返回信息为空
# 205——服务器完成了请求，用户代理必须复位当前已经浏览过的文件
# 206——服务器已经完成了部分用户的GET请求
# 207——接受和处理,但已存在重复资源,无法完成请求
#
# 300——请求的资源可在多处得到
# 301——删除请求数据
# 302——在其他地址发现了请求数据
# 303——建议客户访问其他URL或访问方式
# 304——客户端已经执行了GET，但文件未变化
# 305——请求的资源必须从服务器指定的地址得到
# 306——前一版本HTTP中使用的代码，现行版本中不再使用
# 307——申明请求的资源临时性删除
#
# 400——错误请求，如语法错误
# 401——请求授权失败
# 402——保留有效ChargeTo头响应
# 403——请求不允许
# 404——没有发现文件、查询或URl
# 405——用户在Request-Line字段定义的方法不允许
# 406——根据用户发送的Accept拖，请求资源不可访问
# 407——类似401，用户必须首先在代理服务器上得到授权
# 408——客户端没有在用户指定的饿时间内完成请求
# 409——对当前资源状态，请求不能完成
# 410——服务器上不再有此资源且无进一步的参考地址
# 411——服务器拒绝用户定义的Content-Length属性请求
# 412——一个或多个请求头字段在当前请求中错误
# 413——请求的资源大于服务器允许的大小
# 414——请求的资源URL长于服务器允许的长度
# 415——请求资源不支持请求项目格式
# 416——请求中包含Range请求头字段，在当前请求资源范围内没有range指示值，请求也不包含If-Range请求头字段
# 417——服务器不满足请求Expect头字段指定的期望值，如果是代理服务器，可能是下一级服务器不能满足请求
#
# 500——服务器产生内部错误
# 501——服务器不支持请求的函数
# 502——服务器暂时不可用，有时是为了防止发生系统过载
# 503——服务器过载或暂停维修
# 504——关口过载，服务器使用另一个关口或服务来响应用户，等待时间设定值较长
# 505——服务器不支持或拒绝支请求头中指定的HTTP版本
#
# 600——用户尚未关注公众号