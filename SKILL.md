---
name: 1c-enterprise-skill
description: >-
  Expert engineering skill for 1C:Enterprise 8.3 (1С:Предприятие) managed application configurations.
  Covers XML metadata schema rules, managed forms, BSL scripting (client/server boundaries, queries, automation),
  register design, ConfigDumpInfo.xml synchronization, and pre-commit validation.
---

# 1C:Enterprise 8.3 Managed Application Skill

This skill provides comprehensive instructions, architectural blueprints, XML schema specifications, and BSL development patterns for building enterprise-grade **1C:Enterprise 8.3** configurations from source files.

---

## 1. Directory Structure of a 1C Source Configuration

A 1C:Enterprise project exported to files (or imported via `Загрузить конфигурацию из файлов...`) follows this layout:

```
<ProjectRoot>/
├── Configuration.xml               # Root configuration descriptor
├── ConfigDumpInfo.xml              # Global manifest of all UUIDs and configVersions
├── Languages/
│   └── Русский.xml
├── Subsystems/
│   └── <SubsystemName>.xml
├── Catalogs/
│   └── <CatalogName>.xml
├── Documents/
│   ├── <DocName>.xml
│   └── <DocName>/
│       ├── Ext/
│       │   └── ObjectModule.bsl   # Posting (ОбработкаПроведения), validation
│       └── Forms/
│           ├── <FormName>.xml      # Form metadata definition
│           └── <FormName>/
│               ├── Ext/
│               │   ├── Form.xml    # Managed form UI structure
│               │   └── Form/
│               │       └── Module.bsl # Client/Server form event handlers
├── InformationRegisters/
│   └── <RegisterName>.xml
├── AccumulationRegisters/
│   └── <RegisterName>.xml
└── DataProcessors/
    ├── <ProcessorName>.xml
    └── <ProcessorName>/
        └── Forms/
            ├── <FormName>.xml
            └── <FormName>/
                ├── Ext/
                │   ├── Form.xml
                │   └── Form/
                │       └── Module.bsl
```

---

## 2. Critical XML Schema Rules & Pitfalls

### Rule 1: Form Properties by Object Type
- **Documents (`Document`)**:
  - Property is `<DefaultObjectForm>Document.<DocName>.Form.<FormName></DefaultObjectForm>`
  - Document properties also require:
    ```xml
    <DefaultListForm/>
    <DefaultChoiceForm/>
    <AuxiliaryObjectForm/>
    <AuxiliaryListForm/>
    <AuxiliaryChoiceForm/>
    ```
  - **NEVER** use `<DefaultForm>` in a Document or Catalog!
  - Under `Document/ChildObjects`: include `<Form><FormName></Form>` as a direct child.
- **DataProcessors / Reports**:
  - Property is `<DefaultForm>DataProcessor.<ProcessorName>.Form.<FormName></DefaultForm>`
  - Under `DataProcessor/ChildObjects`: include `<Form><FormName></Form>`.

### Rule 2: Form Metadata (`Forms/<FormName>.xml`)
- Form metadata descriptors under `Forms/` **MUST NOT** contain `<ExtendedPresentation/>`.
- Allowed properties in Form metadata:
  - `Name`
  - `Synonym`
  - `Comment`
  - `FormType` (`Managed`)
  - `IncludeHelpInContents` (`false`)
  - `UsePurposes` (`PlatformApplication`, `MobilePlatformApplication`)
  - `UseInInterfaceCompatibilityMode` (`Any`)

### Rule 3: Attribute Property Differences
| Property | Catalog Attribute | Document Attribute | TabularSection Attribute |
| :--- | :--- | :--- | :--- |
| `Use` (`ForItem`) | **YES** | **FORBIDDEN** | **FORBIDDEN** |
| `FillFromFillingValue` | **YES** | **YES** | **FORBIDDEN** |
| `FillValue` | **YES** | **YES** | **FORBIDDEN** |
| `DefaultForm` | **FORBIDDEN** | **FORBIDDEN** | **FORBIDDEN** |
| `FillChecking` | `DontCheck` / `ShowError` | `DontCheck` / `ShowError` | `DontCheck` / `ShowError` |

### Rule 4: String Qualifiers on Dimensions
- Any `xs:string` Dimension in an `AccumulationRegister` or `InformationRegister` **MUST** have `<StringQualifiers>` with `<Length>` (e.g. 50, 100) and `<AllowedLength>Variable</AllowedLength>`.
- An unqualified string in 1C becomes `NVARCHAR(MAX)` / `TEXT` in SQL, causing fatal DBMS errors when 1C attempts to create unique database indexes (`_AccumRgTn... UNIQUE`).

### Rule 5: Number Qualifiers
- Any `xs:decimal` field **MUST** include both:
  ```xml
  <v8:NumberQualifiers>
      <v8:Digits>15</v8:Digits>
      <v8:FractionDigits>2</v8:FractionDigits>
      <v8:AllowedSign>Any</v8:AllowedSign>
  </v8:NumberQualifiers>
  ```

### Rule 6: Mandatory UTF-8 BOM (`\xef\xbb\xbf`) and `<ConfigDumpInfo>` Root Tag
- 1C:Enterprise natively parses source files expecting the UTF-8 Byte Order Mark (BOM).
- The root tag of `ConfigDumpInfo.xml` **MUST** be:
  ```xml
  <ConfigDumpInfo xmlns="http://v8.1c.ru/8.3/xcf/dumpinfo" xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" format="Hierarchical" version="2.21">
  ```
- If the root tag is written as `<DumpInfo>` or `format="Hierarchical"` is omitted, or files lack the UTF-8 BOM, 1C Designer immediately fails with the error dialog: **«Отсутствует контейнер метаданных»** (Missing metadata container).


---

## 3. BSL Client / Server Rules (`&НаКлиенте` vs `&НаСервере`)

1. **Functions available ONLY on Server (`&НаСервере`)**:
   - `ТекущаяДатаСеанса()`
   - `НачалоМесяца()`, `КонецМесяца()`, `НачалоДня()`, `КонецДня()`
   - Database queries: `Новый Запрос`
   - Document posting, register writing: `Движения.<ИмяРегистра>.Записать()`
   - Catalogs / Documents lookups: `Справочники.<Имя>.НайтиПоРеквизиту()`
2. **Client Scope (`&НаКлиенте`)**:
   - Used only for user interaction, input capturing, and calling server procedures.
   - For line recalculation (`Цена * Количество = Сумма`):
     ```bsl
     &НаКлиенте
     Процедура ЗапчастиКоличествоПриИзменении(Элемент)
         СтрокаТаблицы = Элементы.Запчасти.ТекущиеДанные;
         Если СтрокаТаблицы <> Неопределено Тогда
             СтрокаТаблицы.Сумма = СтрокаТаблицы.Количество * СтрокаТаблицы.Цена;
             РассчитатьИтогиНаКлиенте();
         КонецЕсли;
     КонецПроцедуры
     ```

---

## 4. Manifest Synchronization (`ConfigDumpInfo.xml`)

Every metadata element, form, and module must be registered in `ConfigDumpInfo.xml`:
1. Metadata object: `<Metadata name="Document.ЗаказНаряд" id="..." configVersion="..."/>`
2. Form entry: `<Metadata name="Document.ЗаказНаряд.Form.ФормаДокумента" id="{form_uuid}" configVersion="..."/>`
3. Form body: `<Metadata name="Document.ЗаказНаряд.Form.ФормаДокумента.Form" id="{form_uuid}.0" configVersion="..."/>`
4. Object module: `<Metadata name="Document.ЗаказНаряд.ObjectModule" id="{doc_uuid}.0" configVersion="..."/>`

Use the automated Python script `scripts/generate_config_dump_info.py` to regenerate this file deterministically.

---

## 5. Standard Deployment Workflow

1. Modify or scaffold XML metadata files.
2. Write BSL business logic in `ObjectModule.bsl` and `Form/Module.bsl`.
3. Run `python scripts/validate_config.py <path-to-config>` to ensure zero schema violations.
4. Run `python scripts/generate_config_dump_info.py <path-to-config>` to sync the manifest.
5. In 1C:Designer (Конфигуратор):
   - Open empty or target database.
   - Select **Конфигурация -> Загрузить конфигурацию из файлов...**
   - Point to the configuration folder.
   - Press **F7** (Обновить конфигурацию базы данных) -> click **Принять**.
   - Press **F5** to start in Thin Client (`1С:Предприятие`).
