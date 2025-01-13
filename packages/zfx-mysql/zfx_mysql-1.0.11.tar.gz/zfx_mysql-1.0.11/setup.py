from setuptools import setup, find_packages

setup(
    name='zfx_mysql',
    version='1.0.11',
    packages=find_packages(),
    include_package_data=False,
    author='zengfengxiang',
    author_email='424491679@qq.com',
    description='这是一个用于mysql处理的 Python 工具库,欢迎各路大神反馈意见及提出需求。企鹅号：424491679,企鹅群：961483644',
    long_description="""
    免责声明:
    本模块是“按原样”提供的，没有任何明示或暗示的保证。在任何情况下，作者或版权持有者均不对因使用本模块而产生的任何索赔、损害或其他责任负责，无论是在合同、侵权或其他情况下。

    使用本模块即表示接受此免责声明。如果您不同意此免责声明的任何部分，请勿使用本模块。

    本模块仅供参考和学习用途，用户需自行承担使用本模块的风险。作者对因使用本模块而造成的任何直接或间接损害不承担任何责任。

    作者保留随时更新本免责声明的权利，恕不另行通知。最新版本的免责声明将在模块的最新版本中提供。
    """,
    url='',
    install_requires=[
        'mysql-connector-python',
        'mysql.connector',
        # 添加其他依赖库
    ],
)
