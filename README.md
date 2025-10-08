# Avaliação de Índices da Bolsa Brasileira (B3): Análise Multidimensional de Risco-Retorno com Foco em Carry Trade e Eventos Extremos

**Trabalho 1 - CMP 609: Introdução aos Métodos Computacionais em Finanças (2025-II)**

---

## 1. Introdução e Motivação

### 1.1 Contexto e Relevância
A B3 (Brasil, Bolsa, Balcão) oferece uma ampla gama de índices que capturam diferentes segmentos e estratégias do mercado acionário brasileiro. Esta diversidade permite aos investidores e gestores de recursos construir portfólios especializados, mas também levanta questões fundamentais sobre:

- **Eficiência relativa**: Como diferentes índices se comparam em termos de risco-retorno?
- **Papel do carrego**: Qual o impacto da estrutura de juros brasileira (CDI/Selic) na performance relativa dos índices?
- **Robustez temporal**: Como a performance se mantém ao longo de diferentes regimes econômicos?
- **Contribuição de eventos extremos**: Quanto da variabilidade de retornos é explicada por poucos dias de mercado?

### 1.2 O CDI como Benchmark Fundamental
No contexto brasileiro, o CDI (Certificado de Depósito Interbancário) representa o custo de oportunidade livre de risco em moeda local. Diferentemente de mercados desenvolvidos onde treasury bills servem como referência, o Brasil apresenta:

- **Juros reais historicamente elevados**: Criando um "carrego" significativo para investimentos de renda variável
- **Volatilidade da taxa Selic**: Impactando diretamente o custo de oportunidade
- **Indexação da dívida pública**: Gerando correlações complexas entre renda fixa e variável

### 1.3 Questões de Pesquisa Centrais

1. **Análise Risco-Retorno**: Como os índices se posicionam no espaço risco-retorno considerando diferentes horizontes temporais e ajustados pelo CDI?

2. **Impacto de Dias Extremos**: Qual a contribuição de dias de alta volatilidade (bull/bear) para o retorno total e risco dos índices?

3. **Efeito Carrego vs. Volatilidade**: Como a relação risco-retorno se altera quando consideramos o diferencial entre o retorno dos índices e o CDI?

4. **Concentração e Diversificação**: Como a concentração dos índices afeta sua performance durante diferentes regimes de mercado?

5. **Sazonalidades e Padrões Temporais**: Existem padrões robustos que podem ser explorados ou que devem ser considerados na análise de risco?

---

## 2. Universo de Análise: Taxonomia dos Índices B3

### 2.1 Categorização dos Índices

#### **Índices Amplos (Proxy do Mercado)**
- **IBOV**: Bovespa (tradicional, por liquidez)
- **IBXX**: Brasil 100 (100 maiores por capitalização)
- **IBXL**: Brasil 50 (Large Caps)
- **IBRA**: Brasil Amplo (representa ~95% da capitalização)

#### **Índices por Capitalização**
- **MLCX**: Mid-Large Cap
- **SMLL**: Small Cap
- **IVBX**: Valor (Value investing)

#### **Índices de Governança e Dividendos**
- **IGCX**: Governança Corporativa Trade Index
- **ITAG**: Ações com Tag Along
- **IGNM**: Novo Mercado
- **IGCT**: Governança Corporativa
- **IDIV**: Dividendos

#### **Índices Temáticos e ESG**
- **ICO2**: Carbono Eficiente
- **ISEE**: Sustentabilidade Empresarial

#### **Índices Setoriais**
- **ICON**: Consumo
- **IEEX**: Energia Elétrica
- **IFNC**: Financeiro
- **IMOB**: Imobiliário
- **INDX**: Industrial
- **IMAT**: Materiais Básicos
- **UTIL**: Utilidade Pública

#### **Índices Alternativos**
- **IFIX**: Fundos Imobiliários
- **BDRX**: Brazilian Depositary Receipts

---

## 3. Metodologia de Análise

### 3.1 Preparação dos Dados
- **Série temporal**: Dados diários (preferencial) com cortes por subperíodos
- **Períodos de análise**: 
  - 2014-2019 (Pré-pandemia)
  - 2020-2022 (Pandemia e políticas expansionistas)
  - 2022-2024 (Normalização monetária)
  - 2025 YTD (Período corrente)
- **Base de cálculo**: Total return (incluindo dividendos reinvestidos)
- **Benchmark**: CDI acumulado na mesma periodicidade

### 3.2 Métricas Fundamentais

#### **Performance Ajustada ao Risco**
- **CAGR (Compound Annual Growth Rate)**
- **Volatilidade anualizada** (desvio-padrão dos retornos)
- **Sharpe Ratio** = (Retorno - CDI) / Volatilidade
- **Sortino Ratio** (penaliza apenas downside)
- **Information Ratio** vs IBOV
- **Maximum Drawdown** e duração da recuperação

#### **Métricas de Concentração e Diversificação**
- **Índice Herfindahl-Hirschman (HHI)** dos pesos: HHI = Σ(wᵢ)²
- **Effective Number of Stocks**: 1/HHI
- **Top-10 concentration**: Soma dos 10 maiores pesos
- **Diversification Ratio**: Σ(wᵢ × σᵢ) / σₚₒᵣₜfóₗᵢₒ

### 3.3 Análise de Dias Extremos (Metodologia Central)

#### **Identificação de Dias Extremos**
- **Percentis de retorno**: P5, P95 (5% e 95%)
- **Volatilidade condicional**: Dias com retorno |R| > 2σ
- **Regimes de mercado**: Bull (retornos > P75), Bear (retornos < P25)

#### **Análise de Sensibilidade**
Para cada índice, calcular métricas removendo:
- **Top-N melhores dias** (N = 5, 10, 20 por ano)
- **Top-N piores dias** (N = 5, 10, 20 por ano)
- **Combinação**: Removendo ambos simultaneamente

**Métricas recalculadas**:
- CAGR ajustado
- Sharpe Ratio ajustado
- Volatilidade residual
- **Contribuição marginal** dos dias extremos

#### **Análise do Efeito Carrego**
- **Excess Return** = Retorno do Índice - CDI
- **Carry-Adjusted Sharpe** = Excess Return / Volatilidade
- **Tracking Error** vs CDI
- **Correlação rolante** com a curva de juros (DI360)

---

## 4. Estrutura Analítica Proposta

### 4.1 Análise Descritiva e Exploratória

#### **Visualização Risco-Retorno**
- **Scatter plot** principal: Volatilidade (x) × Retorno Anualizado (y)
  - Cada ponto representa um índice
  - Tamanho do ponto proporcional à capitalização média
  - Cores por categoria (Amplos, Setoriais, etc.)
  - Linha de eficiência do CDI como referência

#### **Decomposição por Componentes**
Para cada categoria de índices:
- **Scatter das ações componentes** vs posição do índice
- **Elipse de confiança** (95%) das componentes
- **Contribuição marginal ao risco** vs peso no índice

### 4.2 Análise Temporal e de Regimes

#### **Evolução da Concentração**
- **Série temporal do HHI** para cada índice
- **Evolução do Diversification Ratio**
- **Correlação com volatilidade do mercado** (IBOV)

#### **Análise de Regimes de Volatilidade**
- **Estados de alta/baixa volatilidade** usando Markov Switching
- **Correlação condicional** entre índices por regime
- **Performance relativa** em cada regime

#### **Dispersão Cross-Sectional como Termômetro**
- **Métrica**: σ_cs,t = std(R_i,t) para i ∈ componentes do índice
- **Correlação** entre dispersão e volatilidade do índice
- **Poder preditivo** da dispersão para retornos futuros

### 4.3 Análise de Robustez e Estabilidade

#### **Estabilidade Temporal**
- **Testes de mudança estrutural** (Chow, Bai-Perron)
- **Análise de subperíodos** com métricas comparáveis
- **Correlação rolante** entre índices

#### **Stress Testing**
- **Cenários simulados** de choques:
  - Queda de 20% em 1 dia seguida de recuperação gradual
  - Período prolongado de alta volatilidade (30 dias)
  - Mudança abrupta na estrutura de juros
- **Análise de sensibilidade** das métricas principais

---

## 5. Contribuições Metodológicas Esperadas

### 5.1 Transparência e Replicabilidade
- **Metodologia total return** consistente para todos os índices
- **Base comum de comparação** (CDI ajustado)
- **Código aberto** para replicação dos resultados

### 5.2 Foco no Contexto Brasileiro
- **Análise específica do efeito carrego** em economia de juros altos
- **Impacto da estrutura tributária** (IR sobre ganhos de capital)
- **Consideração da liquidez diferenciada** dos mercados brasileiros

### 5.3 Metodologia de Dias Extremos
- **Quantificação precisa** da contribuição de outliers
- **Framework para análise** de robustez de estratégias
- **Insights para gestão de risco** em mercados emergentes

---

## 6. Resultados Esperados e Aplicações

### 6.1 Para Investidores Institucionais
- **Mapeamento de oportunidades** de diversificação
- **Identificação de prêmios de risco** específicos por segmento
- **Framework para asset allocation** tática e estratégica

### 6.2 Para Gestores de Recursos
- **Benchmarks alternativos** ao IBOV tradicional
- **Insights sobre concentração** e seus impactos
- **Estratégias de timing** baseadas em padrões identificados

### 6.3 Para Academia e Regulação
- **Base empírica** para discussões sobre estrutura de mercado
- **Evidências sobre eficiência** dos diferentes segmentos
- **Subsídios para políticas** de desenvolvimento do mercado de capitais

---

## 7. Cronograma e Deliverables

### 7.1 Entregáveis Principais
1. **Relatório técnico** completo (30-40 páginas)
2. **Dashboard interativo** com as principais métricas
3. **Dataset limpo** com séries históricas padronizadas
4. **Código Python/R** documentado para replicação

### 7.2 Estrutura do Relatório Final
1. **Executive Summary** (2 páginas)
2. **Análise descritiva** dos índices (8-10 páginas)
3. **Análise de dias extremos** e efeito carrego (10-12 páginas)
4. **Análise de concentração** e diversificação (6-8 páginas)
5. **Robustez temporal** e regimes (6-8 páginas)
6. **Conclusões e recomendações** (3-4 páginas)
7. **Apêndices técnicos** (metodologias, códigos, dados)

---

## 8. Considerações Técnicas e Limitações

### 8.1 Desafios Metodológicos
- **Survivorship bias** em índices com alteração de composição
- **Look-ahead bias** em análises de estratégias
- **Liquidez heterogênea** entre componentes dos índices

### 8.2 Dados e Fontes
- **B3**: Dados oficiais dos índices e composições
- **Economática/Bloomberg**: Séries históricas de preços
- **BCB**: CDI e estrutura de juros
- **CVM**: Informações corporativas complementares

### 8.3 Limitações do Escopo
- **Foco quantitativo**: Análise fundamentalista limitada
- **Custos de transação**: Não considerados diretamente
- **Impacto tributário**: Simplificado para PF padrão

---

Esta proposta reformulada oferece uma estrutura mais robusta e focada nas questões centrais de análise de índices no contexto brasileiro, com ênfase especial no papel do carrego (CDI) e na contribuição de dias extremos para o risco-retorno dos índices.