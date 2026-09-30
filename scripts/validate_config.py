import os
import sys
import xml.etree.ElementTree as ET

def validate_config(proj):
    errors = []
    print(f"=== Validating 1C Configuration in: {proj} ===")

    # 1. Parse all XML files
    xml_count = 0
    for root, dirs, files in os.walk(proj):
        for f in files:
            if f.endswith('.xml'):
                p = os.path.join(root, f)
                rel = os.path.relpath(p, proj)
                try:
                    tree = ET.parse(p)
                    xml_count += 1
                except Exception as e:
                    errors.append(f"XML Parse Error in {rel}: {e}")

    # 2. Check for illegal tags in objects and attributes
    for root, dirs, files in os.walk(proj):
        for f in files:
            if f.endswith('.xml') and not 'ConfigDumpInfo' in f and not 'Form' in root:
                p = os.path.join(root, f)
                rel = os.path.relpath(p, proj)
                with open(p, 'r', encoding='utf-8') as fp:
                    c = fp.read()
                
                # Illegal DefaultForm in Document or Catalog
                if 'DefaultForm' in c and not ('DataProcessor' in rel):
                    errors.append(f"Illegal <DefaultForm> tag in non-DataProcessor file: {rel}")
                
                tree = ET.parse(p)
                
                # Check Document attributes
                for doc in tree.iter('{http://v8.1c.ru/8.3/MDClasses}Document'):
                    doc_child_objs = doc.find('{http://v8.1c.ru/8.3/MDClasses}ChildObjects')
                    if doc_child_objs is not None:
                        for attr in doc_child_objs.findall('{http://v8.1c.ru/8.3/MDClasses}Attribute'):
                            aname = attr.findtext('{http://v8.1c.ru/8.3/MDClasses}Properties/{http://v8.1c.ru/8.3/MDClasses}Name')
                            props = attr.find('{http://v8.1c.ru/8.3/MDClasses}Properties')
                            if props is not None:
                                for child in props:
                                    tag = child.tag.split('}')[-1]
                                    if tag in ['Use', 'DefaultForm']:
                                        errors.append(f"Illegal tag <{tag}> in Document Attribute {rel} -> {aname}")
                
                # Check TabularSection attributes (in Document or Catalog)
                for ts in tree.iter('{http://v8.1c.ru/8.3/MDClasses}TabularSection'):
                    tsname = ts.findtext('{http://v8.1c.ru/8.3/MDClasses}Properties/{http://v8.1c.ru/8.3/MDClasses}Name')
                    ts_child_objs = ts.find('{http://v8.1c.ru/8.3/MDClasses}ChildObjects')
                    if ts_child_objs is not None:
                        for attr in ts_child_objs.findall('{http://v8.1c.ru/8.3/MDClasses}Attribute'):
                            aname = attr.findtext('{http://v8.1c.ru/8.3/MDClasses}Properties/{http://v8.1c.ru/8.3/MDClasses}Name')
                            props = attr.find('{http://v8.1c.ru/8.3/MDClasses}Properties')
                            if props is not None:
                                for child in props:
                                    tag = child.tag.split('}')[-1]
                                    if tag in ['Use', 'FillFromFillingValue', 'FillValue', 'DefaultForm']:
                                        errors.append(f"Illegal tag <{tag}> in TabularSection Attribute {rel} -> {tsname}.{aname}")

    # 3. Check Form metadata files
    form_meta_count = 0
    for root, dirs, files in os.walk(proj):
        for f in files:
            if f.endswith('.xml') and ('Forms' in root) and not ('Ext' in root):
                p = os.path.join(root, f)
                rel = os.path.relpath(p, proj)
                form_meta_count += 1
                with open(p, 'r', encoding='utf-8') as fp:
                    c = fp.read()
                if 'ExtendedPresentation' in c:
                    errors.append(f"Illegal <ExtendedPresentation> in Form metadata: {rel}")

    # 4. Check Registers
    areg_dir = os.path.join(proj, 'AccumulationRegisters')
    if os.path.exists(areg_dir):
        for f in os.listdir(areg_dir):
            if f.endswith('.xml'):
                tree = ET.parse(os.path.join(areg_dir, f))
                rtype = tree.findtext('.//{http://v8.1c.ru/8.3/MDClasses}RegisterType')
                if rtype not in ['Balance', 'Turnovers']:
                    errors.append(f"AccumulationRegister {f} has invalid RegisterType '{rtype}'")

    ireg_dir = os.path.join(proj, 'InformationRegisters')
    independent_iregs = set()
    if os.path.exists(ireg_dir):
        for f in os.listdir(ireg_dir):
            if f.endswith('.xml'):
                ireg_name = f[:-4]
                ipath = os.path.join(ireg_dir, f)
                with open(ipath, 'r', encoding='utf-8') as fp:
                    icontent = fp.read()
                if 'EnableTotalsSplitting' in icontent:
                    errors.append(f"Illegal <EnableTotalsSplitting> in InformationRegister: {f}")
                tree = ET.parse(ipath)
                wmode = tree.findtext('.//{http://v8.1c.ru/8.3/MDClasses}WriteMode')
                if wmode == 'Independent':
                    independent_iregs.add(ireg_name)

    # 4b. Check Document RegisterRecords for independent InfoRegs
    doc_dir = os.path.join(proj, 'Documents')
    if os.path.exists(doc_dir):
        for f in os.listdir(doc_dir):
            if f.endswith('.xml'):
                dpath = os.path.join(doc_dir, f)
                tree = ET.parse(dpath)
                for item in tree.iter('{http://v8.1c.ru/8.3/xcf/readable}Item'):
                    ref_text = item.text or ''
                    if ref_text.startswith('InformationRegister.'):
                        ireg_ref = ref_text.split('.')[-1]
                        if ireg_ref in independent_iregs:
                            errors.append(f"Document {f} contains Independent InformationRegister in RegisterRecords: {ref_text}")

    # 5. Check NumberQualifiers
    num_qual_count = 0
    for root, dirs, files in os.walk(proj):
        for f in files:
            if f.endswith('.xml'):
                tree = ET.parse(os.path.join(root, f))
                for nq in tree.iter('{http://v8.1c.ru/8.1/data/core}NumberQualifiers'):
                    digits = nq.find('{http://v8.1c.ru/8.1/data/core}Digits')
                    frac = nq.find('{http://v8.1c.ru/8.1/data/core}FractionDigits')
                    if digits is None or frac is None:
                        errors.append(f"Incomplete NumberQualifiers in {f}")
                    else:
                        num_qual_count += 1

    # 6. Check BSL syntax & Client/Server scope
    bsl_count = 0
    for root, dirs, files in os.walk(proj):
        for f in files:
            if f.endswith('.bsl'):
                p = os.path.join(root, f)
                rel = os.path.relpath(p, proj)
                bsl_count += 1
                with open(p, 'r', encoding='utf-8') as fp:
                    lines = fp.readlines()
                in_client = False
                for idx, line in enumerate(lines):
                    sline = line.strip()
                    if sline.startswith('&НаКлиенте'):
                        in_client = True
                    elif sline.startswith('&НаСервере') or sline.startswith('&НаКлиентеНаСервереБезКонтекста') or sline.startswith('&НаСервереБезКонтекста'):
                        in_client = False
                    if in_client:
                        for forbidden in ['ТекущаяДатаСеанса', 'НачалоМесяца', 'КонецДня', 'НачалоДня', 'КонецМесяца']:
                            if forbidden in line:
                                errors.append(f"Client scope violation in {rel} (line {idx+1}): forbidden function '{forbidden}'")

    # 7. Check ConfigDumpInfo.xml consistency
    dump_path = os.path.join(proj, 'ConfigDumpInfo.xml')
    if os.path.exists(dump_path):
        dump_tree = ET.parse(dump_path)
        dump_names = set()
        for elem in dump_tree.iter('{http://v8.1c.ru/8.3/xcf/dumpinfo}Metadata'):
            dump_names.add(elem.attrib.get('name'))
    else:
        errors.append("ConfigDumpInfo.xml missing!")

    if errors:
        print(f"FAILED! Found {len(errors)} error(s):")
        for e in errors:
            print(f"  [ERROR] {e}")
        return False
    else:
        print(f"SUCCESS! Validated {xml_count} XMLs, {form_meta_count} Forms, {bsl_count} BSL modules, {num_qual_count} NumberQualifiers.")
        print("Zero schema violations found.")
        return True

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    ok = validate_config(target)
    sys.exit(0 if ok else 1)
