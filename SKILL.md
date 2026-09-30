---
name: 1c-enterprise-skill
description: >-
  Expert engineering skill and authoritative guide for developing, scaffolding, validating,
  and troubleshooting 1C:Enterprise 8.3 (1С:Предприятие) managed application configurations
  directly from source files (XML + BSL). Use whenever creating or modifying 1C metadata,
  managed forms, registers, documents, catalogs, BSL business logic, ConfigDumpInfo.xml manifests,
  or resolving 1C XML parser and DBMS errors.
---

# 1C:Enterprise 8.3 Managed Application Engineering Skill

## 1. When to Activate This Skill

Activate this skill whenever:
- Creating a new 1C:Enterprise 8.3 configuration from scratch or adding new metadata objects.
- Writing or refactoring business logic in **BSL** (1C Enterprise Script).
- Creating or editing **Managed Forms** (Управляемые формы), form XML layouts, or form event handlers.
- Configuring **Registers** (Регистры накопления, Регистры сведений) and document posting mechanisms.
- Resolving 1C Designer errors during import:
  - *«Отсутствует контейнер метаданных»*
  - *«Неверное свойство объекта метаданных. Свойство DefaultForm не входит в состав...»*
  - *«Неверное свойство объекта метаданных. Свойство ExtendedPresentation не входит в состав Form...»*
  - *«Свойство Use / FillFromFillingValue не входит в состав объекта метаданных Attribute...»*
  - *«Попытка включить в индекс поля типов TEXT, NTEXT, IMAGE или ROWVERSION...»*
  - *«Процедура или функция не определена (ТекущаяДатаСеанса)»*
- Synchronizing the configuration manifest (`ConfigDumpInfo.xml`).

---

## 2. Architecture of a 1C Configuration in Source Files

1C:Enterprise 8.3 configurations exported to files (`Выгрузить конфигурацию в файлы...` / `Загрузить конфигурацию из файлов...`) follow a strict hierarchical directory structure:

```text
<ConfigurationRoot>/
├── Configuration.xml               # Root configuration descriptor (ContainedObjects, metadata properties)
├── ConfigDumpInfo.xml              # Global manifest of all UUIDs, versions, and metadata objects
├── Languages/
│   └── Русский.xml                 # Interface language definition
├── Subsystems/
│   └── <SubsystemName>.xml         # UI Navigation subsystems
├── Catalogs/
│   └── <CatalogName>.xml           # Catalogs (Справочники)
├── Documents/
│   ├── <DocName>.xml               # Document descriptor (Документы)
│   └── <DocName>/
│       ├── Ext/
│       │   └── ObjectModule.bsl    # Document posting logic (ОбработкаПроведения)
│       └── Forms/
│           ├── <FormName>.xml      # Form metadata definition
│           └── <FormName>/
│               ├── Ext/
│               │   ├── Form.xml    # Managed form UI structure (Таблицы, Группы, Поля)
│               │   └── Form/
│               │       └── Module.bsl # Form client/server event handlers
├── InformationRegisters/
│   └── <RegisterName>.xml          # Information registers (Регистры сведений)
├── AccumulationRegisters/
│   └── <RegisterName>.xml          # Accumulation registers (Регистры накопления)
└── DataProcessors/
    ├── <ProcessorName>.xml         # Data processors (Обработки, Ассистенты, Отчеты)
    └── <ProcessorName>/
        └── Forms/
            ├── <FormName>.xml
            └── <FormName>/
                ├── Ext/
                │   ├── Form.xml
                │   └── Form/
                │       └── Module.bsl
```

### Essential Root Files
1. **`Configuration.xml`**:
   - Must declare 7 fixed `xr:ContainedObject` class IDs representing core metadata managers:
     - `9cd510cd-abfc-11d4-9434-004095e12fc7` (Metadata Container)
     - `9fcd25a0-4822-11d4-9414-008048da11f9` (Subsystems Container)
     - `e3687481-0a87-462c-a166-9f34594f9bba` (Common Modules Container)
     - `9de14907-ec23-4a07-96f0-85521cb6b53b` (Session Parameters Container)
     - `51f2d5d8-ea4d-4064-8892-82951750031e` (Roles Container)
     - `e68182ea-4237-4383-967f-90c1e3370bc7` (Common Forms Container)
     - `fb282519-d103-4dd3-bc12-cb271d631dfc` (Interface Container)
2. **`ConfigDumpInfo.xml`**:
   - The master manifest required by 1C Designer during load.
   - Root element **MUST** be `<ConfigDumpInfo ... format="Hierarchical" version="2.21">`.

---

## 3. The 6 Critical XML Schema Rules & Prevention

### Rule 1: Form Properties by Object Type (`DefaultObjectForm` vs `DefaultForm`)
- **Document (`<Document>`)**:
  - Property is **`<DefaultObjectForm>Document.<DocName>.Form.<FormName></DefaultObjectForm>`**.
  - Document also requires these 5 companion tags in `<Properties>`:
    ```xml
    <DefaultListForm/>
    <DefaultChoiceForm/>
    <AuxiliaryObjectForm/>
    <AuxiliaryListForm/>
    <AuxiliaryChoiceForm/>
    ```
  - Direct child in `<Document>/<ChildObjects>`: `<Form><FormName></Form>`.
  - ⚠️ **NEVER** use `<DefaultForm>` in a Document, Catalog, or Attribute!
- **DataProcessor / Report (`<DataProcessor>`)**:
  - Property is **`<DefaultForm>DataProcessor.<Name>.Form.<FormName></DefaultForm>`**.
  - Direct child in `<DataProcessor>/<ChildObjects>`: `<Form><FormName></Form>`.

### Rule 2: Form Metadata Descriptors (`Forms/<FormName>.xml`)
The metadata descriptor for a form (e.g. `Documents/ЗаказНаряд/Forms/ФормаДокумента.xml`) is strictly limited.
- ⚠️ **DO NOT include `<ExtendedPresentation/>`**! Doing so causes: `Свойство ExtendedPresentation не входит в состав объекта метаданных Form`.
- Standard valid form metadata template:
  ```xml
  <?xml version="1.0" encoding="UTF-8"?>
  <MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" ... version="2.21">
      <Form uuid="{UUID}">
          <Properties>
              <Name>ФормаДокумента</Name>
              <Synonym>
                  <v8:item>
                      <v8:lang>ru</v8:lang>
                      <v8:content>Форма документа</v8:content>
                  </v8:item>
              </Synonym>
              <Comment/>
              <FormType>Managed</FormType>
              <IncludeHelpInContents>false</IncludeHelpInContents>
              <UsePurposes>
                  <v8:Value xsi:type="app:ApplicationUsePurpose">PlatformApplication</v8:Value>
                  <v8:Value xsi:type="app:ApplicationUsePurpose">MobilePlatformApplication</v8:Value>
              </UsePurposes>
              <UseInInterfaceCompatibilityMode>Any</UseInInterfaceCompatibilityMode>
          </Properties>
      </Form>
  </MetaDataObject>
  ```

### Rule 3: Attribute Property Context Matrix
Properties allowed in `<Properties>` of an `<Attribute>` depend strictly on its parent container:

| Property | Catalog Attribute | Document Attribute | TabularSection Attribute |
| :--- | :---: | :---: | :---: |
| `Name`, `Synonym`, `Type` | ✅ | ✅ | ✅ |
| `Use` (`ForItem` / `ForFolder`) | ✅ | ❌ **FORBIDDEN** | ❌ **FORBIDDEN** |
| `FillFromFillingValue` | ✅ | ✅ | ❌ **FORBIDDEN** |
| `FillValue` | ✅ | ✅ | ❌ **FORBIDDEN** |
| `DefaultForm` | ❌ **FORBIDDEN** | ❌ **FORBIDDEN** | ❌ **FORBIDDEN** |
| `Indexing` | ✅ | ✅ | ✅ |
| `FullTextSearch` | ✅ | ✅ | ✅ |

*Placing `Use` or `FillValue` into a TabularSection Attribute will trigger: `Свойство FillFromFillingValue не входит в состав объекта метаданных Attribute`.*

### Rule 4: String Qualifiers on Dimensions in SQL
- When creating a Dimension with type `xs:string` in an Accumulation or Information Register, you **MUST** provide explicit `<StringQualifiers>`:
  ```xml
  <v8:Type>xs:string</v8:Type>
  <v8:StringQualifiers>
      <v8:Length>50</v8:Length>
      <v8:AllowedLength>Variable</v8:AllowedLength>
  </v8:StringQualifiers>
  ```
- ⚠️ **Why**: An unqualified string defaults to unlimited length (`NVARCHAR(MAX)` / `TEXT` in SQL). When 1C attempts to build unique clustered indexes (`_AccumRgTn... UNIQUE`), SQL Server / PostgreSQL throws a critical table creation error.

### Rule 5: Number Qualifiers Completeness
- Any numeric field (`xs:decimal`) **MUST** specify both digits and fractional digits:
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
- ⚠️ **Why**: If `<ConfigDumpInfo>` is written as `<DumpInfo>`, or `format="Hierarchical"` is omitted, or files lack the UTF-8 BOM, 1C Designer fails on load with the dialog: **«Отсутствует контейнер метаданных»** (Missing metadata container).

### Rule 7: InformationRegister vs AccumulationRegister Properties & Document Movements
1. **`EnableTotalsSplitting` is ONLY for Accumulation Registers**:
   - `AccumulationRegister` supports splitting totals (`<EnableTotalsSplitting>true</EnableTotalsSplitting>`).
   - `InformationRegister` does NOT maintain totals. Placing `<EnableTotalsSplitting>` inside an InformationRegister causes:
     `Неверное свойство объекта метаданных. Свойство EnableTotalsSplitting не входит в состав объекта метаданных InformationRegister`.
2. **Independent Information Registers cannot be listed in Document `<RegisterRecords>`**:
   - If an InformationRegister has `<WriteMode>Independent</WriteMode>`, it has no recorder attribute and cannot be attached as a movement recorder.
   - Listing an Independent InformationRegister in a Document's `<RegisterRecords>` causes:
     `Документ.<Имя> - в списке Движений обнаружены ссылки на объекты, которые не могут быть подключены`.
   - **Solution**: Keep `<RegisterRecords/>` empty on the Document, and write records in BSL using `РегистрыСведений.<Имя>.СоздатьНаборЗаписей()`:
     ```bsl
     Процедура ОбработкаПроведения(Отказ, РежимПроведения)
         Для Каждого Стр Из Товары Цикл
             Набор = РегистрыСведений.ЦеныНоменклатуры.СоздатьНаборЗаписей();
             Набор.Отбор.Номенклатура.Установить(Стр.Номенклатура);
             Запись = Набор.Добавить();
             Запись.Номенклатура = Стр.Номенклатура;
             Запись.Цена = Стр.Цена;
             Набор.Записать(Истина);
         КонецЦикла;
     КонецПроцедуры
     ```

---

## 4. BSL Programming Standards (`&НаКлиенте` vs `&НаСервере`)

### Client/Server Boundary Rules
1. **Functions available ONLY on Server (`&НаСервере` / `&НаСервереБезКонтекста`)**:
   - `ТекущаяДатаСеанса()` (Thin Client does NOT know session time!)
   - `НачалоМесяца()`, `КонецМесяца()`, `НачалоДня()`, `КонецДня()`
   - Database operations: `Новый Запрос`, `Справочники`, `Документы`, `РегистрыНакопления`
   - Document postings: `Движения.<ИмяРегистра>.Записать()`
2. **Client Scope (`&НаКлиенте`)**:
   - Used strictly for UI interaction, user input, and calling server methods.
   - For line recalculation (`Сумма = Количество * Цена`):
     ```bsl
     &НаКлиенте
     Процедура ЗапчастиКоличествоПриИзменении(Элемент)
         СтрокаТаблицы = Элементы.Запчасти.ТекущиеДанные;
         Если СтрокаТаблицы <> Неопределено Тогда
             СтрокаТаблицы.Сумма = СтрокаТаблицы.Количество * СтрокаТаблицы.Цена;
             РассчитатьИтогиНаКлиенте();
         КонецЕсли;
     КонецПроцедуры

     &НаКлиенте
     Процедура РассчитатьИтогиНаКлиенте()
         ИтогРабот = 0;
         ИтогЗапчастей = 0;
         Для Каждого Стр Из Объект.Работы Цикл
             ИтогРабот = ИтогРабот + Стр.Сумма;
         КонецЦикла;
         Для Каждого Стр Из Объект.Запчасти Цикл
             ИтогЗапчастей = ИтогЗапчастей + Стр.Сумма;
         КонецЦикла;
         Объект.ИтогоСуммаРабот = ИтогРабот;
         Объект.ИтогоСуммаЗапчастей = ИтогЗапчастей;
         Объект.ВсегоК_Оплате = ИтогРабот + ИтогЗапчастей;
     КонецПроцедуры
     ```

### Document Posting Pattern (`ObjectModule.bsl`)
```bsl
Процедура ОбработкаПроведения(Отказ, РежимПроведения)
    
    // Блокировка и списание остатков материалов
    Движения.ОстаткиМатериалов.Записывать = Истина;
    Для Каждого Стр Из Запчасти Цикл
        Движение = Движения.ОстаткиМатериалов.ДобавитьРасход();
        Движение.Период = Дата;
        Движение.Склад = Склад;
        Движение.Номенклатура = Стр.Номенклатура;
        Движение.Количество = Стр.Количество;
    КонецЦикла;

    // Начисление выработки и зарплаты механиков
    Движения.ВыработкаИЗарплатаМехаников.Записывать = Истина;
    Для Каждого Стр Из Работы Цикл
        Движение = Движения.ВыработкаИЗарплатаМехаников.Добавить();
        Движение.Период = Дата;
        Движение.Механик = Стр.Исполнитель;
        Движение.ВидРемонта = Строка(Стр.Услуга);
        Движение.НормоЧасы = Стр.НормоЧасы;
        Движение.СуммаНачисления = Стр.Сумма;
    КонецЦикла;

КонецПроцедуры
```

---

## 5. Automation Tooling in `scripts/`

The skill includes three battle-tested Python utilities:

### 1. `scripts/validate_config.py`
Runs a comprehensive pre-flight verification:
- Parses every XML file for well-formedness.
- Detects illegal tags (`DefaultForm` in Documents, `ExtendedPresentation` in Forms, `Use` in TabularSections).
- Verifies `RegisterType` on AccumulationRegisters (`Balance` or `Turnovers`).
- Verifies that all `NumberQualifiers` include both `Digits` and `FractionDigits`.
- Scans all BSL modules for client-scope violations (`ТекущаяДатаСеанса` on client).
- Checks that `ConfigDumpInfo.xml` exists and contains all declared metadata.

Usage:
```bash
python scripts/validate_config.py "C:/Path/To/1C_Configuration"
```

### 2. `scripts/generate_config_dump_info.py`
Inspects all objects, forms, and modules in the configuration folder, extracts their actual UUIDs, generates deterministic 40-character `configVersion` hashes, and writes a valid `ConfigDumpInfo.xml` with `format="Hierarchical"` and `UTF-8 BOM`.

Usage:
```bash
python scripts/generate_config_dump_info.py "C:/Path/To/1C_Configuration"
```

### 3. `scripts/init_project.py`
Initializes a new, fully compliant 1C 8.3 managed configuration in seconds:
- Generates `Configuration.xml` with valid ContainedObject GUIDs.
- Generates `Languages/Русский.xml`.
- Generates initial `ConfigDumpInfo.xml`.
- Creates standard subdirectories.

Usage:
```bash
python scripts/init_project.py "C:/Path/To/NewConfig" "ИмяКонфигурации"
```

---

## 6. Pre-Commit & Deployment Checklist

Before committing or loading configuration into 1C:
1. ✅ **Run Validator**: `python scripts/validate_config.py <path>`. Exit code must be 0.
2. ✅ **Sync Manifest**: `python scripts/generate_config_dump_info.py <path>`.
3. ✅ **Check BOM**: Verify that all `.xml` and `.bsl` files start with `\xef\xbb\xbf`.
4. ✅ **In 1C Designer**:
   - Open target base.
   - Ensure configuration is open: **Конфигурация ➔ Открыть конфигурацию**.
   - Select: **Конфигурация ➔ Загрузить конфигурацию из файлов...**
   - Press **F7** (Обновить конфигурацию базы данных) ➔ click **Принять**.
   - Press **F5** to test in Managed Application mode.
