# 具身智能机器人行业研究交付包

这是一个面向企业管理层的具身智能机器人战略学习包。内容以中国市场为主，海外标杆作为对照，目标是帮助非机器人专业背景的管理者快速理解行业逻辑、识别可试点场景、判断合作与采购路径，并建立持续跟踪机制。

本仓库不是新闻剪贴、投资建议或采购清单，而是一套可阅读、可培训、可讨论、可用于内部战略研判的 Markdown 与静态网页交付物。

## 适合读者

- 董事会、总经理、业务负责人：用于快速判断为什么要关注具身智能机器人，以及企业是否需要进入或试点。
- 战略部、数字化部、创新业务团队：用于建立行业框架、场景评估方法和年度跟踪指标。
- 采购、运营、产研和投资观察者：用于理解供应商差异、落地证据、试点路径和主要风险。

## 交付内容

当前交付包包含：

- 200 个 Markdown 报告和公司深度章节
- 7 个结构化数据表
- 209 个静态 HTML 页面
- 51 家中国公司样本
- 20 家海外对照公司样本
- 36 条公开落地案例
- 8 个核心场景成熟度条目
- 651 条公司深度来源记录
- 10 家核心中国企业 10 万字级深度分析，41 家其他中国企业 5000 字级结构化分析

完整目录请查看 [index.md](index.md)，网页目录请打开 [index.html](index.html)。

## 快速开始

- 管理层入口：[管理层学习指南](reports/management_learning_guide.md)
- 全部 Markdown 与网页索引：[index.md](index.md)
- 本地静态网页目录：[index.html](index.html)
- 中国公司深度库：[中国公司深度库总目录](reports/competition/china_company_deep_index.md)
- 公司深度来源库：[data/company_deep_sources.csv](data/company_deep_sources.csv)
- 中国公司库：[data/domestic_companies.csv](data/domestic_companies.csv)
- 落地案例库：[data/deployment_cases.csv](data/deployment_cases.csv)
- 来源索引：[sources/source_index.md](sources/source_index.md)

## 建议阅读路径

### 2 小时管理层速读

适合董事会、总经理和业务负责人快速建立判断框架：

1. [管理层学习指南](reports/management_learning_guide.md)
2. [管理层简报](reports/executive/01_board_briefing.md)
3. [战略决策地图](reports/executive/02_decision_map.md)
4. [中国公司深度库](reports/competition/china_company_deep_index.md)
5. [成熟度模型](reports/decision_tools/01_maturity_model.md)
6. [90 天试点打法](reports/decision_tools/03_90_day_pilot_playbook.md)

### 半天专题学习

适合战略部、数字化部、业务创新团队组织共读：

1. 先完成 2 小时速读路径。
2. 阅读行业基础课，理解具身智能、机器人形态、VLA、数据飞轮和硬件栈。
3. 阅读中国竞争格局、海外标杆对照、公司分层矩阵。
4. 按本公司业务选择 2 到 3 个场景报告做内部讨论。

### 1 周深读

适合战略规划、采购、产研、运营和投资观察团队做专题研判：

1. 按 [index.md](index.md) 的完整目录通读核心报告。
2. 用 [供应商尽调清单](reports/decision_tools/04_vendor_due_diligence_checklist.md) 访谈候选公司。
3. 用 [ROI 测算模型](reports/decision_tools/05_roi_model.md) 评估一个真实业务场景。
4. 用 [年度跟踪看板](reports/decision_tools/06_annual_tracking_dashboard.md) 建立月度复盘机制。

## 目录说明

- `reports/`：核心研究报告，覆盖管理层总览、行业基础、公司与竞品、场景商业化、战略决策工具。
- `reports/company_profiles/china_deep_dive/`：中国公司深度库，核心企业按章节拆分，其他企业按结构化单篇分析。
- `data/`：结构化数据表，包括公司库、产品库、落地案例库、融资事件库和场景成熟度库。
- `sources/`：来源索引与证据线索，用于回溯关键判断的公开依据。
- `docs/`：项目规划、研究范围、术语口径和来源引用规则。
- `html/`：由 Markdown 和 CSV 转换生成的静态网页版本，便于浏览和培训展示。

## 本地网页预览

当前仓库已配置本机 Nginx 预览入口：

```text
http://localhost:8094/
```

也可以直接打开根目录的 [index.html](index.html) 查看网页目录。网页内容来自仓库内 Markdown 与 CSV，严肃引用时应回到源文件和来源索引核验。

## 使用建议与限制

- 优先把本包作为管理层学习、战略讨论和试点设计材料使用。
- 对公司进展、订单、融资、量产和客户案例等高时效内容，应在正式决策前重新核验公开来源。
- 阅读时应区分事实、公司自述、媒体报道、第三方估算和本包判断。
- 本包不构成投资建议、采购承诺、法律意见或财务意见。
