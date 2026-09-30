import os
import re
import hashlib
import xml.etree.ElementTree as ET

proj = r'C:\Users\enven\OneDrive\Documents\1C_Автосервис_ПРО_Конфигурация'

def get_hash(name):
    h = hashlib.md5(name.encode('utf-8')).hexdigest()
    return h + "00000000"

def get_file_uuid(path, tag_name):
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    m = re.search(rf'<{tag_name}\s+uuid="([^"]+)"', text)
    return m.group(1) if m else None

lines = []
lines.append('<?xml version="1.0" encoding="UTF-8"?>')
lines.append('<ConfigDumpInfo xmlns="http://v8.1c.ru/8.3/xcf/dumpinfo" xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" format="Hierarchical" version="2.21">')
lines.append('\t<ConfigVersions>')

# 1. Configuration
config_uuid = get_file_uuid(os.path.join(proj, 'Configuration.xml'), 'Configuration')
lines.append(f'\t\t<Metadata name="Configuration.Автосервис_ПРО_ERP" id="{config_uuid}" configVersion="{get_hash("Configuration.Автосервис_ПРО_ERP")}"/>')

# 2. Subsystems
subsystems_dir = os.path.join(proj, 'Subsystems')
if os.path.exists(subsystems_dir):
    for f in sorted(os.listdir(subsystems_dir)):
        if f.endswith('.xml'):
            sname = f[:-4]
            suuid = get_file_uuid(os.path.join(subsystems_dir, f), 'Subsystem')
            lines.append(f'\t\t<Metadata name="Subsystem.{sname}" id="{suuid}" configVersion="{get_hash(f"Subsystem.{sname}")}"/>')

# 3. Languages
lang_dir = os.path.join(proj, 'Languages')
if os.path.exists(lang_dir):
    for f in sorted(os.listdir(lang_dir)):
        if f.endswith('.xml'):
            lname = f[:-4]
            luuid = get_file_uuid(os.path.join(lang_dir, f), 'Language')
            lines.append(f'\t\t<Metadata name="Language.{lname}" id="{luuid}" configVersion="{get_hash(f"Language.{lname}")}"/>')

# 4. Catalogs
catalogs_dir = os.path.join(proj, 'Catalogs')
if os.path.exists(catalogs_dir):
    for f in sorted(os.listdir(catalogs_dir)):
        if f.endswith('.xml'):
            cname = f[:-4]
            cpath = os.path.join(catalogs_dir, f)
            cuuid = get_file_uuid(cpath, 'Catalog')
            
            tree = ET.parse(cpath)
            attrs = []
            for a in tree.iter('{http://v8.1c.ru/8.3/MDClasses}Attribute'):
                auuid = a.attrib.get('uuid')
                aname = a.findtext('{http://v8.1c.ru/8.3/MDClasses}Properties/{http://v8.1c.ru/8.3/MDClasses}Name')
                if auuid and aname:
                    attrs.append((aname, auuid))
            
            if attrs:
                lines.append(f'\t\t<Metadata name="Catalog.{cname}" id="{cuuid}" configVersion="{get_hash(f"Catalog.{cname}")}">')
                for aname, auuid in attrs:
                    lines.append(f'\t\t\t<Metadata name="Catalog.{cname}.Attribute.{aname}" id="{auuid}"/>')
                lines.append('\t\t</Metadata>')
            else:
                lines.append(f'\t\t<Metadata name="Catalog.{cname}" id="{cuuid}" configVersion="{get_hash(f"Catalog.{cname}")}"/>')

# 5. Documents
docs_dir = os.path.join(proj, 'Documents')
if os.path.exists(docs_dir):
    for f in sorted(os.listdir(docs_dir)):
        if f.endswith('.xml'):
            dname = f[:-4]
            dpath = os.path.join(docs_dir, f)
            duuid = get_file_uuid(dpath, 'Document')
            
            tree = ET.parse(dpath)
            root = tree.getroot()
            
            items = []
            doc_elem = root.find('{http://v8.1c.ru/8.3/MDClasses}Document')
            child_objs = doc_elem.find('{http://v8.1c.ru/8.3/MDClasses}ChildObjects') if doc_elem is not None else None
            
            if child_objs is not None:
                for child in child_objs:
                    tag = child.tag.split('}')[-1]
                    if tag == 'Attribute':
                        auuid = child.attrib.get('uuid')
                        aname = child.findtext('{http://v8.1c.ru/8.3/MDClasses}Properties/{http://v8.1c.ru/8.3/MDClasses}Name')
                        items.append(('Attribute', aname, auuid, []))
                    elif tag == 'TabularSection':
                        tuuid = child.attrib.get('uuid')
                        tname = child.findtext('{http://v8.1c.ru/8.3/MDClasses}Properties/{http://v8.1c.ru/8.3/MDClasses}Name')
                        t_attrs = []
                        t_child_objs = child.find('{http://v8.1c.ru/8.3/MDClasses}ChildObjects')
                        if t_child_objs is not None:
                            for tc in t_child_objs:
                                if tc.tag.split('}')[-1] == 'Attribute':
                                    t_attrs.append((tc.findtext('{http://v8.1c.ru/8.3/MDClasses}Properties/{http://v8.1c.ru/8.3/MDClasses}Name'), tc.attrib.get('uuid')))
                        items.append(('TabularSection', tname, tuuid, t_attrs))
            
            if items:
                lines.append(f'\t\t<Metadata name="Document.{dname}" id="{duuid}" configVersion="{get_hash(f"Document.{dname}")}">')
                for itype, iname, iuuid, subitems in items:
                    if itype == 'Attribute':
                        lines.append(f'\t\t\t<Metadata name="Document.{dname}.Attribute.{iname}" id="{iuuid}"/>')
                    elif itype == 'TabularSection':
                        lines.append(f'\t\t\t<Metadata name="Document.{dname}.TabularSection.{iname}" id="{iuuid}"/>')
                        for saname, sauuid in subitems:
                            lines.append(f'\t\t\t<Metadata name="Document.{dname}.TabularSection.{iname}.Attribute.{saname}" id="{sauuid}"/>')
                lines.append('\t\t</Metadata>')
            else:
                lines.append(f'\t\t<Metadata name="Document.{dname}" id="{duuid}" configVersion="{get_hash(f"Document.{dname}")}"/>')
            
            # Forms
            forms_dir = os.path.join(docs_dir, dname, 'Forms')
            if os.path.exists(forms_dir):
                for form_file in sorted(os.listdir(forms_dir)):
                    if form_file.endswith('.xml'):
                        fname = form_file[:-4]
                        form_uuid = get_file_uuid(os.path.join(forms_dir, form_file), 'Form')
                        lines.append(f'\t\t<Metadata name="Document.{dname}.Form.{fname}" id="{form_uuid}" configVersion="{get_hash(f"Document.{dname}.Form.{fname}")}"/>')
                        lines.append(f'\t\t<Metadata name="Document.{dname}.Form.{fname}.Form" id="{form_uuid}.0" configVersion="{get_hash(f"Document.{dname}.Form.{fname}.Form")}"/>')
            
            # ObjectModule
            obj_mod_path = os.path.join(docs_dir, dname, 'Ext', 'ObjectModule.bsl')
            if os.path.exists(obj_mod_path):
                lines.append(f'\t\t<Metadata name="Document.{dname}.ObjectModule" id="{duuid}.0" configVersion="{get_hash(f"Document.{dname}.ObjectModule")}"/>')

# 6. InformationRegisters
ireg_dir = os.path.join(proj, 'InformationRegisters')
if os.path.exists(ireg_dir):
    for f in sorted(os.listdir(ireg_dir)):
        if f.endswith('.xml'):
            rname = f[:-4]
            rpath = os.path.join(ireg_dir, f)
            ruuid = get_file_uuid(rpath, 'InformationRegister')
            
            tree = ET.parse(rpath)
            root = tree.getroot()
            reg_elem = root.find('{http://v8.1c.ru/8.3/MDClasses}InformationRegister')
            child_objs = reg_elem.find('{http://v8.1c.ru/8.3/MDClasses}ChildObjects') if reg_elem is not None else None
            
            items = []
            if child_objs is not None:
                for child in child_objs:
                    tag = child.tag.split('}')[-1]
                    if tag in ['Dimension', 'Resource', 'Attribute']:
                        items.append((tag, child.findtext('{http://v8.1c.ru/8.3/MDClasses}Properties/{http://v8.1c.ru/8.3/MDClasses}Name'), child.attrib.get('uuid')))
            
            if items:
                lines.append(f'\t\t<Metadata name="InformationRegister.{rname}" id="{ruuid}" configVersion="{get_hash(f"InformationRegister.{rname}")}">')
                for itype, iname, iuuid in items:
                    lines.append(f'\t\t\t<Metadata name="InformationRegister.{rname}.{itype}.{iname}" id="{iuuid}"/>')
                lines.append('\t\t</Metadata>')
            else:
                lines.append(f'\t\t<Metadata name="InformationRegister.{rname}" id="{ruuid}" configVersion="{get_hash(f"InformationRegister.{rname}")}"/>')

# 7. AccumulationRegisters
areg_dir = os.path.join(proj, 'AccumulationRegisters')
if os.path.exists(areg_dir):
    for f in sorted(os.listdir(areg_dir)):
        if f.endswith('.xml'):
            rname = f[:-4]
            rpath = os.path.join(areg_dir, f)
            ruuid = get_file_uuid(rpath, 'AccumulationRegister')
            
            tree = ET.parse(rpath)
            root = tree.getroot()
            reg_elem = root.find('{http://v8.1c.ru/8.3/MDClasses}AccumulationRegister')
            child_objs = reg_elem.find('{http://v8.1c.ru/8.3/MDClasses}ChildObjects') if reg_elem is not None else None
            
            items = []
            if child_objs is not None:
                for child in child_objs:
                    tag = child.tag.split('}')[-1]
                    if tag in ['Dimension', 'Resource', 'Attribute']:
                        items.append((tag, child.findtext('{http://v8.1c.ru/8.3/MDClasses}Properties/{http://v8.1c.ru/8.3/MDClasses}Name'), child.attrib.get('uuid')))
            
            if items:
                lines.append(f'\t\t<Metadata name="AccumulationRegister.{rname}" id="{ruuid}" configVersion="{get_hash(f"AccumulationRegister.{rname}")}">')
                for itype, iname, iuuid in items:
                    lines.append(f'\t\t\t<Metadata name="AccumulationRegister.{rname}.{itype}.{iname}" id="{iuuid}"/>')
                lines.append('\t\t</Metadata>')
            else:
                lines.append(f'\t\t<Metadata name="AccumulationRegister.{rname}" id="{ruuid}" configVersion="{get_hash(f"AccumulationRegister.{rname}")}"/>')

# 8. DataProcessors
dp_dir = os.path.join(proj, 'DataProcessors')
if os.path.exists(dp_dir):
    for f in sorted(os.listdir(dp_dir)):
        if f.endswith('.xml'):
            dpname = f[:-4]
            dpath = os.path.join(dp_dir, f)
            duuid = get_file_uuid(dpath, 'DataProcessor')
            lines.append(f'\t\t<Metadata name="DataProcessor.{dpname}" id="{duuid}" configVersion="{get_hash(f"DataProcessor.{dpname}")}"/>')
            
            forms_dir = os.path.join(dp_dir, dpname, 'Forms')
            if os.path.exists(forms_dir):
                for form_file in sorted(os.listdir(forms_dir)):
                    if form_file.endswith('.xml'):
                        fname = form_file[:-4]
                        form_uuid = get_file_uuid(os.path.join(forms_dir, form_file), 'Form')
                        lines.append(f'\t\t<Metadata name="DataProcessor.{dpname}.Form.{fname}" id="{form_uuid}" configVersion="{get_hash(f"DataProcessor.{dpname}.Form.{fname}")}"/>')
                        lines.append(f'\t\t<Metadata name="DataProcessor.{dpname}.Form.{fname}.Form" id="{form_uuid}.0" configVersion="{get_hash(f"DataProcessor.{dpname}.Form.{fname}.Form")}"/>')

lines.append('\t</ConfigVersions>')
lines.append('</ConfigDumpInfo>')

output_path = os.path.join(proj, 'ConfigDumpInfo.xml')
with open(output_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines) + '\n')

print(f'Successfully generated ConfigDumpInfo.xml with {len(lines)} lines!')
