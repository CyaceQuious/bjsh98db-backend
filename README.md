# 大体协数据库-backend


## API 文档

https://jwegtxl61kb.feishu.cn/wiki/DE42wHWeyigsttk5uQ4ctOBsnvh

以下是在本地部署的向导。

## 环境配置

使用 `conda` 创建一个新的虚拟环境：

```bash
conda env create -f environment.yaml
conda activate backend
```

### 安装PostgreSQL数据库

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

### 配置 PostgreSQL 数据库和用户：

登录 PostgreSQL：

```bash
sudo -u postgres psql
```

创建数据库：

```sql
CREATE DATABASE meetresult;
```

创建数据库用户并设置密码：

```sql
CREATE USER bjsh WITH PASSWORD '111';
```

为数据库授予权限：

```sql
GRANT ALL PRIVILEGES ON DATABASE meetresult TO bjsh;
```

退出 PostgreSQL：

```sql
\q
```

你现在可以使用用户名 bjsh 和密码 111 来连接到 meetresult 数据库。

### 检查 PostgreSQL 服务是否正常运行：

在终端运行以下命令，确保 PostgreSQL 服务正在运行：

```bash
sudo systemctl status postgresql
```

如果 PostgreSQL 没有运行，可以通过以下命令启动它：

```bash
sudo systemctl start postgresql
```

## 运行

### 建库

```bash
python manage.py makemigrations
python manage.py migrate    
```

### 恢复数据库中的数据

```bash
python manage.py flush
python manage.py makemigrations Query
python manage.py migrate
python manage.py load_results
```

可能下面这样也行？

```bash
psql -U bjsh -d meetresult -f meetresult_backup.sql
```

### 创建系统管理员
```bash
python manage.py create_system_admin
```

### 导入运动员
```bash
python manage.py load_athlete
```

### 启动

```bash
python manage.py runserver
```