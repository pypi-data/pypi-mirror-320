from setuptools import setup, find_packages

setup(
    name='crystalflow',  # 包名
    version='0.0.9',  # 版本
    description="XRD Enhanced Crystal Graph Dataloader",  # 包简介
    long_description=open('README.md', encoding='utf-8').read(),  # 读取文件中介绍包的详细内容
    long_description_content_type='text/markdown',  # 指定详细描述的内容格式为 Markdown
    include_package_data=True,  # 是否允许上传资源文件
    author='Cao Bin',  # 作者
    author_email='binjacobcao@gmail.com',  # 作者邮件
    maintainer='Cao Bin',  # 维护者
    maintainer_email='binjacobcao@gmail.com',  # 维护者邮件
    license='MIT',  # 协议
    url='https://github.com/Bin-Cao/CrystalFlow',  # GitHub 或者自己的网站地址
    packages=find_packages(include=['crystalflow', 'crystalflow.*']),
    classifiers=[
        'Development Status :: 3 - Alpha',  # 当前开发阶段
        'Intended Audience :: Developers',  # 目标受众
        'Topic :: Software Development :: Build Tools',  # 软件主题分类
        'License :: OSI Approved :: MIT License',  # 授权协议
        'Programming Language :: Python :: 3',  # 支持的 Python 版本
        'Programming Language :: Python :: 3.7',  # 进一步声明支持的具体版本
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.7',  # 设置最低 Python 版本要求（更新为更现代版本）
    install_requires=[
        'numpy>=1.21.0',  # 添加版本限制，避免兼容性问题
        'matplotlib>=3.4.0'
    ],  # 安装所需要的库
    entry_points={
        'console_scripts': [
            # 设置命令行工具，需填写具体功能
            # 例如 'crystalflow-cli=crystalflow.cli:main'
        ],
    },  # 如果不使用命令行工具可以注释掉这部分
)
