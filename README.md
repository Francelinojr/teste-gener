# Geografia da Desigualdade: Um Estudo de Clusters sobre a Participação Feminina em STEM no Nordeste vs. Sudeste

Este artigo apresenta uma análise aprofundada da **disparidade de gênero** na área de Ciência, Tecnologia, Engenharia e Matemática (**STEM**) no Ensino Superior brasileiro, com foco na comparação entre as regiões **Nordeste** e **Sudeste** no período de 2010 a 2024.

A análise se concentra no **Índice de Paridade de Gênero (IPG)**, que mede a razão entre o número de matrículas femininas e masculinas (IPG = Matrículas Femininas / Matrículas Masculinas). Um IPG igual a 1.0 indica paridade, enquanto valores abaixo de 1.0 indicam maior participação masculina.

## Relatório Técnico
- Estrutura detalhada com Título, Objetivo principal, Objetivos específicos, Metodologia e Resultados iniciais está disponível em [Relatorio_Tecnico.md](file:///f:/arquivos/Geografia-da-Desigualdade-main/Geografia-da-Desigualdade-main/Relatorio_Tecnico.md).
- O código lê automaticamente os microdados reais em `Dados/microdados_censo_da_educacao_superior_YYYY/` (1995–2024), além de quaisquer CSVs em `Dados/` que sigam o padrão `*CURSOS_YYYY.CSV`. Execute [app.py](file:///f:/arquivos/Geografia-da-Desigualdade-main/Geografia-da-Desigualdade-main/app.py) e as imagens serão salvas em `Imagens_Geradas/`.

## 1. Metodologia e Classificação de Cursos STEM

Os dados utilizados provêm dos microdados do Censo da Educação Superior do INEP. A classificação dos cursos STEM foi realizada com base nas áreas gerais CINE/OCDE, conforme detalhado na tabela a seguir:

| Código CINE | Área de Estudo |
| --- | --- |
| 05 | Ciências Naturais, Matemática e Estatística |
| 06 | Tecnologias da Informação e Comunicação (TIC) |
| 07 | Engenharia, Produção e Construção |

## 2. Evolução da Disparidade Regional (2010-2024)

A análise da série histórica revela a trajetória da participação feminina nas duas regiões. O gráfico de evolução do IPG mostra que, historicamente, o Nordeste tem mantido um índice de paridade ligeiramente superior ao Sudeste, desafiando a percepção de que regiões mais desenvolvidas teriam indicadores de diversidade melhores.

**Gráfico 1: Evolução do Índice de Paridade de Gênero (IPG) em STEM: Nordeste vs Sudeste**

*Nota: O gráfico abaixo representa a evolução temporal da participação feminina em STEM, comparando as regiões Nordeste e Sudeste. A linha tracejada em 1.0 indica a paridade de gênero.*

<img width="1500" height="900" alt="Evolução do IPG em STEM" src="https://github.com/user-attachments/assets/809a5c84-b067-4163-b9ac-fe4d4ae4892d" />

### Dados Consolidados (Ano de Referência: 2024 )

Apesar das diferenças regionais, ambas as regiões apresentam um IPG significativamente abaixo de 1.0, indicando uma forte disparidade em favor dos homens em STEM.

| ANO | NO_REGIAO | QT_MAT | QT_MAT_FEM | QT_MAT_MASC | PCT_MULHERES | IPG_STEM |
| --- | --- | --- | --- | --- | --- | --- |
| 2024 | Nordeste | 318961 | 87457 | 231504 | 27.42% | 0.38 |
| 2024 | Sudeste | 926305 | 249824 | 676481 | 26.97% | 0.37 |

## 3. A Disparidade por Tipo de Instituição (Pública vs. Privada)

A natureza administrativa da Instituição de Ensino Superior (IES) é um fator crucial na análise da disparidade. O setor público demonstra consistentemente um IPG mais elevado (mais próximo da paridade) do que o setor privado em ambas as regiões.

**Gráfico 2: % de Mulheres em STEM por Tipo de IES (2024)**

*Nota: O gráfico de barras abaixo compara o percentual de mulheres em cursos STEM entre IES Públicas e Privadas nas regiões Nordeste e Sudeste.*

<img width="1500" height="900" alt="Comparação Pública vs Privada" src="https://github.com/user-attachments/assets/0479e4f0-7c0c-4791-a2ca-e838f71fd022" />

### Dados Detalhados (Ano de Referência: 2024 )

| NO_REGIAO | TIPO_IES | QT_MAT | PCT_MULHERES | IPG_STEM |
| --- | --- | --- | --- | --- |
| Nordeste | Privada | 192319 | 22.90% | 0.30 |
| Nordeste | Pública | 126642 | 34.28% | 0.52 |
| Sudeste | Privada | 654142 | 24.58% | 0.33 |
| Sudeste | Pública | 272163 | 32.71% | 0.49 |

**Conclusão:** O setor público no Nordeste apresenta o melhor IPG (0.52), indicando que, para cada 100 homens matriculados, há 52 mulheres. Em contraste, o setor privado no Nordeste apresenta o pior IPG (0.30), com apenas 30 mulheres para cada 100 homens.

## 4. Disparidade por Área de Estudo STEM

A disparidade de gênero não é uniforme dentro das áreas STEM. A área de **Ciências Naturais, Matemática e Estatística** é a que apresenta o IPG mais próximo da paridade, enquanto **Tecnologias da Informação e Comunicação (TIC)** é a área com a maior disparidade.

### Dados Detalhados (Ano de Referência: 2024)

| `NO_REGIAO` | `AREA_CINE` | `QT_MAT` | `PCT_MULHERES` | `IPG_STEM` |
| --- | --- | --- | --- | --- |
| `Sudeste` | `Ciências Naturais, Matemática e Estatística` | `66331` | `47.55%` | `0.91` |
| `Nordeste` | `Ciências Naturais, Matemática e Estatística` | `29934` | `42.91%` | `0.75` |
| `Nordeste` | `Engenharia, Produção e Construção` | `150248` | `33.02%` | `0.49` |
| `Sudeste` | `Engenharia, Produção e Construção` | `447005` | `30.28%` | `0.43` |
| `Sudeste` | `Tecnologias da Informação e Comunicação (TIC)` | `412969` | `20.08%` | `0.25` |
| `Nordeste` | `Tecnologias da Informação e Comunicação (TIC)` | `138779` | `18.01%` | `0.22` |

**Conclusão:**

- **Ciências Naturais, Matemática e Estatística** no Sudeste está muito próxima da paridade (IPG de 0.91).

- **TIC** é a área mais crítica, com um IPG de apenas 0.22 no Nordeste e 0.25 no Sudeste, indicando que há aproximadamente 4 a 5 homens para cada mulher matriculada.

- **Engenharia, Produção e Construção** apresenta uma disparidade intermediária, com o Nordeste novamente à frente do Sudeste em termos de IPG.

## 5. Clusters de Desigualdade (Análise Qualitativa)

Embora a clusterização K-Means não tenha sido executada devido a restrições de ambiente, a análise dos dados brutos sugere a existência de clusters de municípios com perfis distintos de desigualdade, como os identificados no `README` original:

- **Cluster A (Alta Paridade/Inclusão):** Municípios com alto volume de matrículas e IPG mais próximo de 1.0, frequentemente associados a grandes universidades públicas com forte tradição em Ciências Naturais e Matemática.

- **Cluster B (Intermediário):** Municípios com volume e IPG medianos, representando a maioria das cidades universitárias.

- **Cluster C (Baixa Paridade/Disparidade Crítica):** Municípios com baixo volume de matrículas e IPG muito baixo (próximo de 0.0), geralmente dominados por instituições privadas com foco em áreas de alta disparidade como TIC.

**Gráfico 3: Clusterização da Disparidade de Gênero em STEM por Município**

*Nota: O gráfico abaixo, gerado pela análise original, ilustra a distribuição dos municípios em clusters com base no IPG e no volume de matrículas.*

<img width="1000" height="600" alt="Clusterização K-Means" src="https://github.com/user-attachments/assets/d1a96b59-26f3-48d8-bf2d-d66dd95a9ee2" />

A caracterização desses clusters, baseada na análise original, permanece válida:

| Cluster | Característica Principal |
| --- | --- |
| **A** | Grandes Polos de Ensino Privado/Público com Maior IPG (Alta Inclusão ) |
| **B** | Municípios Intermediários (IPG Mediano) |
| **C** | Municípios com Baixa Participação Feminina em STEM (Disparidade Crítica) |

## Conclusão Final

A **Geografia da Desigualdade** em STEM no Brasil é complexa. O Nordeste demonstra uma ligeira vantagem histórica e atual no IPG geral e no setor público, mas ambas as regiões enfrentam uma crise de representatividade feminina, especialmente nas áreas de **Tecnologias da Informação e Comunicação**. A disparidade é significativamente maior no setor privado, sugerindo que políticas públicas de incentivo à participação feminina em IES públicas e em áreas críticas de STEM são essenciais para reverter a tendência de queda observada na última década.





A linha do tempo abaixo revela a trajetória da participação feminina nas duas regiões comparadas, baseada na agregação dos microdados do INEP.

<img width="1500" height="900" alt="comparacao_municipio_vs_microrregiao_2010" src="https://github.com/user-attachments/assets/163fbdfd-0296-4b67-b1a5-4e91cf2d8265" />
<img width="1500" height="900" alt="comparacao_municipio_vs_microrregiao_2011" src="https://github.com/user-attachments/assets/3d4df8f1-0197-4563-b9a0-2ee99ade3bfb" />
<img width="1500" height="900" alt="comparacao_municipio_vs_microrregiao_2012" src="https://github.com/user-attachments/assets/056e59ef-7b48-437c-bb98-d0a0330bb659" />
<img width="1500" height="900" alt="comparacao_municipio_vs_microrregiao_2013" src="https://github.com/user-attachments/assets/68bd6c27-7642-44c8-bcc8-15ae22f5590d" />
<img width="1500" height="900" alt="comparacao_municipio_vs_microrregiao_2014" src="https://github.com/user-attachments/assets/f32171f9-94d3-4208-98d4-973117d53e19" />
<img width="1500" height="900" alt="comparacao_municipio_vs_microrregiao_2015" src="https://github.com/user-attachments/assets/5508d082-e874-464d-8129-34f2e98d4c60" />
<img width="1500" height="900" alt="comparacao_municipio_vs_microrregiao_2016" src="https://github.com/user-attachments/assets/bae1b1ff-ed96-4dac-9413-9fde1151702a" />
<img width="1500" height="900" alt="comparacao_municipio_vs_microrregiao_2017" src="https://github.com/user-attachments/assets/a2b7cd5e-01bd-4c88-b44a-29777ffbc2e7" />
<img width="1500" height="900" alt="comparacao_municipio_vs_microrregiao_2018" src="https://github.com/user-attachments/assets/f60ac36a-1d6a-4616-b208-ca7dc17a9f7b" />
<img width="1500" height="900" alt="comparacao_municipio_vs_microrregiao_2019" src="https://github.com/user-attachments/assets/0fa7d3ad-913c-414f-be23-736be093e69d" />
<img width="1500" height="900" alt="comparacao_municipio_vs_microrregiao_2020" src="https://github.com/user-attachments/assets/38fe4538-bf60-4822-9eb3-40e5cbe65e39" />
<img width="1500" height="900" alt="comparacao_municipio_vs_microrregiao_2021" src="https://github.com/user-attachments/assets/19080ae2-33f7-402f-ae0f-794aa6ca40b1" />
<img width="1500" height="900" alt="comparacao_municipio_vs_microrregiao_2022" src="https://github.com/user-attachments/assets/e6ba8002-44b4-4eda-9380-cc1131d52cde" />
<img width="1500" height="900" alt="comparacao_municipio_vs_microrregiao_2023" src="https://github.com/user-attachments/assets/79022c55-c882-47f3-afba-e72a5884ee2a" />
<img width="1500" height="900" alt="comparacao_municipio_vs_microrregiao_2024" src="https://github.com/user-attachments/assets/eac81d6d-f7b2-4f28-8e6f-47a8a4bd23c1" />

## Microregião Sudeste Publica e Privada 2024

- **A "Exceção à Regra"**: Se você olhar para a barra no topo, Itaguaí é o destaque. É a única microrregião nessa lista onde as mulheres são a maioria (a barra passa um pouco dos 50%). Isso é algo raro em cursos de exatas, que historicamente têm mais homens.
- **A Realidade Geral**: Descendo a lista, vemos cidades universitárias famosas como Viçosa e São Carlos. Nelas, a participação feminina é forte, mas ainda não chega à metade (fica entre 35% e 45%).
- **O Resumo**: Esse gráfico nos mostra que, no setor público dessa região, a paridade de gênero (50/50) ainda é uma meta a ser alcançada na maioria dos lugares.

<img width="1500" height="900" alt="microrregiao_Sudeste_Privada_2024" src="https://github.com/user-attachments/assets/59a5786c-de07-4c57-b96c-379617e6d587" />

- **Números Surpreendentes**: A primeira coisa que chama a atenção é o tamanho das barras. Em Belém, por exemplo, o gráfico indica que mais de 70% dos estudantes em STEM são mulheres. Isso é um número altíssimo e muito diferente do padrão que costumamos ver.

- **Várias cidades acima de 50%**: Diferente do gráfico público, aqui temos várias regiões (como Goiânia e Guanhães) onde as mulheres são a clara maioria.

<img width="1500" height="900" alt="microrregiao_Sudeste_Pública_2024" src="https://github.com/user-attachments/assets/4ccccc7d-d157-4fef-9e91-9947d53fab05" />



## Microregião Nordeste Publica e Privada 2024

<img width="1500" height="900" alt="microrregiao_Nordeste_Privada_2024" src="https://github.com/user-attachments/assets/dca54c76-65be-4f3f-a9d1-e96f3779c200" />

<img width="1500" height="900" alt="microrregiao_Nordeste_Pública_2024" src="https://github.com/user-attachments/assets/2816ebf8-85b3-4072-8787-747fa9c3ae74" />


<img width="1500" height="900" alt="pct_mulheres_stem_tipo_IES_2024" src="https://github.com/user-attachments/assets/0479e4f0-7c0c-4791-a2ca-e838f71fd022" />

- **Nordeste à Frente**: Historicamente (de 2010 a 2024), o Nordeste (linha laranja) manteve uma proporção de mulheres em STEM consistentemente maior que o Sudeste (linha azul). Isso quebra o estereótipo de que regiões mais ricas (Sudeste) teriam indicadores de diversidade melhores.

- **A Queda Geral**: Note que ambas as linhas estão caindo desde 2016/2017. A participação feminina parece estar regredindo nos últimos anos.
  
<img width="1500" height="900" alt="evolucao_pct_mulheres_stem_NE_SE" src="https://github.com/user-attachments/assets/809a5c84-b067-4163-b9ac-fe4d4ae4892d" />

- **Cluster A (Vermelho)**: Grandes Polos de Ensino Privado (Alto volume).

- **Cluster B (Azul)**: Municípios Intermediários (Melhor % de mulheres que o C).

- **Cluster C (Roxo)**: Municípios com Baixa Participação Feminina em STEM (A maioria crítica).

<img width="1000" height="600" alt="Figure_1" src="https://github.com/user-attachments/assets/d1a96b59-26f3-48d8-bf2d-d66dd95a9ee2" />

Tabela de Dados (Evolução):
     ANO NO_REGIAO    QT_MAT  QT_MAT_FEM  PCT_MULHERES
0   2010  Nordeste  147232.0     43256.0     29.379483
1   2010   Sudeste  582439.0    155855.0     26.759025
2   2011  Nordeste  171998.0     51466.0     29.922441
3   2011   Sudeste  666840.0    183548.0     27.525043
4   2012  Nordeste  200121.0     61860.0     30.911299
5   2012   Sudeste  731630.0    208762.0     28.533822
6   2013  Nordeste  230045.0     72318.0     31.436458
7   2013   Sudeste  802633.0    235560.0     29.348407
8   2014  Nordeste  260457.0     83071.0     31.894324
9   2014   Sudeste  883253.0    263837.0     29.871056
10  2015  Nordeste  283502.0     90707.0     31.995189
11  2015   Sudeste  904216.0    275287.0     30.444827
12  2016  Nordeste  289322.0     92314.0     31.907010
13  2016   Sudeste  879720.0    269940.0     30.684763
14  2017  Nordeste  289320.0     92022.0     31.806304
15  2017   Sudeste  863151.0    262601.0     30.423530
16  2018  Nordeste  288106.0     89359.0     31.016015
17  2018   Sudeste  835003.0    249726.0     29.907198
18  2019  Nordeste  276050.0     84369.0     30.562941
19  2019   Sudeste  787123.0    231685.0     29.434409
20  2020  Nordeste  259369.0     77352.0     29.823148
21  2020   Sudeste  776019.0    223937.0     28.857154
22  2021  Nordeste  264517.0     77835.0     29.425330
23  2021   Sudeste  772810.0    218130.0     28.225566
24  2022  Nordeste  287260.0     82333.0     28.661491
25  2022   Sudeste  820504.0    226978.0     27.663241
26  2023  Nordeste  299659.0     83830.0     27.975132
27  2023   Sudeste  889237.0    241873.0     27.200060
28  2024  Nordeste  318961.0     87457.0     27.419340
29  2024   Sudeste  926305.0    249824.0     26.969951

Municípios com menor participação feminina em STEM (ano de referência):
      NO_REGIAO SG_UF          NO_MUNICIPIO  PCT_FEM_STEM  VOLUME_STEM  PCT_PUBLICA LABEL
13776  Nordeste    AL                Anadia           0.0          1.0          0.0     C
13848  Nordeste    BA               Brejões           0.0          1.0          0.0     C
14418  Nordeste    PE             Dormentes           0.0         10.0          0.0     C
14897   Sudeste    MG                 Ijaci           0.0          1.0          0.0     C
15689   Sudeste    SP  Vista Alegre do Alto           0.0          1.0          0.0     C
13780  Nordeste    AL               Batalha           0.0          3.0          0.0     C
13783  Nordeste    AL          Campo Alegre           0.0         12.0          0.0     C
13784  Nordeste    AL    Colônia Leopoldina           0.0          2.0          0.0     C
13788  Nordeste    AL          Feira Grande           0.0          1.0          0.0     C
13830  Nordeste    BA      Amélia Rodrigues           0.0          3.0          0.0     C
