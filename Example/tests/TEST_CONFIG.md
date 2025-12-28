# 测试配置说明

## 当前测试参数配置

根据用户指定，测试使用以下参数：

### 已配置的参数

- **project_name**: `ai_test`
- **version**: `P85`
- **flow**: `pv_calibre.drc`
- **foundry**: `TEST_FOUNDRY`
- **node**: `TEST_NODE`
- **user**: `test_user`（使用当前的 user）

### 默认参数（可修改）

- **block**: `block1`（默认值，可以修改）
- **branch**: `main`（默认分支，init 时使用；branch 命令可以创建其他分支）

## 测试路径结构

测试会在临时目录中创建以下结构：

```
{temp_base}/
└── ai_test/                    # project_name
    └── P85/                    # version
        ├── .edp_version        # 版本信息文件
        └── block1/             # block
            └── test_user/       # user
                └── main/       # branch (init 时创建)
                    └── ...     # 项目文件
```

## Flow 配置路径

测试会创建以下 flow 配置（使用正确的目录结构）：

```
{edp_center_path}/
├── flow/
│   └── initialize/              # 正确的 flow 目录结构
│       └── TEST_FOUNDRY/        # foundry
│           └── TEST_NODE/       # node
│               └── common/      # common 配置（所有项目共享）
│                   └── cmds/
│                       └── pv_calibre/
│                           └── steps/
│                               └── calibre_drc.tcl
└── config/
    └── TEST_FOUNDRY/            # foundry
        └── TEST_NODE/           # node
            └── common/           # common 配置（所有项目共享）
                └── pv_calibre/
                    ├── dependency.yaml
                    └── config.yaml
```

**注意**：
- Flow 脚本应该在 `flow/initialize/<FOUNDRY>/<NODE>/common/cmds/<flow_name>/steps/` 下
- 不应该直接在 `flow/pv_calibre/` 下创建（这是错误的目录结构）
- 可以使用已有的目录结构，比如 `flow/initialize/SAMSUNG/S8/common/cmds/pv_calibre/steps/` 中已经有文件

## 配置说明

### dependency.yaml

```yaml
pv_calibre:
  dependency:
    FP_MODE:
      - drc:
          in: []
          out: ["drc.pass"]
          cmd: "calibre_drc.tcl"
```

### config.yaml

```yaml
pv_calibre:
  drc:
    lsf: 0          # 本地执行，非 LSF
    tool_opt: "bash"
    cmd: "echo 'DRC check'"
```

## 修改测试参数

如果需要修改测试参数，编辑 `test_full_workflow.py` 中的 `setUpClass` 方法：

```python
@classmethod
def setUpClass(cls):
    """测试类初始化"""
    cls.edp_center_path = find_edp_center_path_helper()
    cls.temp_base = Path(tempfile.mkdtemp(prefix="edp_test_"))
    # 修改以下参数
    cls.test_project = "ai_test"        # 项目名称
    cls.test_version = "P85"            # 版本
    cls.test_block = "block1"           # 块名称
    cls.test_user = "test_user"         # 用户名称
    cls.test_branch = "main"             # 分支名称
    cls.test_foundry = "TEST_FOUNDRY"   # 代工厂
    cls.test_node = "TEST_NODE"         # 工艺节点
    cls.test_flow = "pv_calibre.drc"    # Flow 名称
```

## 运行测试

```bash
cd EDP_AI
python Example/tests/test_full_workflow.py
```

或运行所有测试：

```bash
cd EDP_AI
python Example/tests/run_tests.py
```

