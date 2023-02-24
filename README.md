# iGrowth - mvp1

O objetivo do projeto iGrowth é desenvolver e insights e reports para restaurantes que vendem na plataforma Ifood.

No MVP1 as automações foram desenvolvidas Python, processos de ELT  foram desenvolvidos em python, Data Visualization foram desenvolvidos em Power BI, bancos de dados foram desenvolvidos em colaboração com o Google Drive. 

Diversas validações de mercado foram executadas antes de iniciarmos as automações de processos, além disso, operamos por 14 dias em mapeamento dos processos na metodologia BPMN com foco na identificação de fragilidades das automações.
  - Estratégias de validação: Pesquisa de mercado, Testes A/B, User interview e Feedback contínuo.

## etapas do processo
Etapa 1: Automação 1
  - Objetivos: Automação de login em diversas contas e captura de bases financeiras individuais "LISTA_DE_PEDIDOS" e alimentar a base de dados "finalidade".
  - Processo: O processo envolve a captura de dados de um banco na núvem para a captura de logins, senhas e acessos, realiza inputs e manipulações na plataforma para a obtenção da base de dados "LISTA_DE_PEDIDOS" do dia anterior.
  - Dificuldades: O processo de login envolve obrigatoriamente uma validação de token do tipo CAPCHA, "Completely Automated Public Turing test to tell Computers and Humans Apart" e diversos POP-UP que dificultam as movimentações na plataforma.

Etapa 2: ELT 1
  - Objetivos: Tratar os dados alimentados na base "finalidade", criando correlações para a obtenção de valores em taxa de investimento e faturamentos liquido, real e bruto.
  - Dificuldades: 

Etapa 3: Visualização em Power BI 1
  - Objetivos: Visualizar de forma clara a performance financeira do restaurante para a obtenção de insights.
  - Dificuldades: Os usuários não eram habituados a utilizar ferramentas de visualização de dados, então tivemos que simplificar diversas informações para tornar possível a comunicação ideal dos dados, as estratégias foram validadas com testes A/B e user interview.
  
