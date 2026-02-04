# Geografia da Desigualdade: Um Estudo de Clusters sobre a Participação Feminina em STEM no Nordeste vs. Sudeste

## Objetivo Principal
- Investigar a participação feminina em cursos STEM no Ensino Superior brasileiro, comparando as regiões Nordeste e Sudeste, com foco em métricas de paridade de gênero e padrões espaciais (clusters) por município.

## Objetivos Específicos
- Calcular o Índice de Paridade de Gênero (IPG = Matrículas Femininas / Masculinas) em STEM por região e ano.
- Comparar a participação feminina por tipo de IES (Pública vs. Privada).
- Caracterizar clusters municipais de desigualdade com base em IPG, matrículas e % mulheres.
- Produzir gráficos e tabelas reprodutíveis a partir de microdados do INEP.

## Metodologia
- Fontes de dados:
  - Microdados do Censo da Educação Superior (INEP), arquivos CSV com o cadastro de cursos por ano.
  - Classificação de cursos STEM com base nas áreas gerais CINE/OCDE: 05 (Ciências Naturais, Matemática e Estatística), 06 (TIC) e 07 (Engenharia).
- Processamento:
  - Leitura e pré-processamento dos microdados em [app.py](file:///f:/arquivos/Geografia-da-Desigualdade-main/Geografia-da-Desigualdade-main/app.py).
  - Filtros: seleção das regiões Nordeste e Sudeste; identificação STEM via códigos CINE e palavras-chave de respaldo.
  - Agregações: por ano e região; por tipo de IES; por município (último ano).
  - Clusterização: K-Means com 3 grupos, atributos padronizados (IPG, QT_MAT, PCT_MULHERES).
- Especificidades:
  - Estrutura esperada de dados em `Dados/Comma Separated Values Source File/` com padrão `MICRODADOS_CADASTRO_CURSOS_YYYY.CSV`.
  - Amostra mínima para clusterização municipal: ≥ 3 municípios no último ano.

## Resultados (Iniciais)
- Linhas do tempo e comparações regionais são geradas automaticamente em `Imagens_Geradas/` ao executar o script:
  - Evolução do IPG: `evolucao_ipg_stem_NE_SE.png`.
  - Evolução de % Mulheres: `evolucao_pct_mulheres_stem_NE_SE.png`.
  - % Mulheres por tipo de IES (último ano): `pct_mulheres_stem_tipo_IES_YYYY.png`.
  - Clusterização municipal K-Means (último ano): `clusters_municipio_stem_YYYY.png`.
- Tabelas analíticas impressas no console:
  - Evolução anual por região (IPG, % mulheres).
  - Disparidade por área CINE e região (último ano).
  - Comparação Pública vs. Privada por região (último ano).
  - Rankings municipais (último ano): `top_municipios_ipg_YYYY*` e `top_municipios_pct_YYYY*`.
 - Relatórios auxiliares salvos em `Tabelas_Geradas/`:
   - `md5_completude_por_ano*.csv|.md`: presença de arquivos esperados por ano, conforme manifesto MD5.
   - `consistencia_genero*.csv|.md`: contagem de registros com IPG negativo e % mulheres fora de 0–100.

## Reprodutibilidade
- Dependências: pandas, numpy, matplotlib, scikit-learn.
- Execução:
  1. Coloque os CSVs do INEP em `Dados/Comma Separated Values Source File/`.
  2. Execute: `python app.py`.
  3. Verifique as imagens em `Imagens_Geradas/` e os prints de tabelas no terminal.
 - Filtros aplicados e sufixos:
   - Os artefatos são gerados com sufixos que codificam os filtros utilizados: `_cine_{codes}_anos_{YYYY_início}_{YYYY_fim}_regs_{NO-NE-...}_k{clusters}`.
   - Exemplo de string de filtros incorporada aos títulos: `CINE=05,06 | Anos=2010–2024 | Regiões=NE,SE | k=3`.
 - Seleção via CLI:
   - `--anos`: intervalo ou lista (ex.: `--anos 2010-2024` ou `--anos 2005,2012,2020`).
   - `--regioes`: lista (ex.: `--regioes Nordeste,Sudeste`).
   - `--cine`: códigos CINE (ex.: `--cine 05,07`).
   - `--cine-nomes`: nomes livres (ex.: `--cine-nomes TI,Engenharia,Exatas`), com normalização automática.
   - `--chunk-size`: leitura em chunks para CSVs grandes.
  - `--saida-dir`: define diretório base para salvar imagens/tabelas.
  - `--municipios-top`: número de municípios nos rankings do último ano.
