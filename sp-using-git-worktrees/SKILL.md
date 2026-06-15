---
name: sp-using-git-worktrees
description: 在开始需要与当前工作区隔离的功能开发时使用，或在执行实现计划之前使用——确保通过原生工具或 git worktree 降级方案建立隔离的工作区
---

# 使用 Git Worktrees

## 概述

确保工作在隔离的工作区中进行。优先使用你所在平台的原生 worktree 工具。仅当没有原生工具时才降级为手动使用 git worktrees。

**开始时声明：** "我正在使用 `sp-using-git-worktrees` 技能来设置隔离的工作区。"

## 步骤 0：检测已有的隔离环境

在创建任何内容之前，检查是否已经处于隔离的工作区中。
使用 `git rev-parse --git-dir` 和 `git rev-parse --git-common-dir`。如果它们不相等且你不在子模块中，说明你已经在 linked worktree 中，直接跳到步骤 3。

## 步骤 1：创建隔离工作区

### 1a. 原生 Worktree 工具（首选）
如果宿主平台有类似 `EnterWorktree` 的工具或指令，使用它，然后跳到步骤 3。

### 1b. Git Worktree 降级方案（没有原生工具时才用）
根据用户指令中指定的目录或优先尝试本地 `.worktrees` 目录（隐藏目录）。
**关键安全验证：** 必须使用 `git check-ignore` 验证该目录在 git 忽略列表中。如果不在，自动添加到 `.gitignore` 并提交。
创建 worktree：`git worktree add <path> -b <branch>`，并 `cd` 进入。

## 步骤 3：项目环境设置
自动检测并运行依赖安装：
- Node.js：如果有 `package.json` 则 `npm install`
- Rust：如果有 `Cargo.toml` 则 `cargo build`
- Python：如果有 `requirements.txt` 则 `pip install`，如果有 `pyproject.toml` 则 `poetry install`
- Go：如果有 `go.mod` 则 `go mod download`

## 步骤 4：验证干净的基线测试
运行项目的默认测试，确保工作区一开始是干净无错的。如果测试失败，报告错误并询问是否要继续。

## 红线规则
**绝不：**
- 当步骤 0 检测到已处于隔离中时创建 worktree
- 在有原生隔离工具时使用 `git worktree add`
- 在项目内创建 worktree 时未验证其被 git ignore 忽略
- 在不告知的情况下带着失败的测试继续工作
