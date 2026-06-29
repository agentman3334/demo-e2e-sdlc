# PRD: Project Management System (PMS)

## 1. 需求背景

团队在项目协作中缺乏统一的管理工具，任务分配依赖口头沟通和电子表格，导致进度追踪困难、职责不清、信息遗漏频发。随着团队规模扩大，急需一套自研的轻量级项目管理系统，实现从用户认证、项目创建、任务看板到数据看板的全流程数字化管理。

本系统采用前后端分离架构：前端基于 React 18 + Vite + Ant Design 5，后端基于 FastAPI + SQLAlchemy 2.0 (async) + PostgreSQL 15，通过 JWT 实现认证，最终以 Docker Compose 方式部署至华为云 ECS。

## 2. 目标与价值

**目标：**
- 实现完整的用户注册/登录认证体系（JWT）
- 实现项目 CRUD 及团队成员管理
- 实现 Kanban 风格任务看板（拖拽排序）
- 实现数据看板（进度追踪 + 分析图表）
- 实现基于角色的访问控制（Admin / Project Manager / Member）
- 建立完整的 CI/CD 流水线（GitHub Actions → JFrog Artifactory → SonarCloud）
- 容器化部署至华为云 ECS

**价值：**
- 统一团队协作入口，减少信息碎片化
- 实时可视化项目进度，提升管理透明度
- 角色权限控制保障数据安全
- 自动化流水线保障交付质量与可追溯性

## 3. 名词解释/角色说明

- **Admin（管理员）**：拥有系统全部权限，可管理所有项目和用户
- **Project Manager（项目经理）**：可创建项目、分配任务、管理项目成员
- **Member（成员）**：可查看所属项目、更新自己负责的任务状态
- **Kanban Board（看板）**：按状态列（To Do / In Progress / Done）展示任务的可视化面板
- **JWT（JSON Web Token）**：无状态认证令牌，用于前后端鉴权
- **JFrog Artifactory**：制品仓库，存储构建产物并执行 Xray 安全扫描
- **SonarCloud**：代码质量与安全扫描平台

## 4. 适用范围

- 适用：Web 端项目管理系统的完整 MVP
- 适用：Docker 容器化部署（本地开发 + 华为云 ECS 生产环境）
- 适用：GitHub Actions CI/CD 全流程
- 不适用：移动端 App
- 不适用：实时通知（WebSocket）
- 不适用：第三方 OAuth 登录

## 5. 非目标/范围外说明

- 不包含移动端适配（响应式布局为可选优化）
- 不包含邮件/推送通知系统
- 不包含第三方集成（Slack、Jira 等）
- 不包含文件上传/附件功能
- 不包含多语言国际化（i18n）
- 不包含数据导出（CSV/PDF）

## 6. 功能需求

### 认证模块
- FR-1: 系统必须提供用户注册接口，接收 email、username、password，密码使用 bcrypt 加密存储
- FR-2: 系统必须提供用户登录接口，验证凭据后返回 JWT access token（有效期 30 分钟）
- FR-3: 前端必须提供登录页面（LoginPage），包含 email + password 表单和提交按钮
- FR-4: 前端必须提供注册页面（RegisterPage），包含 email + username + password + confirm password 表单
- FR-5: 前端必须在 Axios 请求拦截器中自动附加 Authorization: Bearer <token> 头
- FR-6: 前端必须在 token 过期或无效时自动跳转至登录页

### 项目管理模块
- FR-7: 系统必须提供项目创建接口，接收 name、description、owner_id
- FR-8: 系统必须提供项目列表查询接口，支持分页（默认 20 条/页）
- FR-9: 系统必须提供项目详情查询接口，返回项目基本信息 + 成员列表 + 任务统计
- FR-10: 系统必须提供项目更新接口（name、description）
- FR-11: 系统必须提供项目删除接口（软删除，标记 is_deleted）
- FR-12: 系统必须提供项目成员添加/移除接口
- FR-13: 前端必须提供项目列表页（ProjectsPage），展示所有项目卡片，支持新建项目弹窗
- FR-14: 前端必须提供项目详情页（ProjectDetailPage），展示项目信息 + 成员管理 + 任务列表

### 任务看板模块
- FR-15: 系统必须提供任务创建接口，接收 title、description、project_id、assignee_id、status、priority
- FR-16: 系统必须提供任务状态更新接口，支持 status 字段变更（todo / in_progress / done）
- FR-17: 系统必须提供任务列表查询接口，按 project_id 过滤，支持按 status、priority 排序
- FR-18: 前端必须提供 Kanban 看板页面（TaskBoardPage），按三列（To Do / In Progress / Done）展示任务卡片
- FR-19: 前端必须支持任务卡片在列间拖拽移动，拖拽后自动调用状态更新接口
- FR-20: 前端必须提供任务创建/编辑弹窗，包含 title、description、assignee、priority 字段

### 数据看板模块
- FR-21: 系统必须提供分析数据接口，返回项目维度的任务统计（总数/已完成/进行中/待办）
- FR-22: 系统必须提供项目进度接口，返回各项目完成百分比
- FR-23: 前端必须提供 Dashboard 页面（DashboardPage），展示项目概览卡片 + 进度条 + 统计图表
- FR-24: Dashboard 必须展示当前用户参与的所有项目的汇总统计

### 角色权限控制模块
- FR-25: 系统必须支持三种角色：Admin、Project Manager、Member
- FR-26: 系统必须在每个 API 请求中校验用户角色权限
- FR-27: Admin 可执行所有操作，包括删除项目和用户管理
- FR-28: Project Manager 可在所属项目内创建任务、分配成员、更新任务
- FR-29: Member 只能查看所属项目和更新自己被分配的任务状态
- FR-30: 前端必须根据用户角色动态显示/隐藏操作按钮

### DevOps / CI-CD 模块
- FR-31: GitHub Actions 工作流必须包含三个阶段：Build → SonarCloud Scan → JFrog Upload
- FR-32: Build 阶段必须执行前端构建（vite build）和后端检查（lint + test）
- FR-33: SonarCloud Scan 阶段必须上传分析结果并通过 Quality Gate
- FR-34: JFrog Upload 阶段必须将前端构建产物上传至 Artifactory，并触发 Xray 安全扫描
- FR-35: 工作流必须支持手动触发（workflow_dispatch）
- FR-36: Docker Compose 必须包含 frontend、backend、postgres 三个服务
- FR-37: 前端 Dockerfile 必须使用多阶段构建（build → nginx serve）
- FR-38: 后端 Dockerfile 必须基于 Python 3.11 slim 镜像

## 7. 关键流程/交互说明

### 用户注册/登录流程
1. 用户访问注册页面，填写 email、username、password
2. 提交后后端验证唯一性，bcrypt 加密密码，写入数据库
3. 注册成功跳转登录页
4. 用户输入 email + password 登录
5. 后端验证凭据，生成 JWT 返回
6. 前端存储 token 至 localStorage，后续请求自动附加

### 项目创建与任务分配流程
1. Project Manager 点击"新建项目"按钮
2. 填写项目名称和描述，提交创建
3. 进入项目详情页，添加团队成员
4. 在看板页面创建任务，指定负责人和优先级
5. 负责人在看板拖拽任务卡片更新状态

### CI/CD 流水线流程
1. 开发者推送代码或手动触发 workflow_dispatch
2. Stage 1 (Build): npm ci + vite build + python lint/test
3. Stage 2 (SonarCloud): 执行代码质量扫描，等待 Quality Gate
4. Stage 3 (JFrog Upload): 上传构建产物至 Artifactory
5. Xray 自动扫描上传的制品
6. 部署阶段：从 JFrog 拉取镜像，SSH 至华为云 ECS 执行 docker-compose up

## 8. 风险与依赖

**风险：**
- Kanban 拖拽交互在移动端浏览器兼容性不确定（不在 MVP 范围内）
- 大量任务时前端看板渲染可能影响性能
- 华为云 ECS 网络配置可能影响 Docker 镜像拉取速度
- SonarCloud Quality Gate 可能因已有技术债务导致初始扫描失败

**依赖：**
- PostgreSQL 15+ 数据库实例
- JFrog Artifactory 平台账号及仓库配置
- SonarCloud 组织及项目配置
- 华为云 ECS 实例及 SSH 访问权限
- GitHub Actions workflow dispatch 权限

## 9. 验收标准

- [ ] 用户可注册、登录，JWT 认证正常工作
- [ ] 项目 CRUD 完整可用，成员可添加/移除
- [ ] Kanban 看板展示三列任务，拖拽更新状态正常
- [ ] Dashboard 展示项目统计和进度图表
- [ ] Admin/PM/Member 三种角色权限正确限制操作
- [ ] 前端构建产物成功上传至 JFrog Artifactory
- [ ] SonarCloud Quality Gate 通过
- [ ] JFrog Xray 扫描无高危漏洞
- [ ] Docker Compose 本地启动正常（frontend + backend + postgres）
- [ ] GitHub Actions CI/CD 流水线三阶段全部通过
- [ ] 代码通过 Semgrep 安全扫描，无 CRITICAL 发现
- [ ] E2E 测试覆盖所有核心用户流程

## 10. 待确认问题

- 华为云 ECS 实例是否已就绪？SSH 密钥是否已配置？
- JFrog Artifactory 仓库是否已创建并配置 Xray？
- SonarCloud 项目是否已创建并关联 GitHub 仓库？
- 任务优先级是否需要影响看板列内排序？
- 是否需要任务截止日期（due date）字段？