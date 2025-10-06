# Avaliacao_indices_bolsa
Trabalho 1 - CMP 609 : Introdução aos Métodos Computacionais em Finanças (2025-II)

indices = {
    "rows": [
        {
            "name": "amplos",
            "symbols": ["IBOV", "IBXX", "IBXL", "IBRA"]
        },
        {
            "name": "capitalizacao",
            "symbols": ["MLCX", "SMLL", "IVBX"]
        },
        {
            "name": "governanca_dividendos",
            "symbols": ["IGCX", "ITAG", "IGNM", "IGCT", "IDIV"]
        },
        {
            "name": "tematicos_esg",
            "symbols": ["ICO2", "ISEE"]
        },
        {
            "name": "setoriais",
            "symbols": ["ICON", "IEEX", "IFNC", "IMOB", "INDX", "IMAT", "UTIL"]
        },
        {
            "name": "alternativos",
            "symbols": ["IFIX", "BDRX"]
        }
    ]
}


1) Introdução
- Motivação: por que índices e por que B3? Papel do CDI como benchmark em BRL.
- Questões de pesquisa:
  - Como os índices se comparam em risco-retorno (em excesso ao CDI)?
  - Em que medida a carteira (índice) melhora o perfil em relação às suas componentes (diversificação)?
  - Existem sazonalidades robustas nos índices/sets? Qual a relevância prática?
  - Quanto do retorno/risco dos índices é explicado por poucos dias extremos?
- Contribuições: transparência metodológica (total return, CDI na mesma base), análises de robustez, e visualizações focadas em efeito de diversificação e caudas.

2) Dados e Preparação
- Universo: famílias de índices da B3 listadas (amplos, capitalização, governança/dividendos, temáticos ESG, setoriais, alternativos).
- Frequência e período: diário (preferencial), com cortes por subperíodos (ex.: 2014–2019; 2020–2022; 2022–2024; 2025 YTD).
- Ajustes:
  - Retornos totais (incluindo proventos) das componentes e índices.
  - Pesos: usar composições históricas por rebalance (trimestral/semestre). Se não disponível, documentar suposições.
  - CDI: converter para a mesma frequência dos retornos; trabalhar sempre em excesso ao CDI quando aplicável.
  - Qualidade: tratamento de faltantes, não-sincronia (avaliar semanal/mensal para robustez), checagem de tracking error do índice reconstruído vs oficial.

3) Análise de Retorno e Risco entre Índices
3.1) Estatística descritiva em excesso ao CDI
- Métricas: retorno médio (aritmético), retorno composto (CAGR), volatilidade anualizada, skewness, kurtosis.
- Correções: diferença entre média aritmética vs geométrica (volatility drag).
- Gráficos:
  - Retorno acumulado: índice vs índice–CDI vs CDI.
  - Barras de retorno anualizado (geométrico) e volatilidade com ICs.
  - QQ-plot por índice para caudas.

3.2) Desempenho ajustado a risco
- Métricas: Sharpe e Sortino (com ajuste de autocorrelação para IFIX/Small caps), Calmar.
- Subperíodos: repetir para blocos de regime; apresentar estabilidade temporal.
- Gráficos:
  - Sharpe/Sortino com IC95% por subperíodo.
  - “Underwater” (drawdown) e tempo de recuperação.

3.3) Sensibilidade ao mercado e fatores simples
- Betas e alfas: regressão dos índices (excesso ao CDI) contra um mercado amplo (IBRA ou IBOV).
- Opcional: incluir proxies de fatores (tamanho: SMLL–MLCX; dividendos: IDIV; defensivo: UTIL/IFNC).
- Gráficos:
  - Beta e correlação rolantes (12 meses).
  - Decomposição do retorno em alpha + beta×mercado por subperíodo.

3.4) Concentração e diversificação
- Métricas: HHI de pesos, top-10 pesos, razão de diversificação = Σ w_i σ_i / σ_port.
- Gráficos:
  - Evolução do HHI e da razão de diversificação.
  - Paridade “peso vs contribuição ao risco” (Pareto).

4) Componentes dos Índices, Diversificação e Sazonalidade
4.1) Efeito de diversificação: componentes vs índice
- Comparação: dispersão risco-retorno das ações componentes (pontos) vs o índice (marcador) para cada índice.
- Métricas:
  - Volatilidade do índice vs média ponderada das volatilidades (ganho de diversificação).
  - Contribuição marginal de risco (MCR) e top-5 contribuições ao risco.
- Gráficos:
  - Scatter risco-retorno (com elipse de confiança) de componentes e posição do índice.
  - Barras das top-5 contribuições de risco vs top-5 pesos.

4.2) Equal-weight vs cap-weight (robustez de construção)
- Construir versão equal-weight para as mesmas componentes e rebalancear em frequência definida.
- Avaliar: retorno, volatilidade, Sharpe, turnover.
- Gráficos:
  - Comparativo cap-weight vs equal-weight (retorno acumulado e tabela de métricas).
  - Diferença de desempenho ao longo do tempo (cap–eq).

4.3) Sazonalidade nos índices e nas componentes
- Dimensões de sazonalidade:
  - Calendário: mês do ano, dia da semana, viradas de mês (turn-of-the-month), efeitos de feriados.
  - Microestrutural: último/primeiro dia de rebalanceamento de índice (se datas conhecidas).
- Metodologia:
  - Retornos médios condicionais e testes simples (t-test/bootstraps); controlar múltiplas comparações.
  - Robustez: usar versões winsorizadas ou excluir outliers para não “contaminar”.
- Gráficos:
  - Heatmap de retorno médio por mês x índice.
  - Boxplots por dia da semana e por índice; marcar significância.

4.4) Dispersão cross-sectional como termômetro
- Métrica: desvio-padrão entre retornos das componentes por data; correlação com a vol do índice.
- Gráficos:
  - Série temporal da dispersão vs vol do índice e correlação rolante.
  - Histogramas comparando períodos de alta vs baixa dispersão.

5) Como os Índices São Afetados por Dias com Maior/Menor Retorno
5.1) Contribuição de dias extremos para o retorno total
- Excluir top-N melhores e piores dias e recomputar CAGR e Sharpe (N = 5, 10, 20 por ano e na amostra).
- Insight: sensibilidade do retorno de longo prazo a poucos dias.
- Gráficos:
  - Barras do CAGR com/sem top-N melhores e piores dias.
  - Curvas de retorno acumulado excluindo extremos (sobrepostas).

5.2) Regime de volatilidade e cliques de correlação
- Analítica: em janelas de estresse, correlações sobem, a diversificação cai; relacione com performance dos índices.
- Gráficos:
  - Razão de diversificação e correlação média implícita ao longo do tempo (usar identidade de variância).
  - Marcadores de eventos (COVID, choques de commodities/juros).

5.3) Efeito de “under/over‑reaction” pós-extremos
- Estudo evento simples:
  - Condicionar retornos D+1, D+5, D+20 após um dia no top 1% melhor/pior de cada índice.
- Gráficos:
  - Linhas com média acumulada pós-evento e ICs.

6) Robustez Temporal e Benchmarks
6.1) Subperíodos e estabilidade
- Repetir as principais métricas em blocos (2014–2019; 2020–2022; 2022–2024; 2025 YTD).
- Testes de mudança estrutural simples (Chow/Bai-Perron, opcional).

6.2) Frequências alternativas e não-sincronia
- Recalcular análises chave em semanal/mensal (especial atenção a SMLL/IFIX).
- Comparar correlações e Sharpes.

6.3) CDI como referência
- Trabalhar sempre em excesso ao CDI para Sharpe/beta/alpha; mostrar também nominal para intuição.
- Gráficos: retornos acumulados índice–CDI e dispersão risco-retorno em excesso ao CDI.

7) Resultados e Discussão
- Síntese dos trade-offs por família:
  - Amplos (IBOV/IBRA/IBXL/IBXX): risco de mercado e concentração.
  - Capitalização (MLCX/SMLL/IVBX): tamanho e caudas.
  - Governança/Dividendos (IGCX/ITAG/IGNM/IGCT/IDIV): drawdowns e estabilidade.
  - Setoriais (ICON/IEEX/IFNC/IMOB/INDX/IMAT/UTIL): sensibilidade a ciclos e juros/commodities.
  - Alternativos (IFIX/BDRX): renda recorrente e componente cambial.
- Onde a diversificação do índice supera suas componentes; quando falha (crises).
- Relevância de sazonalidades e de dias extremos para decisões práticas.
- Limitações: dados de composição, proventos, custos/tributação, viés de sobrevivência.

8) Conclusões
- 3–5 afirmações objetivas com respaldo nos resultados.
- Pistas para trabalhos futuros: extensão multifatorial, otimizações com restrições, análise intradiária.

Apêndices
A) Fórmulas e detalhes de anualização e métricas
- Retornos simples/log; anualização geométrica; vol anual; Sharpe ajustado por autocorrelação; beta/alpha; VaR/ES; razão de diversificação; correlação média implícita.

B) Checagens e armadilhas (mini-guia)
- CDI na mesma base; total return vs price; pesos de início do período; tracking error; root‑time pitfall em VaR; efeito dos outliers; winsorização vs trimming.

C) Reprodutibilidade
- Organização de código: ingestão, limpeza, construção de índices, métricas, gráficos, tabelas.
- Sementes e versões de pacotes; arquivos de configuração (paths, datas de rebalance, tickers).

Lista compacta de figuras (prioridade)
- F1: Retornos acumulados (índice vs índice–CDI vs CDI), por família.
- F2: Dispersão risco-retorno: componentes vs índice (diversificação).
- F3: Barras CAGR vs média aritmética (volatility drag).
- F4: Sharpe/Sortino (IC95%) e vol rolante (12m).
- F5: Underwater e tempo de recuperação.
- F6: HHI de pesos e top-5 contribuições ao risco.
- F7: Heatmap de sazonalidade (mês x índice).
- F8: Boxplots por dia da semana (por índice).
- F9: Impacto de excluir top-N melhores/piores dias (CAGR).
- F10: Cap-weight vs equal-weight (comparativo).

Checklist operacional (resumo)
- Consolidar composições históricas e proventos; construir retornos totais das componentes.
- Reconstituir cada índice cap-weight por janela de rebalance; validar contra série oficial.
- Calcular retornos em excesso ao CDI com CDI na mesma base.
- Gerar métricas e figuras principais nas janelas totais e por subperíodos.
- Rodar sazonalidades com correção de múltiplas comparações e robustez (winsorizar).
- Executar análises de dias extremos (excluir top-N; estudo de evento pós-extremo).
- Documentar limitações e sensibilidade (semanal/mensal; equal-weight).