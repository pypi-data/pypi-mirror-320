from setuptools import setup, find_packages

setup(
    name="tos_decrator",  # 替换为实际的包名
    version="0.2",  # 初始版本号，可以根据发布情况修改
    packages=find_packages(),
    install_requires=[
        "tos"
    ],
    author="Yukun Li",
    author_email="liyukun@mathmagical.com",
    description="A simple tos decrator to download file,process and upload",
    long_description=open('README.md').read(),  # 假设 README.md 中有详细的包说明
    long_description_content_type="text/markdown",
)
