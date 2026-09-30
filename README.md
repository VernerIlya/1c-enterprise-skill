# 1C:Enterprise Skill for AI Agents & Developers 🚀

[![1C:Enterprise](https://img.shields.io/badge/1C%3AEnterprise-8.3-yellow.svg)](https://1c.ru)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Validation](https://img.shields.io/badge/Schema%20Validation-Passing-brightgreen.svg)]()

> A robust, battle-tested engineering skill and framework for developing, validating, and scaffolding **1C:Enterprise 8.3 (1С:Предприятие)** managed configurations directly from source files using autonomous AI agents.

---

## 🌟 Why this Skill?

Developing 1C:Enterprise configurations outside the official GUI designer often triggers subtle XML schema errors and database crashes:
- `Свойство DefaultForm не входит в состав объекта Document` (Documents require `DefaultObjectForm`, only DataProcessors use `DefaultForm`).
- `Свойство ExtendedPresentation не входит в состав объекта Form` (Form metadata files must not have `ExtendedPresentation`).
- `Свойство Use не входит в состав объекта метаданных Attribute` (`Use` is valid only on Catalog attributes, not Document or TabularSection attributes).
- `Попытка включить в индекс поля типов TEXT/IMAGE` (string dimensions without fixed lengths become unbounded strings in SQL and cannot be indexed).
- `Процедура или функция не определена (ТекущаяДатаСеанса)` on Thin Client (`&НаКлиенте`).

This skill codifies **100% of these rules**, providing automated linters, manifest generators, and templates.

---

## 📂 Repository Contents

```
1c-enterprise-skill/
├── SKILL.md                          # Main agent instructions & schema rules
├── README.md                         # Documentation & Quickstart
├── scripts/
│   ├── validate_config.py            # Pre-flight XML and BSL validator (0 errors guarantee)
│   └── generate_config_dump_info.py  # Automatic ConfigDumpInfo.xml manifest generator
└── templates/                        # Reusable 1C metadata XML templates
```

---

## 🛠️ Quickstart

### 1. Pre-commit Validation
Before loading your configuration into 1C:Enterprise:
```bash
python scripts/validate_config.py /path/to/1C_Configuration
```

### 2. Synchronize ConfigDumpInfo.xml
```bash
python scripts/generate_config_dump_info.py /path/to/1C_Configuration
```

### 3. Import into 1C:Enterprise
1. Open **1C:Designer** (Конфигуратор).
2. Choose **Конфигурация -> Загрузить конфигурацию из файлов...**
3. Select your configuration folder.
4. Press **F7** (Обновить конфигурацию базы данных) and click **Принять**.
5. Press **F5** to run in Managed Client.

---

## 📄 License
MIT License. Feel free to use in your projects and fork!
