from setuptools import setup

setup(
    name="nonebot-plugin-llm-jade",
    version="0.0.6",
    packages=["nonebot_plugin_llm_jade"],
    install_requires=["nonebot2>=2.2.0","httpx","nonebot-adapter-onebot","PyJWT"],
    description="基于 LLM 的玉检测插件",
    author="NightWind",
    author_email="2125714976@qq.com",
    url="https://github.com/XTxiaoting14332/nonebot-plugin-llm-jade",
)
