### Repositories 目录说明

#### 目录结构
```
repositories/
├── readme.md
├── __init__.py
├── base.py
├── account.py
├── category.py
├── tag.py
├── transaction.py
├── transaction_tag.py
```
---

#### 方法规范
- `base.py` 定义基础仓库类，包含通用的CRUD方法。方法 model 形参为 SQLModel 模型类，返回值依旧为 SQLModel 类型。
- ~~模型类要求重写基础仓库类的方法，将形参类型更改为 schema 模型，经类型转换为 SQLModel 模型后调用基础仓库类的方法。返回值类型同样为 SQLModel 模型类。~~
- 具体模型仓库方法正式更改为必须**以 SQLModel 模型类为形参和返回值**类型，SQLModel 与 schema 模型的转换由服务层负责。
- 仓库层不直接操作中间表模型，服务层通过 append 和 remove 方法进行绑定和解绑操作。
---

#### 开发日志
- 2026-04-29:
  - 初始版本，定义了仓库层的目录结构和方法规范。
  - 记得中间表由服务层通过`append`和`remove`方法进行绑定和解绑：
  ```
  transaction.tags.append(tag)   # 绑定标签
  transaction.tags.remove(tag)   # 解绑标签
  session.add(transaction)
  ```
  -