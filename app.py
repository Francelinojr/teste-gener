import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import os
import glob
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import re
import io
import pathlib
import zipfile
import argparse
import unicodedata
import json
try:
    import tabulate  # noqa
    HAS_TABULATE = True
except Exception:
    HAS_TABULATE = False
def _to_md(df):
    return df.to_markdown(index=False) if HAS_TABULATE else df.to_string(index=False)

# --- 1. CONSTANTES E MAPPING ---

REGIAO_UF = {
    'AC': 'Norte', 'AP': 'Norte', 'AM': 'Norte', 'PA': 'Norte', 'RO': 'Norte', 'RR': 'Norte', 'TO': 'Norte',
    'AL': 'Nordeste', 'BA': 'Nordeste', 'CE': 'Nordeste', 'MA': 'Nordeste', 'PB': 'Nordeste', 'PE': 'Nordeste', 'PI': 'Nordeste', 'RN': 'Nordeste', 'SE': 'Nordeste',
    'ES': 'Sudeste', 'MG': 'Sudeste', 'RJ': 'Sudeste', 'SP': 'Sudeste',
    'PR': 'Sul', 'RS': 'Sul', 'SC': 'Sul',
    'DF': 'Centro-Oeste', 'GO': 'Centro-Oeste', 'MS': 'Centro-Oeste', 'MT': 'Centro-Oeste'
}
UF_CODE_TO_REGIAO = {
    11: 'Norte', 12: 'Norte', 13: 'Norte', 14: 'Norte', 15: 'Norte', 16: 'Norte', 17: 'Norte',
    21: 'Nordeste', 22: 'Nordeste', 23: 'Nordeste', 24: 'Nordeste', 25: 'Nordeste', 26: 'Nordeste', 27: 'Nordeste', 28: 'Nordeste', 29: 'Nordeste',
    31: 'Sudeste', 32: 'Sudeste', 33: 'Sudeste', 35: 'Sudeste',
    41: 'Sul', 42: 'Sul', 43: 'Sul',
    50: 'Centro-Oeste', 51: 'MT', 52: 'GO', 53: 'DF'
}
UF_CODE_TO_SG = {
    11: 'RO', 12: 'AC', 13: 'AM', 14: 'RR', 15: 'PA', 16: 'AP', 17: 'TO',
    21: 'MA', 22: 'PI', 23: 'CE', 24: 'RN', 25: 'PB', 26: 'PE', 27: 'AL', 28: 'SE', 29: 'BA',
    31: 'MG', 32: 'ES', 33: 'RJ', 35: 'SP',
    41: 'PR', 42: 'SC', 43: 'RS',
    50: 'MS', 51: 'MT', 52: 'GO', 53: 'DF'
}

# Definição de Áreas STEM (CINE/OCDE)
CINE_STEM_CODES = ['05', '06', '07']
CINE_STEM_AREAS = {
    '05': 'Ciências Naturais, Matemática e Estatística',
    '06': 'Tecnologias da Informação e Comunicação (TIC)',
    '07': 'Engenharia, Produção e Construção'
}

# --- 2. FUNÇÕES DE CARREGAMENTO E PRÉ-PROCESSAMENTO ---

def infer_regiao_uf(df):
    """Adiciona colunas de região e UF ao DataFrame, se ausentes."""
    if 'NO_REGIAO' in df.columns:
        return df
    if 'SG_UF' in df.columns:
        df['NO_REGIAO'] = df['SG_UF'].map(REGIAO_UF)
        return df
    if 'CO_UF' in df.columns:
        df['NO_REGIAO'] = df['CO_UF'].map(UF_CODE_TO_REGIAO)
        if 'SG_UF' not in df.columns:
            df['SG_UF'] = df['CO_UF'].map(UF_CODE_TO_SG)
        return df
    if 'CO_MUNICIPIO' in df.columns:
        def _uf_code(x):
            try:
                return int(str(int(x))[:2])
            except Exception:
                return np.nan
        uf_codes = df['CO_MUNICIPIO'].apply(_uf_code)
        df['SG_UF'] = uf_codes.map(UF_CODE_TO_SG)
        df['NO_REGIAO'] = uf_codes.map(UF_CODE_TO_REGIAO)
        return df
    return df

def load_ies_mapping(ano):
    """Carrega dados de IES para mapeamento de microrregião/município."""
    patterns = [f"*IES_{ano}.CSV"]
    paths = []
    for pat in patterns:
        paths += glob.glob(os.path.join(PATH_CSV_DIR, pat))
        paths += glob.glob(os.path.join(PATH_DADOS_DIR, '**', pat), recursive=True)
    for p in paths:
        try:
            df = pd.read_csv(p, sep=';', encoding='latin1', low_memory=False)
            df = infer_regiao_uf(df)
            cols = [c for c in [
                'CO_IES', 'NO_MICRORREGIAO_IES', 'CO_MICRORREGIAO_IES',
                'NO_MUNICIPIO_IES', 'CO_MUNICIPIO_IES', 'SG_UF_IES', 'NO_REGIAO_IES', 'CO_UF_IES'
            ] if c in df.columns]
            return df[cols]
        except Exception:
            continue
    return pd.DataFrame(columns=['CO_IES'])

def identificar_stem(texto):
    """Identifica cursos STEM por palavras-chave (fallback para anos sem CINE)."""
    if pd.isna(texto): return False
    texto = str(texto).upper()
    palavras_chave = [
        'CIÊNCIAS NATURAIS', 'CIENCIAS NATURAIS', 'MATEMÁTICA', 'MATEMATICA', 'ESTATÍSTICA', 'ESTATISTICA',
        'COMPUTAÇÃO', 'COMPUTACAO', 'TIC', 'TECNOLOGIA', 'ENGENHARIA', 'PRODUÇÃO', 'PRODUCAO', 'CONSTRUÇÃO', 'CONSTRUCAO',
        'CIÊNCIAS EXATAS', 'CIENCIAS EXATAS'
    ]
    return any(p in texto for p in palavras_chave)

def load_cursos(ano):
    """Carrega e pré-processa os dados de cursos para um dado ano."""
    try:
        path_csv = CSV_BY_YEAR.get(ano, None)
        if path_csv is not None:
            if args.chunk_size and args.chunk_size > 0:
                cols_base = [
                    'NO_REGIAO','SG_UF','NO_MUNICIPIO','CO_MUNICIPIO','TP_CATEGORIA_ADMINISTRATIVA',
                    'NO_CINE_AREA_GERAL','NO_OCDE_AREA_GERAL','CO_CINE_AREA_GERAL',
                    'QT_MAT','QT_MAT_FEM','QT_ING','QT_CONC','CO_IES'
                ]
                agg_df = None
                for chunk in pd.read_csv(path_csv, sep=';', encoding='latin1', low_memory=False, chunksize=args.chunk_size):
                    chunk = infer_regiao_uf(chunk)
                    cols_present = [c for c in cols_base if c in chunk.columns]
                    ch = chunk[cols_present].copy()
                    col_area = 'NO_CINE_AREA_GERAL' if 'NO_CINE_AREA_GERAL' in ch.columns else ('NO_OCDE_AREA_GERAL' if 'NO_OCDE_AREA_GERAL' in ch.columns else None)
                    if col_area:
                        ch = ch.rename(columns={col_area:'AREA_GERAL'})
                    else:
                        ch['AREA_GERAL'] = np.nan
                    for c in ['QT_MAT','QT_MAT_FEM','QT_ING','QT_CONC']:
                        if c in ch.columns:
                            ch[c] = pd.to_numeric(ch[c], errors='coerce')
                    keys = ['NO_REGIAO','SG_UF','NO_MUNICIPIO','CO_MUNICIPIO','TP_CATEGORIA_ADMINISTRATIVA','AREA_GERAL','CO_CINE_AREA_GERAL','CO_IES']
                    keys = [k for k in keys if k in ch.columns]
                    sums = {}
                    for c in ['QT_MAT','QT_MAT_FEM','QT_ING','QT_CONC']:
                        if c in ch.columns:
                            sums[c] = ('%s'%c,'sum')
                    grp = ch.groupby(keys).agg(**sums).reset_index() if sums else ch
                    if agg_df is None:
                        agg_df = grp
                    else:
                        agg_df = pd.concat([agg_df, grp], ignore_index=True)
                        agg_df = agg_df.groupby(keys).agg(**sums).reset_index() if sums else agg_df
                if agg_df is None:
                    df = pd.DataFrame()
                else:
                    df = agg_df
                df['QT_MAT'] = df['QT_MAT'] if 'QT_MAT' in df.columns else df.get('QT_MAT_FEM', 0)
            else:
                df = pd.read_csv(path_csv, sep=';', encoding='latin1', low_memory=False)
                df = infer_regiao_uf(df)
        else:
            df = pd.DataFrame()
        
        df = df[df['NO_REGIAO'].isin(REGIOES_ALVO)].copy()
        
        # Identifica a coluna de área geral
        col_area = 'NO_CINE_AREA_GERAL' if 'NO_CINE_AREA_GERAL' in df.columns else 'NO_OCDE_AREA_GERAL'
        
        # Colunas a serem mantidas
        cols = [
            'NO_REGIAO', 'SG_UF', 'NO_MUNICIPIO', 'CO_MUNICIPIO', 'TP_CATEGORIA_ADMINISTRATIVA',
            col_area, 'CO_CINE_AREA_GERAL', 'QT_MAT', 'QT_MAT_FEM', 'CO_IES'
        ]
        for c in ['QT_ING', 'QT_CONC']:
            if c in df.columns:
                cols.append(c)
        
        df_clean = df[cols].rename(columns={col_area: 'AREA_GERAL'})
        
        # Merge com dados de IES para informações de microrregião/município
        ies_map = load_ies_mapping(ano)
        if not ies_map.empty:
            if 'CO_IES' in df_clean.columns:
                df_clean = df_clean.merge(ies_map, on='CO_IES', how='left')
            # Preenche dados de município/microrregião do curso com os da IES, se faltarem
            if 'NO_MUNICIPIO_IES' in df_clean.columns:
                df_clean['NO_MUNICIPIO'] = df_clean['NO_MUNICIPIO'].fillna(df_clean['NO_MUNICIPIO_IES'])
            if 'CO_MUNICIPIO_IES' in df_clean.columns:
                df_clean['CO_MUNICIPIO'] = df_clean['CO_MUNICIPIO'].fillna(df_clean['CO_MUNICIPIO_IES'])
        
        df_clean['ANO'] = ano
        for c in ['NO_REGIAO','SG_UF','AREA_GERAL','NO_MUNICIPIO']:
            if c in df_clean.columns:
                df_clean[c] = df_clean[c].astype('category')
        for c in ['QT_MAT','QT_MAT_FEM','QT_ING','QT_CONC','TP_CATEGORIA_ADMINISTRATIVA','CO_MUNICIPIO','CO_CINE_AREA_GERAL']:
            if c in df_clean.columns:
                df_clean[c] = pd.to_numeric(df_clean[c], errors='coerce')
        if not df_clean.empty:
            return df_clean
        legacy = load_legacy_cursos(ano)
        return legacy
    except Exception as e:
        # print(f"Erro ao carregar dados do ano {ano}: {e}")
        return pd.DataFrame()

def load_legacy_cursos(ano):
    base = os.path.join(PATH_DADOS_DIR, f"microdados_censo_da_educacao_superior_{ano}")
    gpaths = glob.glob(os.path.join(base, '**', 'DADOS', 'GRADUACAO_*.CSV'), recursive=True)
    ipaths = glob.glob(os.path.join(base, '**', 'DADOS', 'INSTITUICAO.CSV'), recursive=True)
    if not gpaths:
        return pd.DataFrame()
    dfs = []
    for gp in gpaths:
        try:
            dfg = pd.read_csv(gp, sep='|', encoding='latin1', low_memory=False)
        except Exception:
            try:
                dfg = pd.read_csv(gp, sep=';', encoding='latin1', low_memory=False)
            except Exception:
                continue
        cols_map = {}
        cols_map['NO_REGIAO'] = next((c for c in dfg.columns if c.upper() == 'NO_REGIAO'), None)
        uf_col = next((c for c in dfg.columns if c.upper() in ['SG_UF_CURSO','SG_UF']), None)
        mun_code_col = next((c for c in dfg.columns if c.upper() in ['CODMUNIC','CO_MUNICIPIO','CO_MUNICIPIO_CURSO']), None)
        area_col = next((c for c in dfg.columns if c.upper() in ['NO_AREA_CONHE','AREACURSO','NO_OCDE_AREA_GERAL','NO_CINE_AREA_GERAL']), None)
        ies_id_col = next((c for c in dfg.columns if c.upper() in ['CO_IES','CODIGO_IES','CO_IES_CURSO','MASCARA','ID_IES','CODIGO_INSTITUICAO']), None)
        f_diurno = next((c for c in dfg.columns if c.upper() in ['QT_MAT_ATU_DIU_FEMI','QT_MAT_ATU_DIURNO_FEMI']), None)
        m_diurno = next((c for c in dfg.columns if c.upper() in ['QT_MAT_ATU_DIU_MASC','QT_MAT_ATU_DIURNO_MASC']), None)
        f_not = next((c for c in dfg.columns if c.upper() in ['QT_MAT_ATU_NOT_FEMI','QT_MAT_ATU_NOTURNO_FEMI']), None)
        m_not = next((c for c in dfg.columns if c.upper() in ['QT_MAT_ATU_NOT_MASC','QT_MAT_ATU_NOTURNO_MASC']), None)
        dfg['NO_REGIAO'] = dfg[cols_map['NO_REGIAO']] if cols_map['NO_REGIAO'] else np.nan
        dfg['SG_UF'] = dfg[uf_col] if uf_col else np.nan
        dfg['CO_MUNICIPIO'] = dfg[mun_code_col] if mun_code_col else np.nan
        dfg['AREA_GERAL'] = dfg[area_col] if area_col else np.nan
        if ies_id_col:
            dfg['CO_IES'] = dfg[ies_id_col]
        fem = (pd.to_numeric(dfg[f_diurno], errors='coerce').fillna(0) if f_diurno else 0) + (pd.to_numeric(dfg[f_not], errors='coerce').fillna(0) if f_not else 0)
        masc = (pd.to_numeric(dfg[m_diurno], errors='coerce').fillna(0) if m_diurno else 0) + (pd.to_numeric(dfg[m_not], errors='coerce').fillna(0) if m_not else 0)
        dfg['QT_MAT_FEM'] = fem
        dfg['QT_MAT_MASC'] = masc
        dfg['QT_MAT'] = dfg['QT_MAT_FEM'] + dfg['QT_MAT_MASC']
        dfg['ANO'] = ano
        sel_cols = ['NO_REGIAO','SG_UF','CO_MUNICIPIO','AREA_GERAL','QT_MAT','QT_MAT_FEM','QT_MAT_MASC','ANO'] + (['CO_IES'] if 'CO_IES' in dfg.columns else [])
        dfs.append(dfg[sel_cols])
    df_leg = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
    if df_leg.empty:
        return df_leg
    group_keys = ['NO_REGIAO','SG_UF','CO_MUNICIPIO','AREA_GERAL','ANO'] + (['CO_IES'] if 'CO_IES' in df_leg.columns else [])
    df_leg = df_leg.groupby(group_keys).agg(QT_MAT=('QT_MAT','sum'), QT_MAT_FEM=('QT_MAT_FEM','sum'), QT_MAT_MASC=('QT_MAT_MASC','sum')).reset_index()
    dep_map = None
    if ipaths:
        try:
            dfi = pd.read_csv(ipaths[0], sep='|', encoding='latin1', low_memory=False)
            dep_col = next((c for c in dfi.columns if c.upper() in ['IN_DEP_ADM','TP_CATEGORIA_ADMINISTRATIVA']), None)
            id_ies_i = next((c for c in dfi.columns if c.upper() in ['CO_IES','CODIGO_IES','MASCARA','ID_IES','CODIGO_INSTITUICAO']), None)
            uf_col_i = next((c for c in dfi.columns if c.upper() in ['SG_UF']), None)
            muni_code_i = next((c for c in dfi.columns if c.upper() in ['CODMUNIC','CO_MUNICIPIO']), None)
            muni_name_i = next((c for c in dfi.columns if c.upper() in ['NO_MUNICIPIO']), None)
            cols_sel = [dep_col, uf_col_i, muni_code_i] + ([muni_name_i] if muni_name_i else []) + ([id_ies_i] if id_ies_i else [])
            dep_map = dfi[cols_sel].rename(columns={dep_col:'DEP',uf_col_i:'SG_UF',muni_code_i:'CO_MUNICIPIO', (muni_name_i if muni_name_i else 'NO_MUNICIPIO'):'NO_MUNICIPIO', (id_ies_i if id_ies_i else 'CO_IES'):'CO_IES'})
        except Exception:
            dep_map = None
    if dep_map is not None:
        dep_map['DEP'] = pd.to_numeric(dep_map['DEP'], errors='coerce')
        if 'CO_IES' in df_leg.columns and 'CO_IES' in dep_map.columns:
            df_leg = df_leg.merge(dep_map[['CO_IES','DEP','SG_UF','CO_MUNICIPIO','NO_MUNICIPIO']], on='CO_IES', how='left')
        else:
            df_leg = df_leg.merge(dep_map, on=['SG_UF','CO_MUNICIPIO'], how='left')
        df_leg['TIPO_IES'] = np.where(df_leg['DEP'].fillna(9).astype(int) <= 3, 'Pública', 'Privada')
    else:
        df_leg['TIPO_IES'] = np.nan
    if 'NO_MUNICIPIO' not in df_leg.columns:
        df_leg['NO_MUNICIPIO'] = df_leg['CO_MUNICIPIO'].astype(str)
    return df_leg
# --- 3. ENGENHARIA DE DADOS (FILTROS E CÁLCULOS) ---

# Configuração visual
plt.style.use('ggplot')
plt.rcParams['figure.figsize'] = (12, 6)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PATH_DADOS_DIR = os.path.join(BASE_DIR, 'Dados')
PATH_CSV_DIRS = [
    os.path.join(BASE_DIR, 'Comma Separated Values Source File'),
    os.path.join(BASE_DIR, 'Dados', 'Comma Separated Values Source File'),
    os.path.join(BASE_DIR, 'Dados'),
    os.path.join(os.getcwd(), 'Dados')
]
PATH_CSV_DIR = next((p for p in PATH_CSV_DIRS if os.path.exists(p)), PATH_DADOS_DIR)

def _auto_unzip_microdados(root):
    zips = glob.glob(os.path.join(root, 'microdados_censo_da_educacao_superior_*.zip'))
    for zp in zips:
        target = os.path.splitext(zp)[0]
        if not os.path.exists(target):
            try:
                with zipfile.ZipFile(zp, 'r') as zf:
                    zf.extractall(target)
            except Exception:
                pass

def _collect_csv_by_year(root):
    files = glob.glob(os.path.join(root, '**', '*CURSOS_*.CSV'), recursive=True)
    out = {}
    for f in files:
        m = re.search(r'(\d{4})\.CSV$', os.path.basename(f))
        if m:
            out[int(m.group(1))] = f
    return out

def _collect_legacy_years(root):
    out = set()
    for p in glob.glob(os.path.join(root, 'microdados_censo_da_educacao_superior_*')):
        m = re.search(r'(\d{4})$', p)
        if not m:
            continue
        ano = int(m.group(1))
        grad_paths = glob.glob(os.path.join(p, '**', 'DADOS', 'GRADUACAO_*.CSV'), recursive=True)
        if grad_paths:
            out.add(ano)
    return out

CSV_BY_YEAR = {}
for dirp in PATH_CSV_DIRS:
    if os.path.exists(dirp):
        CSV_BY_YEAR.update(_collect_csv_by_year(dirp))
if CSV_BY_YEAR:
    print(f"Arquivos de cursos detectados: {len(CSV_BY_YEAR)} anos -> {sorted(CSV_BY_YEAR.keys())}")
else:
    print("Nenhum arquivo de cursos encontrado em Dados. Verifique os CSVs.")

_auto_unzip_microdados(PATH_DADOS_DIR)

def _scan_md5_expected_files(base_dir):
    md5_files = glob.glob(os.path.join(base_dir, '**', 'md5_microdados_ed_superior_*.txt'), recursive=True)
    expected = set()
    for f in md5_files:
        try:
            with open(f, 'r', encoding='latin1') as fh:
                for line in fh:
                    m = re.search(r'([A-Za-z0-9_]+\\.CSV)', line)
                    if m:
                        expected.add(m.group(1).upper())
        except Exception:
            continue
    present_paths = glob.glob(os.path.join(base_dir, '**', '*.CSV'), recursive=True)
    present_names = {os.path.basename(p).upper() for p in present_paths}
    found = expected & present_names
    missing = expected - present_names
    print(f"Documento de Texto: esperados={len(expected)} presentes={len(found)} ausentes={len(missing)}")
    return expected, found, missing

_scan_md5_expected_files(PATH_DADOS_DIR)
def _scan_md5_by_year(base_dir):
    files = glob.glob(os.path.join(base_dir, '**', 'MD5_microdados_ed_superior_*.TXT'), recursive=True)
    rows = []
    for fp in files:
        m = re.search(r'(\d{4})', os.path.basename(fp))
        ano = int(m.group(1)) if m else None
        exp = set()
        try:
            with open(fp, 'r', encoding='latin1') as fh:
                for line in fh:
                    mm = re.search(r'([A-Za-z0-9_]+\\.CSV)', line)
                    if mm:
                        exp.add(mm.group(1).upper())
        except Exception:
            pass
        present = set()
        base = os.path.dirname(fp)
        for p in glob.glob(os.path.join(os.path.dirname(os.path.dirname(base)), '**', '*.CSV'), recursive=True):
            if os.path.basename(p).upper() in exp:
                present.add(os.path.basename(p).upper())
        rows.append({'ANO': ano, 'ESPERADOS': len(exp), 'PRESENTES': len(present), 'AUSENTES': len(exp - present), 'ARQUIVOS_AUSENTES': ",".join(sorted(exp - present))})
    df = pd.DataFrame(rows).sort_values('ANO')
    return df

LEGACY_YEARS = _collect_legacy_years(PATH_DADOS_DIR)

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("--anos", type=str)
parser.add_argument("--regioes", type=str)
parser.add_argument("--clusters", type=int)
parser.add_argument("--cine", type=str)
parser.add_argument("--cine-nomes", type=str)
parser.add_argument("--chunk-size", type=int)
parser.add_argument("--saida-dir", type=str)
parser.add_argument("--municipios-top", type=int)
args, _ = parser.parse_known_args()

REGIOES_ALVO = ['Nordeste', 'Sudeste']
if args.regioes:
    REGIOES_ALVO = [s.strip() for s in args.regioes.split(',') if s.strip()]

anos_all = sorted(set(list(CSV_BY_YEAR.keys()) + list(LEGACY_YEARS)))
if args.anos:
    sel_years = []
    s = args.anos.strip()
    if '-' in s:
        a, b = s.split('-', 1)
        try:
            ai = int(a)
            bi = int(b)
            for y in range(ai, bi + 1):
                sel_years.append(y)
        except Exception:
            sel_years = anos_all
    else:
        for part in s.split(','):
            try:
                y = int(part.strip())
                sel_years.append(y)
            except Exception:
                pass
    anos = sorted(sel_years)
else:
    anos = anos_all

N_CLUSTERS = args.clusters if isinstance(args.clusters, int) and args.clusters > 1 else 3
CINE_CODES_SELECTED = []
if args.cine:
    CINE_CODES_SELECTED = [c.strip().zfill(2) for c in args.cine.split(',') if c.strip()]
if args.cine_nomes:
    txt = [t.strip().upper() for t in args.cine_nomes.split(',') if t.strip()]
    name2code = {
        'CIENCIAS NATURAIS': '05', 'CIÊNCIAS NATURAIS': '05', 'MATEMATICA': '05', 'MATEMÁTICA': '05', 'ESTATISTICA': '05', 'ESTATÍSTICA': '05', 'EXATAS': '05',
        'TIC': '06', 'TI': '06', 'TECNOLOGIAS DA INFORMACAO E COMUNICACAO': '06', 'TECNOLOGIAS DA INFORMAÇÃO E COMUNICAÇÃO': '06',
        'ENGENHARIA': '07', 'ENGENHARIA PRODUCAO CONSTRUCAO': '07', 'ENGENHARIA, PRODUÇÃO E CONSTRUÇÃO': '07', 'ENG': '07'
    }
    norm = lambda s: re.sub(r'[^A-Za-z ]', '', ''.join(ch for ch in unicodedata.normalize('NFD', s) if unicodedata.category(ch) != 'Mn')).strip()
    mapped = []
    for n in txt:
        k = norm(n)
        c = name2code.get(k, None)
        if not c:
            if 'EXATAS' in k or 'MAT' in k or 'ESTAT' in k:
                c = '05'
            elif k == 'TI' or 'TIC' in k:
                c = '06'
            elif 'ENG' in k:
                c = '07'
        mapped.append(c)
    CINE_CODES_SELECTED = sorted(set(CINE_CODES_SELECTED) | {c for c in mapped if c is not None})

lista_dfs = []
for ano in anos:
    print(f"Processando {ano}...")
    dfa = load_cursos(ano)
    if not dfa.empty:
        lista_dfs.append(dfa)
df_geral = pd.concat(lista_dfs, ignore_index=True) if len(lista_dfs) > 0 else pd.DataFrame(columns=['ANO'])

if df_geral.empty:
    print("Nenhum dado carregado. Verifique os arquivos CSV.")
    exit()

# Identificação STEM
if 'CO_CINE_AREA_GERAL' in df_geral.columns:
    codes = df_geral['CO_CINE_AREA_GERAL'].astype(str).str.zfill(2)
    by_cine = codes.isin(CINE_STEM_CODES)
    # Usa CINE como primário, fallback para palavras-chave
    df_geral['IS_STEM'] = np.where(df_geral['CO_CINE_AREA_GERAL'].notna(), by_cine, df_geral['AREA_GERAL'].apply(identificar_stem))
else:
    df_geral['IS_STEM'] = df_geral['AREA_GERAL'].apply(identificar_stem)
    
df_stem = df_geral[df_geral['IS_STEM']].copy()

if CINE_CODES_SELECTED and 'CO_CINE_AREA_GERAL' in df_stem.columns:
    df_stem = df_stem[df_stem['CO_CINE_AREA_GERAL'].astype(str).str.zfill(2).isin(CINE_CODES_SELECTED)].copy()

# Definição Pública vs Privada (1,2,3 = Pública)
cat = pd.to_numeric(df_stem['TP_CATEGORIA_ADMINISTRATIVA'], errors='coerce')
df_stem['TIPO_IES'] = np.where(cat.fillna(9).astype(int) <= 3, 'Pública', 'Privada')

# Cálculo da Disparidade de Gênero
df_stem['QT_MAT_MASC'] = df_stem['QT_MAT'] - df_stem['QT_MAT_FEM']

# Agregação por Ano e Região
resumo_anual = df_stem.groupby(['ANO', 'NO_REGIAO']).agg(
    QT_MAT=('QT_MAT', 'sum'),
    QT_MAT_FEM=('QT_MAT_FEM', 'sum'),
    QT_MAT_MASC=('QT_MAT_MASC', 'sum')
).reset_index()

# Cálculo das métricas de gênero
resumo_anual['PCT_MULHERES'] = resumo_anual['QT_MAT_FEM'] / resumo_anual['QT_MAT'] * 100
resumo_anual['PCT_HOMENS'] = resumo_anual['QT_MAT_MASC'] / resumo_anual['QT_MAT'] * 100
# Índice de Paridade de Gênero (IPG): Mulheres / Homens. IPG = 1.0 é paridade.
resumo_anual['IPG_STEM'] = np.where(resumo_anual['QT_MAT_MASC'] > 0, resumo_anual['QT_MAT_FEM'] / resumo_anual['QT_MAT_MASC'], np.nan)

# --- 4. GERAÇÃO DOS GRÁFICOS E TABELAS ---

BASE_OUT = os.path.abspath(args.saida_dir) if args.saida_dir else os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_OUT, 'Imagens_Geradas')
os.makedirs(OUTPUT_DIR, exist_ok=True)
REG_CODE = {'Norte':'NO','Nordeste':'NE','Sudeste':'SE','Sul':'SU','Centro-Oeste':'CO'}
parts = []
if CINE_CODES_SELECTED:
    parts.append("_cine_" + "_".join(CINE_CODES_SELECTED))
if args.anos:
    parts.append(f"_anos_{anos[0]}_{anos[-1]}")
if REGIOES_ALVO:
    parts.append("_regs_" + "-".join(REG_CODE.get(r, r.upper()) for r in REGIOES_ALVO))
parts.append(f"_k{N_CLUSTERS}")
SFX = "".join(parts)
FILTER_STR = []
if CINE_CODES_SELECTED:
    FILTER_STR.append("CINE=" + ",".join(CINE_CODES_SELECTED))
else:
    FILTER_STR.append("CINE=STEM")
FILTER_STR.append(f"Anos={anos[0]}–{anos[-1]}")
FILTER_STR.append("Regiões=" + ",".join(REG_CODE.get(r, r.upper()) for r in REGIOES_ALVO))
FILTER_STR.append(f"k={N_CLUSTERS}")
FILTER_STR = " | ".join(FILTER_STR)
TABLES_DIR = os.path.join(BASE_OUT, 'Tabelas_Geradas')
os.makedirs(TABLES_DIR, exist_ok=True)
def _save_table(df, name):
    try:
        df.to_csv(os.path.join(TABLES_DIR, f"{name}.csv"), index=False, sep=';')
    except Exception:
        pass
    try:
        if HAS_TABULATE:
            with open(os.path.join(TABLES_DIR, f"{name}.md"), 'w', encoding='utf-8') as fh:
                fh.write(df.to_markdown(index=False))
        else:
            with open(os.path.join(TABLES_DIR, f"{name}.md"), 'w', encoding='utf-8') as fh:
                fh.write(df.to_string(index=False))
    except Exception:
        pass
def _save_json(obj, name):
    try:
        with open(os.path.join(TABLES_DIR, f"{name}.json"), 'w', encoding='utf-8') as fh:
            json.dump(obj, fh, ensure_ascii=False, indent=2)
    except Exception:
        pass
_save_json({
    'cine_codes': CINE_CODES_SELECTED if CINE_CODES_SELECTED else CINE_STEM_CODES,
    'anos': [anos[0], anos[-1]],
    'regioes': REGIOES_ALVO,
    'clusters': N_CLUSTERS,
    'sufixo': SFX,
    'titulo_filtros': FILTER_STR
}, "filtros_aplicados" + SFX)

# GRÁFICO 1: Evolução da Disparidade (IPG)
plt.figure(figsize=(12, 7))
for reg in resumo_anual['NO_REGIAO'].unique():
    d = resumo_anual[resumo_anual['NO_REGIAO'] == reg]
    plt.plot(d['ANO'], d['IPG_STEM'], marker='o', linewidth=2.5, label=reg)

plt.axhline(1.0, color='red', linestyle='--', linewidth=1, label='Paridade (IPG=1.0)')
plt.title('Evolução do Índice de Paridade de Gênero (IPG) em STEM: Nordeste vs Sudeste\n' + FILTER_STR, fontsize=14)
plt.ylabel('Índice de Paridade de Gênero (Mulheres/Homens)')
plt.xlabel('Ano')
plt.ylim(0, 1.5)
plt.legend(title='Região')
plt.grid(True, alpha=0.3)
plt.tight_layout()
ipg_filename = "evolucao_ipg_stem_NE_SE" + SFX + ".png"
plt.savefig(os.path.join(OUTPUT_DIR, ipg_filename), dpi=150)
plt.close()

plt.figure(figsize=(12, 7))
for reg in resumo_anual['NO_REGIAO'].unique():
    d = resumo_anual[resumo_anual['NO_REGIAO'] == reg]
    plt.plot(d['ANO'], d['PCT_MULHERES'], marker='o', linewidth=2.5, label=reg)
plt.title('Evolução de % Mulheres em STEM: Nordeste vs Sudeste\n' + FILTER_STR, fontsize=14)
plt.ylabel('% de Mulheres em STEM')
plt.xlabel('Ano')
plt.ylim(0, 60)
plt.legend(title='Região')
plt.gca().yaxis.set_major_formatter(PercentFormatter(100))
plt.grid(True, alpha=0.3)
plt.tight_layout()
pct_filename = "evolucao_pct_mulheres_stem_NE_SE" + SFX + ".png"
plt.savefig(os.path.join(OUTPUT_DIR, pct_filename), dpi=150)
plt.close()

# GRÁFICO 2: Comparação Pública vs Privada (Foco no último ano) - PCT_MULHERES
ano_ref = anos[-1]
resumo_tipo = df_stem.groupby(['ANO', 'NO_REGIAO', 'TIPO_IES']).agg(
    QT_MAT=('QT_MAT', 'sum'),
    QT_MAT_FEM=('QT_MAT_FEM', 'sum')
).reset_index()
resumo_tipo['PCT_MULHERES'] = resumo_tipo['QT_MAT_FEM'] / resumo_tipo['QT_MAT'] * 100

plt.figure(figsize=(10, 6))
dt = resumo_tipo[resumo_tipo['ANO'] == ano_ref] # Último ano
pivot_tipo = dt.pivot_table(index='NO_REGIAO', columns='TIPO_IES', values='PCT_MULHERES')
idx = np.arange(len(pivot_tipo.index))
width = 0.35
plt.bar(idx - width/2, pivot_tipo.get('Pública', pd.Series(index=pivot_tipo.index, dtype=float)), width, label='Pública', color='#1f77b4')
plt.bar(idx + width/2, pivot_tipo.get('Privada', pd.Series(index=pivot_tipo.index, dtype=float)), width, label='Privada', color='#ff7f0e')
plt.xticks(idx, pivot_tipo.index)
plt.title(f'Geografia da Desigualdade: % Mulheres em STEM por Tipo de IES ({ano_ref})\n' + FILTER_STR, fontsize=14)
plt.ylabel('% de Mulheres em STEM')
plt.xlabel('Região')
plt.ylim(0, 60)
plt.legend(title='Categoria Administrativa')
plt.gca().yaxis.set_major_formatter(PercentFormatter(100))
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
ies_filename = f"pct_mulheres_stem_tipo_IES_{ano_ref}" + SFX + ".png"
plt.savefig(os.path.join(OUTPUT_DIR, ies_filename), dpi=150)
plt.close()

print(f"Código executado. Gráficos salvos em: {OUTPUT_DIR}")
def _consistency_summary(df, group_cols):
    x = df.copy()
    x['ERR_IPG_NEG'] = x['IPG_STEM'] < 0
    x['ERR_PCT_OUT'] = (x['PCT_MULHERES'] < 0) | (x['PCT_MULHERES'] > 100)
    agg = x.groupby(group_cols).agg(
        REGISTROS=('IPG_STEM','size'),
        IPG_NEG=('ERR_IPG_NEG','sum'),
        PCT_FORA=('ERR_PCT_OUT','sum')
    ).reset_index()
    return agg

print("\n--- Tabela de Evolução da Disparidade (IPG) ---")
print(_to_md(resumo_anual[['ANO', 'NO_REGIAO', 'QT_MAT', 'QT_MAT_FEM', 'QT_MAT_MASC', 'PCT_MULHERES', 'IPG_STEM']]))
_save_table(resumo_anual[['ANO', 'NO_REGIAO', 'QT_MAT', 'QT_MAT_FEM', 'QT_MAT_MASC', 'PCT_MULHERES', 'IPG_STEM']], f"tabela_evolucao_ipg_{anos[0]}_{ano_ref}{SFX}")

print("\n--- Classificação de Cursos STEM ---")
print(_to_md(pd.DataFrame(CINE_STEM_AREAS.items(), columns=['Código CINE', 'Área de Estudo'])))
_save_table(pd.DataFrame(CINE_STEM_AREAS.items(), columns=['Código CINE', 'Área de Estudo']), "classificacao_cine_stem" + SFX)

# --- 5. Geração de Tabela de Disparidade por Área STEM (Último Ano) ---
df_stem_area = df_stem[df_stem['ANO'] == ano_ref].copy()
df_stem_area['AREA_CINE'] = df_stem_area['CO_CINE_AREA_GERAL'].astype(str).str.zfill(2).map(CINE_STEM_AREAS)

resumo_area = df_stem_area.groupby(['NO_REGIAO', 'AREA_CINE']).agg(
    QT_MAT=('QT_MAT', 'sum'),
    QT_MAT_FEM=('QT_MAT_FEM', 'sum'),
    QT_MAT_MASC=('QT_MAT_MASC', 'sum')
).reset_index()

resumo_area['PCT_MULHERES'] = resumo_area['QT_MAT_FEM'] / resumo_area['QT_MAT'] * 100
resumo_area['IPG_STEM'] = np.where(resumo_area['QT_MAT_MASC'] > 0, resumo_area['QT_MAT_FEM'] / resumo_area['QT_MAT_MASC'], np.nan)

print(f"\n--- Tabela de Disparidade por Área STEM e Região ({ano_ref}) ---")
print(_to_md(resumo_area[['NO_REGIAO', 'AREA_CINE', 'QT_MAT', 'PCT_MULHERES', 'IPG_STEM']].sort_values(by=['NO_REGIAO', 'IPG_STEM'], ascending=[True, False])))
_save_table(resumo_area[['NO_REGIAO', 'AREA_CINE', 'QT_MAT', 'PCT_MULHERES', 'IPG_STEM']].sort_values(by=['NO_REGIAO', 'IPG_STEM'], ascending=[True, False]), f"tabela_disparidade_area_{ano_ref}{SFX}")

# Tabela 4: Comparação Pública vs Privada (Último Ano)
resumo_tipo = df_stem.groupby(['ANO', 'NO_REGIAO', 'TIPO_IES']).agg(
    QT_MAT=('QT_MAT', 'sum'),
    QT_MAT_FEM=('QT_MAT_FEM', 'sum'),
    QT_MAT_MASC=('QT_MAT_MASC', 'sum')
).reset_index()
resumo_tipo['PCT_MULHERES'] = resumo_tipo['QT_MAT_FEM'] / resumo_tipo['QT_MAT'] * 100
resumo_tipo['IPG_STEM'] = np.where(resumo_tipo['QT_MAT_MASC'] > 0, resumo_tipo['QT_MAT_FEM'] / resumo_tipo['QT_MAT_MASC'], np.nan)

print(f"\n--- Tabela de Disparidade por Tipo de IES e Região ({ano_ref}) ---")
print(_to_md(resumo_tipo[resumo_tipo['ANO'] == ano_ref][['NO_REGIAO', 'TIPO_IES', 'QT_MAT', 'PCT_MULHERES', 'IPG_STEM']].sort_values(by=['NO_REGIAO', 'TIPO_IES'])))
_save_table(resumo_tipo[resumo_tipo['ANO'] == ano_ref][['NO_REGIAO', 'TIPO_IES', 'QT_MAT', 'PCT_MULHERES', 'IPG_STEM']].sort_values(by=['NO_REGIAO', 'TIPO_IES']), f"tabela_disparidade_tipo_ies_{ano_ref}{SFX}")

df_mun = df_stem[df_stem['ANO'] == ano_ref].copy()
cols_needed = ['NO_MUNICIPIO', 'NO_REGIAO', 'QT_MAT', 'QT_MAT_FEM', 'QT_MAT_MASC']
df_mun = df_mun[cols_needed]
df_mun = df_mun.groupby(['NO_MUNICIPIO', 'NO_REGIAO']).agg(
    QT_MAT=('QT_MAT', 'sum'),
    QT_MAT_FEM=('QT_MAT_FEM', 'sum'),
    QT_MAT_MASC=('QT_MAT_MASC', 'sum')
).reset_index()
df_mun['IPG_STEM'] = np.where(df_mun['QT_MAT_MASC'] > 0, df_mun['QT_MAT_FEM'] / df_mun['QT_MAT_MASC'], np.nan)
df_mun['PCT_MULHERES'] = df_mun['QT_MAT_FEM'] / df_mun['QT_MAT'] * 100
df_mun = df_mun.replace([np.inf, -np.inf], np.nan).dropna(subset=['IPG_STEM', 'QT_MAT'])
if len(df_mun) >= 3:
    feats = df_mun[['IPG_STEM', 'QT_MAT', 'PCT_MULHERES']].values
    scaler = StandardScaler()
    X = scaler.fit_transform(feats)
    km = KMeans(n_clusters=N_CLUSTERS, n_init=10, random_state=42)
    df_mun['CLUSTER'] = km.fit_predict(X)
    
    plt.figure(figsize=(12, 7))
    colors = {0: '#2ca02c', 1: '#1f77b4', 2: '#d62728'}
    for reg in ['Nordeste', 'Sudeste']:
        sub = df_mun[df_mun['NO_REGIAO'] == reg]
        plt.scatter(sub['IPG_STEM'], sub['QT_MAT'], 
                    c=sub['CLUSTER'].map(colors), 
                    s=np.clip(sub['QT_MAT']/10, 20, 300), 
                    alpha=0.8, label=reg)
    plt.axvline(1.0, color='gray', linestyle='--', linewidth=1)
    plt.title(f'Clusterização K-Means de Desigualdade em STEM por Município ({ano_ref})\n' + FILTER_STR)
    plt.xlabel('Índice de Paridade de Gênero (IPG)')
    plt.ylabel('Total de Matrículas em STEM')
    plt.legend(title='Região')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    cluster_filename = f"clusters_municipio_stem_{ano_ref}" + SFX + ".png"
    plt.savefig(os.path.join(OUTPUT_DIR, cluster_filename), dpi=150)
    plt.close()
    
    print(f"\n--- Clusterização por Município ({ano_ref}) ---")
    print(_to_md(df_mun[['NO_MUNICIPIO', 'NO_REGIAO', 'QT_MAT', 'PCT_MULHERES', 'IPG_STEM', 'CLUSTER']].sort_values(['NO_REGIAO','CLUSTER','NO_MUNICIPIO'])))
    _save_table(df_mun[['NO_MUNICIPIO', 'NO_REGIAO', 'QT_MAT', 'PCT_MULHERES', 'IPG_STEM', 'CLUSTER']].sort_values(['NO_REGIAO','CLUSTER','NO_MUNICIPIO']), f"tabela_cluster_municipio_{ano_ref}{SFX}")
    top_n = args.municipios_top if isinstance(args.municipios_top, int) and args.municipios_top > 0 else 10
    top_ipg = df_mun.sort_values('IPG_STEM', ascending=False).head(top_n)
    print("\n--- Top municípios por IPG ---")
    print(_to_md(top_ipg[['NO_MUNICIPIO', 'NO_REGIAO', 'QT_MAT', 'PCT_MULHERES', 'IPG_STEM']]))
    _save_table(top_ipg[['NO_MUNICIPIO', 'NO_REGIAO', 'QT_MAT', 'PCT_MULHERES', 'IPG_STEM']], f"top_municipios_ipg_{ano_ref}{SFX}")
    top_pct = df_mun.sort_values('PCT_MULHERES', ascending=False).head(top_n)
    print("\n--- Top municípios por % Mulheres ---")
    print(_to_md(top_pct[['NO_MUNICIPIO', 'NO_REGIAO', 'QT_MAT', 'PCT_MULHERES', 'IPG_STEM']]))
    _save_table(top_pct[['NO_MUNICIPIO', 'NO_REGIAO', 'QT_MAT', 'PCT_MULHERES', 'IPG_STEM']], f"top_municipios_pct_{ano_ref}{SFX}")
    
    def _norm_mun(x):
        s = unicodedata.normalize('NFD', str(x))
        s = ''.join(ch for ch in s if unicodedata.category(ch) != 'Mn')
        return s.upper().strip()
    coords_path = os.path.join(PATH_DADOS_DIR, 'municipios_coords.csv')
    COORDS = {}
    if os.path.exists(coords_path):
        try:
            dcm = pd.read_csv(coords_path, sep=';', encoding='latin1', low_memory=False)
            dcm['NORM'] = dcm['NO_MUNICIPIO'].apply(_norm_mun)
            for _, r in dcm[['NORM','LON','LAT']].iterrows():
                COORDS[r['NORM']] = (float(r['LON']), float(r['LAT']))
        except Exception:
            COORDS = {}
    if not COORDS:
        COORDS = {
            'FORTALEZA': (-38.54, -3.73),
            'RECIFE': (-34.88, -8.05),
            'SALVADOR': (-38.50, -12.97),
            'RIO DE JANEIRO': (-43.21, -22.90),
            'SAO PAULO': (-46.63, -23.55),
            'BELO HORIZONTE': (-43.94, -19.92),
            'NATAL': (-35.21, -5.80),
            'JOAO PESSOA': (-34.87, -7.12),
            'MACEIO': (-35.74, -9.65),
            'ARACAJU': (-37.07, -10.91),
            'TERESINA': (-42.81, -5.09),
            'SAO LUIS': (-44.30, -2.53),
            'VITORIA': (-40.32, -20.32)
        }
    df_mun['NORM'] = df_mun['NO_MUNICIPIO'].apply(_norm_mun)
    df_geo = df_mun[df_mun['NORM'].isin(COORDS.keys())].copy()
    if not df_geo.empty:
        df_geo['LON'] = df_geo['NORM'].apply(lambda k: COORDS[k][0])
        df_geo['LAT'] = df_geo['NORM'].apply(lambda k: COORDS[k][1])
        if os.path.exists(coords_path):
            try:
                dcm = pd.read_csv(coords_path, sep=';', encoding='latin1', low_memory=False)
                dcm['NORM'] = dcm['NO_MUNICIPIO'].apply(_norm_mun)
                df_geo = df_geo.merge(dcm[['NORM','POP','QT_CURSO']], on='NORM', how='left')
            except Exception:
                pass
        plt.figure(figsize=(10, 8))
        size_series = None
        if 'POP' in df_geo.columns and df_geo['POP'].notna().any():
            size_series = np.clip(df_geo['POP'].fillna(0)/1000, 40, 500)
        elif 'QT_CURSO' in df_geo.columns and df_geo['QT_CURSO'].notna().any():
            size_series = np.clip(df_geo['QT_CURSO'].fillna(0)*10, 30, 400)
        else:
            size_series = np.clip(df_geo['PCT_MULHERES']*5, 50, 300)
        sc = plt.scatter(df_geo['LON'], df_geo['LAT'], c=df_geo['IPG_STEM'], s=size_series, cmap='viridis', alpha=0.85)
        for _, r in df_geo.iterrows():
            plt.text(r['LON']+0.2, r['LAT']+0.1, f"{r['NO_MUNICIPIO']}\\nIPG={r['IPG_STEM']:.2f}, %={r['PCT_MULHERES']:.0f}", fontsize=9)
        plt.colorbar(sc, label='IPG')
        plt.title(f"Mapa temático por município: IPG e % mulheres ({ano_ref})\n" + FILTER_STR)
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        mapa_filename = f"mapa_tematico_municipio_stem_{ano_ref}" + SFX + ".png"
        plt.savefig(os.path.join(OUTPUT_DIR, mapa_filename), dpi=150)
        plt.close()
else:
    print("\nAmostra municipal insuficiente para clusterização (mínimo de 3 registros).")
md5_df = _scan_md5_by_year(PATH_DADOS_DIR)
if not md5_df.empty:
    print("\n--- Completude de arquivos por ano (MD5) ---")
    print(_to_md(md5_df[['ANO','ESPERADOS','PRESENTES','AUSENTES']]))
    _save_table(md5_df, "md5_completude_por_ano" + SFX)
cons_reg = _consistency_summary(resumo_anual, ['ANO','NO_REGIAO'])
print("\n--- Resumo de Consistência (IPG e % mulheres) ---")
print(_to_md(cons_reg.sort_values(['ANO','NO_REGIAO'])))
_save_table(cons_reg.sort_values(['ANO','NO_REGIAO']), "consistencia_genero" + SFX)
