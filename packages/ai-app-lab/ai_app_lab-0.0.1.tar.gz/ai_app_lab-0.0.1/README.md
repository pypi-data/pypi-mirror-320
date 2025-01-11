# ark-python-sdk

本仓库主要用于方舟编排的python sdk开发，包含了python sdk的开发工具、sdk的代码、sdk的测试代码、sdk的文档、sdk的发布脚本等。

## 目录结构
```
├── Makefile              # 编译/安装/lint等脚本
├── OWNERS
├── README.md
├── ark
│   ├── __init__.py
│   ├── cli         # 命令行工具脚本，主要用于初始化project，推送镜像等
│   ├── component   # 基于core包组成的不同插件/模型上层调用
│   ├── core        # 核心数据结构抽象/client包/装饰器部分
│   └── telemetry   # 可观测性
├── build.sh              # scm编译脚本
├── docker                # dockerfile
├── examples              # sdk使用示例
│   ├── action_call      # function call
│   ├── assistant_client # 调用智能体
│   ├── custom
│   ├── llm
│   ├── rag     # 知识库
│   ├── rag_ry
│   ├── search  # 联网
│   └── video
├── poetry.lock
├── pyproject.toml      # 项目依赖包管理
├── scripts             # ci/cd相关脚本
└── tests               # 单元测试/集成测试/e2e测试
    ├── e2e             # e2e测试
    ├── integration     # 集成测试
    └── ut              # 单元测试

```

## 开发环境

* 安装poetry

```shell
cd sdk/src
make poetry_install
```

* poetry安装依赖

```shell
make install

# 带cli工具相关的依赖安装
make install_with_cli
```

* 虚拟环境创建

```shell
poetry shell
```

## 测试

[本地测试文档](https://bytedance.larkoffice.com/wiki/T4Cvwy8SCiRi4rkDxxfca4pYnbz)

## 发布

* 本地打包whl

```shell
make build
```

* 流水线打包并发布

[发布流水线](https://bytecycle.bytedance.net/space/machinelearning/module/pipeline/info/14463514)

* 开白授权sdk下载权限

[tos授权](https://bytecycle.bytedance.net/space/machinelearning/module/pipeline/info/14464018)

[sdk下载方法](https://bytedance.larkoffice.com/wiki/EelBw62BeiXchwkCoc4cIRADndg)