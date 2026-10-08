"""Disassemble selected sts2 managed methods without loading/executing the game."""
from pathlib import Path
import dnfile, hashlib, json, re, sys
from dncil.cil.body.reader import read_method_body_from_bytes
from dncil.clr.token import Token, StringToken

DLL=Path('/mnt/c/Program Files (x86)/Steam/steamapps/common/Slay the Spire 2/data_sts2_windows_x86_64/sts2.dll')
pe=dnfile.dnPE(str(DLL))
owners={}
typenames={id(t):f'{t.TypeNamespace}.{t.TypeName}'.strip('.') for t in pe.net.mdtables.TypeDef}
if pe.net.mdtables.NestedClass:
    for nested in pe.net.mdtables.NestedClass:
        child=nested.NestedClass.row; parent=nested.EnclosingClass.row
        typenames[id(child)]=typenames[id(parent)]+'+'+str(child.TypeName)
for t in pe.net.mdtables.TypeDef:
    name=typenames[id(t)]
    for m in t.MethodList: owners[(6,m.row_index)]=name
    for f in t.FieldList: owners[(4,f.row_index)]=name

def resolve(token):
    if isinstance(token,StringToken):
        val=pe.net.user_strings.get(token.rid)
        return json.dumps(str(val.value) if val else '<missing>',ensure_ascii=False)
    if not isinstance(token,Token):return str(token)
    table=pe.net.mdtables.tables.get(token.table)
    if not table or token.rid<1 or token.rid>len(table.rows): return str(token)
    row=table.rows[token.rid-1]
    if token.table in (4,6):return owners.get((token.table,token.rid),'?')+'::'+str(row.Name)
    if token.table in (1,2):return str(row.TypeNamespace)+'.'+str(row.TypeName)
    if token.table==10:
        c=row.Class
        base=getattr(c.row,'TypeNamespace','')
        cls=getattr(c.row,'TypeName',getattr(c.row,'Name','?'))
        return f'{base}.{cls}::{row.Name}'
    if token.table==43:return resolve(Token((row.Method.table.number<<24)|row.Method.row_index))+'<generic>'
    return str(token)

def dump(pattern):
    for t in pe.net.mdtables.TypeDef:
        n=typenames[id(t)]
        if not re.search(pattern,n):continue
        if n.endswith(('+MethodName','+PropertyName','+SignalName')):continue
        print('TYPE',n)
        for m in t.MethodList:
            row=m.row
            if not row.Rva or str(row.Name).startswith(('GetGodot','InvokeGodot','HasGodot','SetGodot','SaveGodot','RestoreGodot')):continue
            print(f'\nMETHOD {n}::{row.Name} [MethodDef 0x{0x06000000|m.row_index:08x}, RVA 0x{row.Rva:x}]')
            body=read_method_body_from_bytes(pe.get_data(row.Rva,200000))
            for ins in body.instructions:
                print(f'IL_{ins.offset:04x}: {ins.opcode.name} {resolve(ins.operand) if ins.operand is not None else ""}'.rstrip())

def calls(pattern):
    out=[]
    for t in pe.net.mdtables.TypeDef:
        n=typenames[id(t)]
        if n.endswith(('+MethodName','+PropertyName','+SignalName')):continue
        for m in t.MethodList:
            row=m.row
            if not row.Rva or str(row.Name).startswith(('GetGodot','InvokeGodot','HasGodot','SetGodot','SaveGodot','RestoreGodot')):continue
            body=read_method_body_from_bytes(pe.get_data(row.Rva,200000))
            targets=[{'offset':i.offset,'target':resolve(i.operand)} for i in body.instructions if i.opcode.name.startswith(('call','newobj')) and re.search(pattern,resolve(i.operand))]
            if targets:
                out.append({'method':n+'::'+str(row.Name),'token':f'0x{0x06000000|m.row_index:08x}','rva':hex(row.Rva),'calls':targets,'strings':[{'offset':i.offset,'value':resolve(i.operand)} for i in body.instructions if i.opcode.name=='ldstr']})
    print(json.dumps(out,indent=2,ensure_ascii=False))

if __name__=='__main__':
    if sys.argv[1]=='calls':calls(sys.argv[2])
    else:dump(sys.argv[1])
