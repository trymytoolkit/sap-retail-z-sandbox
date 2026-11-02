# Génère src/zret_md/sapmzret_art.prog.xml (PROGDIR + DYNPROS + CUA) au format abapGit.
# Les structures RPY_DYHEAD / RPY_DYCATT / RPY_DYFATC ont été relevées sur A4H (RPY_DYNPRO_READ).
import os
P='SAPMZRET_ART'
def n3(v): return f'{int(v):03d}'
def tag(k,v): return f'       <{k}>{v}</{k}>\n'
def cont(type_,name,element_of='',line=0,col=0,length=0,height=0,resize=('','',0,0),scroll=('',''),tc=None):
    x='      <RPY_DYCATT>\n'+'       <TYPE>'+type_+'</TYPE>\n'+'       <NAME>'+name+'</NAME>\n'
    if element_of: x+=tag('ELEMENT_OF',element_of)
    if line or col or length or height:
        x+=tag('LINE',n3(line))+tag('COLUMN',n3(col))+tag('LENGTH',n3(length))+tag('HEIGHT',n3(height))
    if resize[0]: x+=tag('C_RESIZE_V','X')
    if resize[1]: x+=tag('C_RESIZE_H','X')
    if resize[2]: x+=tag('C_LINE_MIN',n3(resize[2]))
    if resize[3]: x+=tag('C_COLN_MIN',n3(resize[3]))
    if scroll[0]: x+=tag('C_SCROLL_V','X')
    if scroll[1]: x+=tag('C_SCROLL_H','X')
    if tc:
        x+=tag('TC_TABTYPE','ENTRY')+tag('TC_SEPAR_V','X')+tag('TC_SEPAR_H','X')+tag('TC_HEADER','X')+tag('TC_CONFIG','X')
        x+=tag('TC_SEL_LNS','MULTIPLE')+tag('TC_SEL_CLS','NONE')+tag('TC_LSEL_CL','X')+tag('TC_FIXCOL',n3(tc))
    return x+'      </RPY_DYCATT>\n'
def fld(ct,cn,type_,name,text='',line=0,col=0,length=0,vis=None,fmt='CHAR',io=False,req=False,fcode='',dd=False,fromdict=False,ref='',tc_head=False,tc_sel=False,ro=False):
    vis=length if vis is None else vis
    x='      <RPY_DYFATC>\n'+tag('CONT_TYPE',ct)+tag('CONT_NAME',cn)+tag('TYPE',type_)+tag('NAME',name)
    if text: x+=tag('TEXT',text.replace('&','&amp;'))
    if dd: x+=tag('DROPDOWN','L')
    x+=tag('LINE',n3(line))+tag('COLUMN',n3(col))+tag('LENGTH',n3(length))+tag('VISLENGTH',n3(vis))+tag('HEIGHT','001')
    if fcode: x+=tag('PUSH_FCODE',fcode)
    x+=tag('FORMAT',fmt)
    if fromdict: x+=tag('FROM_DICT','X')
    if io: x+=tag('INPUT_FLD','X')+tag('OUTPUT_FLD','X')
    if ro: x+=tag('OUTPUT_FLD','X')+tag('OUTPUTONLY','X')
    if req: x+=tag('REQU_ENTRY','X')
    if type_=='TEXT' and not tc_head: x+=tag('LABELLEFT','X')
    if ref: x+=tag('REF_FIELD',ref)
    if tc_head: x+=tag('TC_HEADING','X')
    if tc_sel: x+=tag('TC_SELCOL','X')
    return x+'      </RPY_DYFATC>\n'
def okcode(): return fld('SCREEN','SCREEN','OKCODE','OK_CODE','_'*20,0,0,20,io=False)+''  # input only
def screen(no,descr,type_,lines,cols,containers,fields,next_=None):
    x='    <item>\n     <HEADER>\n'+f'      <PROGRAM>{P}</PROGRAM>\n      <SCREEN>{no}</SCREEN>\n      <LANGUAGE>E</LANGUAGE>\n      <DESCRIPT>{descr}</DESCRIPT>\n      <TYPE>{type_}</TYPE>\n      <NEXTSCREEN>{next_ or no}</NEXTSCREEN>\n      <LINES>{n3(lines)}</LINES>\n      <COLUMNS>{n3(cols)}</COLUMNS>\n     </HEADER>\n'
    x+='     <CONTAINERS>\n'+cont('SCREEN','SCREEN')+''.join(containers)+'     </CONTAINERS>\n'
    x+='     <FIELDS>\n'+''.join(fields)+'     </FIELDS>\n'
    # Flow logic AUSSI dans le XML (les versions d'abapGit antérieures aux
    # fichiers screen_NNNN.abap la lisent ici ; les récentes prennent le fichier).
    flow=open(f'src/zret_md/sapmzret_art.prog.screen_{no}.abap',encoding='utf-8').read().rstrip('\n').split('\n')
    x+='     <FLOW_LOGIC>\n'+''.join(f'      <RPY_DYFLOW>\n       <LINE>{l.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")}</LINE>\n      </RPY_DYFLOW>\n' if l.strip() else '      <RPY_DYFLOW/>\n' for l in flow)+'     </FLOW_LOGIC>\n'
    x+='    </item>\n'
    return x
S=('SCREEN','SCREEN')
def label(text,line,col,length=None):
    return fld(*S,'TEXT','%#AUTOTEXT'+n3(label.n),text,line,col,length or len(text)); 
label.n=0
def lab(text,line,col,length=None):
    label.n+=1; return label(text,line,col,length)
def tmpl(name,line,col,length,vis=None,req=False,fmt='CHAR',dd=False,ct=S):
    return fld(ct[0],ct[1],'TEMPLATE',name,'_'*(vis or length),line,col,length,vis,fmt,io=True,req=req,dd=dd,fromdict=True)
OK=fld(*S,'OKCODE','OK_CODE','_'*20,0,0,20)
OK=OK.replace('      </RPY_DYFATC>\n','       <INPUT_FLD>X</INPUT_FLD>\n      </RPY_DYFATC>\n')
# ---- 0100
s0100=screen('0100','ZMM01: initial screen','N',10,80,[],[
 lab('Article',2,1,10), tmpl('ZRET_S_ART-ARTICLE_ID',2,14,10,req=True),
 fld(*S,'PUSH','BTN_GO','Continue',4,14,12,fcode='GO'), OK])
# ---- 0200 : tabstrip + subscreen area
TS=('STRIP_CTRL','TS_MAIN')
s0200=screen('0200','ZMM01: main screen (tabstrip)','N',24,120,[
 cont('STRIP_CTRL','TS_MAIN','SCREEN',1,1,112,20,resize=('X','X',10,20)),
 cont('SUBSCREEN','SUB_MAIN','TS_MAIN',3,2,108,16,resize=('X','X',8,8),scroll=('X','X'))],[
 fld(*TS,'PUSH','TAB1','Basic data',1,1,14,fcode='TAB1',ref='SUB_MAIN'),
 fld(*TS,'PUSH','TAB2','Sales',1,2,8,fcode='TAB2',ref='SUB_MAIN'),
 fld(*TS,'PUSH','TAB3','Variants',1,3,12,fcode='TAB3',ref='SUB_MAIN'), OK])
# ---- 0210 subscreen basic data
s0210=screen('0210','ZMM01: basic data','S',16,108,[],[
 lab('Article name',2,1,20), tmpl('ZRET_S_ART-ARTICLE_NAME',2,24,40),
 lab('Article type',3,1,20), tmpl('ZRET_S_ART-ARTICLE_TYPE',3,24,4,vis=12,dd=True),
 lab('Base unit',4,1,20), tmpl('ZRET_S_ART-BASE_UOM',4,24,3,fmt='UNIT'),
 fld(*S,'CHECK','ZRET_S_ART-ACTIVE_FLAG','Active',5,24,8,io=True,fromdict=True)])
# ---- 0220 subscreen sales
s0220=screen('0220','ZMM01: sales data','S',16,108,[],[
 lab('Price',2,1,20), tmpl('ZRET_S_ART-PRICE',2,24,17,fmt='DEC'),
 lab('Currency',3,1,20), tmpl('ZRET_S_ART-CURRENCY',3,24,5,fmt='CUKY'),
 lab('Generic article',4,1,20), tmpl('ZRET_S_ART-GENERIC_ARTICLE_ID',4,24,10)])
# ---- 0230 subscreen variants: table control
TC=('TABLE_CTRL','TC_VAR')
cols=[('VARIANT_ID','Variant',4,6),('COLOR','Color',20,12),('SIZE_CODE','Size',6,6),('EAN','EAN',13,13),('PRICE','Price',17,12)]
tcfields=[fld(*TC,'CHECK','ZRET_S_ART_VAR-MARK','',1,0,1,1,io=True,fromdict=True,tc_sel=True)]
for i,(f,t,L,v) in enumerate(cols,1):
    tcfields.append(fld(*TC,'TEXT','H_'+f,t,1,i,v,v,tc_head=True))
for i,(f,t,L,v) in enumerate(cols,1):
    tcfields.append(fld(*TC,'TEMPLATE','ZRET_S_ART_VAR-'+f,'_'*v,1,i,L,v,'DEC' if f=='PRICE' else 'CHAR',io=True,fromdict=True))
s0230=screen('0230','ZMM01: variants (table control)','S',16,108,[
 cont('TABLE_CTRL','TC_VAR','SCREEN',1,1,100,8,resize=('X','X',3,10),scroll=('X','X'),tc=1)],
 tcfields+[fld(*S,'PUSH','BTN_ADD','Add line',10,1,14,fcode='ADD'), fld(*S,'PUSH','BTN_DEL','Delete line',10,17,16,fcode='DEL')])
# ---- CUA : status MAIN, title T_MAIN
funs=[('SAVE','Save','ICON_SYSTEM_SAVE','@2L@'),('BACK','Back','',''),('EXIT','Exit','',''),('CANC','Cancel','ICON_CANCEL','@0W@'),('ENTER','Enter','','')]
def funt(c,t,tn,ic):
    x=f'     <RSMPE_FUNT>\n      <CODE>{c}</CODE>\n      <TEXTNO>001</TEXTNO>\n      <TEXT_TYPE>S</TEXT_TYPE>\n'
    if tn: x+=f'      <TEXT_NAME>{tn}</TEXT_NAME>\n      <ICON_ID>{ic}</ICON_ID>\n'
    return x+f'      <FUN_TEXT>{t}</FUN_TEXT>\n     </RSMPE_FUNT>\n'
pfk=[('00','ENTER'),('03','BACK'),('11','SAVE'),('12','CANC'),('15','EXIT')]
cua='   <CUA>\n    <ADM>\n     <ACTCODE>000001</ACTCODE>\n     <PFKCODE>000001</PFKCODE>\n    </ADM>\n    <STA>\n     <RSMPE_STAT>\n      <CODE>MAIN</CODE>\n      <MODAL>D</MODAL>\n      <ACTCODE>000001</ACTCODE>\n      <PFKCODE>000001</PFKCODE>\n      <BUTCODE>0001</BUTCODE>\n      <INT_NOTE>ZMM01 main status</INT_NOTE>\n     </RSMPE_STAT>\n    </STA>\n'
cua+='    <FUN>\n'+''.join(funt(*f) for f in funs)+'    </FUN>\n'
cua+='    <BUT>\n'+''.join(f'     <RSMPE_BUT>\n      <PFK_CODE>000001</PFK_CODE>\n      <CODE>0001</CODE>\n      <NO>{no}</NO>\n      <PFNO>{pf}</PFNO>\n     </RSMPE_BUT>\n' for no,pf in [('01','11'),('03','03'),('04','15'),('05','12')])+'    </BUT>\n'
cua+='    <PFK>\n'+''.join(f'     <RSMPE_PFK>\n      <CODE>000001</CODE>\n      <PFNO>{pf}</PFNO>\n      <FUNCODE>{fc}</FUNCODE>\n      <FUNNO>001</FUNNO>\n     </RSMPE_PFK>\n' for pf,fc in pfk)+'    </PFK>\n'
cua+='    <SET>\n'+''.join(f'     <RSMPE_STAF>\n      <STATUS>MAIN</STATUS>\n      <FUNCTION>{f[0]}</FUNCTION>\n     </RSMPE_STAF>\n' for f in funs)+'    </SET>\n'
cua+='    <DOC>\n'+''.join(f'     <RSMPE_ATRT>\n      <OBJ_TYPE>{t}</OBJ_TYPE>\n      <OBJ_CODE>000001</OBJ_CODE>\n{sub}      <MODAL>D</MODAL>\n      <INT_NOTE>ZMM01 main status</INT_NOTE>\n     </RSMPE_ATRT>\n' for t,sub in [('A',''),('P',''),('B','      <SUB_CODE>0001</SUB_CODE>\n')])+'    </DOC>\n'
cua+='    <TIT>\n     <RSMPE_TITT>\n      <CODE>T_MAIN</CODE>\n      <TEXT>&amp;1</TEXT>\n     </RSMPE_TITT>\n    </TIT>\n   </CUA>\n'
xml='﻿<?xml version="1.0" encoding="utf-8"?>\n<abapGit version="v1.0.0" serializer="LCL_OBJECT_PROG" serializer_version="v1.0.0">\n <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">\n  <asx:values>\n'
xml+=f'   <PROGDIR>\n    <NAME>{P}</NAME>\n    <DBAPL>S</DBAPL>\n    <SUBC>M</SUBC>\n    <FIXPT>X</FIXPT>\n    <LDBNAME>D$S</LDBNAME>\n    <UCCHECK>X</UCCHECK>\n   </PROGDIR>\n'
xml+='   <DYNPROS>\n'+s0100+s0200+s0210+s0220+s0230+'   </DYNPROS>\n'+cua
xml+='   <TPOOL>\n    <item>\n     <ID>R</ID>\n     <ENTRY>ZMM01: article maintenance (MM01-style test bench)</ENTRY>\n     <LENGTH>50</LENGTH>\n    </item>\n   </TPOOL>\n'
xml+='  </asx:values>\n </asx:abap>\n</abapGit>\n'
open('src/zret_md/sapmzret_art.prog.xml','w',encoding='utf-8',newline='\n').write(xml)
print(len(xml))
