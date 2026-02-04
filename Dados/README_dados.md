Estrutura esperada de dados para execução local:

- Pasta: `Dados/Comma Separated Values Source File/`
- Arquivos CSV por ano com o padrão: `MICRODADOS_CADASTRO_CURSOS_YYYY.CSV`
- Delimitador: `;` (ponto e vírgula)
- Colunas mínimas:
  - `NO_REGIAO`, `SG_UF`, `NO_MUNICIPIO`, `CO_MUNICIPIO`
  - `TP_CATEGORIA_ADMINISTRATIVA`
  - `NO_CINE_AREA_GERAL`, `CO_CINE_AREA_GERAL`
  - `QT_MAT`, `QT_MAT_FEM`
  - `CO_IES`

Uso dos microdados reais:
- O script integra os diretórios `microdados_censo_da_educacao_superior_YYYY/` de 1995 a 2024.
- São lidos automaticamente arquivos como `DADOS/GRADUACAO_PRESENCIAL.CSV`, `GRADUACAO_DISTANCIA.CSV` e `INSTITUICAO.CSV` quando disponíveis.

Varredura automática:
- O script procura por `*CURSOS_YYYY.CSV` recursivamente em toda a pasta `Dados/`.
- Também inspeciona `Documento de Texto/md5_microdados_ed_superior_*.txt` para listar arquivos esperados e sinalizar ausências.
- Detecta anos legados com base nos diretórios `microdados_censo_da_educacao_superior_YYYY/` e integra os CSVs em `DADOS/`.
