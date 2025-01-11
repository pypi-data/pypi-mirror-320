from setuptools import setup, find_packages

setup(
    name='aivagent',
    version='0.2.2', # 2024.8.4
    packages= ["aivagent"], # find_packages(),
    install_requires=[
        # 任何依赖项都在这里列出
    ],
    package_data={
        'aivagent': ['*.pyd'],  # 包含 my_package 目录下的所有 .pyd 文件
    },
    author='aiv.store',
    author_email='76881573@qq.com',
    description='Aiv Agent',
    python_requires='>=3.9',
    # long_description=open('./readme.rts').read(),    #显示在 pypi.org 首页的项目介绍里 2024.6
    license='MIT',
    keywords='Aiv Agent',
    url='https://www.aiv.store'
)