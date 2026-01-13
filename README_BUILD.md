# 极智考典 - 打包指南

## 文件说明

1. **`build_user_version.bat`** - Windows批处理打包脚本
2. **`build_user_version.py`** - Python打包脚本（跨平台）
3. **`user_version/`** - 用户版本源代码目录

## 使用方法

### 方法1：使用批处理脚本（Windows推荐）

```bash
# 在项目根目录运行
build_user_version.bat
```

### 方法2：使用Python脚本

```bash
# 1. 进入 user_version 目录
cd user_version

# 2. 运行打包脚本
python ../build_user_version.py
```

### 方法3：手动打包

```bash
# 1. 进入 user_version 目录
cd user_version

# 2. 安装依赖
pip install -r requirements.txt

# 3. 执行打包命令
pyinstaller --onefile --windowed --name="极智考典" --add-data="data;data" --add-data="ui;ui" --add-data="core;core" main.py
```

## 打包配置说明

### 基本参数
- `--onefile`：打包成单个exe文件
- `--windowed`：窗口程序（不显示控制台）
- `--name="极智考典"`：输出文件名
- `--clean`：清理临时文件
- `--noconfirm`：不确认覆盖

### 数据文件包含
- `--add-data="data;data"`：包含data目录（题目数据）
- `--add-data="ui;ui"`：包含ui目录（用户界面）
- `--add-data="core;core"`：包含core目录（核心功能）

### 安全排除模块
以下管理工具模块被排除，确保用户版本安全：
- `admin`：管理工具
- `generate_codes`：激活码生成
- `encrypt_exams`：试卷加密
- `decrypt_exams`：试卷解密
- `import_papers`：试卷导入
- `fix_activation_data`：激活数据修复
- `manage_image_mapping`：图片映射管理

### 隐藏导入
- PyQt5相关模块
- crypto加密模块

## 输出文件

打包完成后，生成的文件位于：
- `user_version/dist/极智考典.exe` - 主程序文件
- `user_version/build/` - 临时构建文件（可删除）
- `user_version/极智考典.spec` - PyInstaller配置文件（可删除）

## 依赖要求

### Python包
- PyQt5>=5.15.0
- pycryptodome>=3.15.0
- pyinstaller（打包工具）

### 系统要求
- Windows 7/8/10/11
- Python 3.7+
- 足够的磁盘空间（打包过程需要约500MB临时空间）

## 常见问题

### 1. 打包失败：模块找不到
**解决方法**：添加对应的 `--hidden-import` 参数

### 2. exe文件太大
**原因**：PyQt5库较大，这是正常现象
**预期大小**：50-100MB

### 3. 运行时缺少DLL
**解决方法**：确保在Windows系统上运行，或使用 `--add-binary` 参数包含必要的DLL

### 4. 激活功能不正常
**检查**：确保 `core/activation.py` 和 `ui/activation_dialog.py` 已正确包含

## 发布流程

1. **打包测试**：运行打包脚本生成exe
2. **功能测试**：测试exe文件的所有功能
3. **激活测试**：测试激活码验证功能
4. **分发准备**：将exe文件复制到发布目录
5. **生成激活码**：使用 `admin/activation_admin.py` 生成用户激活码

## 注意事项

1. **不要修改 `user_version` 目录中的 `main.py`**，它已经包含激活验证功能
2. **确保 `data` 目录包含最新的题目数据**
3. **打包前关闭所有Python相关程序**，避免文件占用
4. **定期清理 `build` 目录**，释放磁盘空间

## 技术支持

如有问题，请检查：
1. Python和pip是否正确安装
2. 依赖包是否安装成功
3. 是否在正确的目录运行脚本
4. 系统是否有足够的权限和磁盘空间