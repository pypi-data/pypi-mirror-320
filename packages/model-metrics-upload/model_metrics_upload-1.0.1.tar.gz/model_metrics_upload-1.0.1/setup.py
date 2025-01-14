from setuptools import setup, find_packages

setup(
    name="model_metrics_upload",                # 包的名称，pip安装时用到
    version="1.0.1",                  # 版本号
    author="admin",               # 作者名称
    author_email="111@google.com",  # 作者邮箱
    description="upload model params to target address", # 简短描述
    long_description=open('README.md').read(), # 从 README.md 中读取长描述
    long_description_content_type='text/markdown', # 指定 README 文件的格式
    url="", # 项目主页
    packages=find_packages(),         # 自动发现包
    classifiers=[                     # 其他元数据
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',          # 指定 Python 版本要求
    install_requires=[                # 依赖的库
        "requests",
    ],
)