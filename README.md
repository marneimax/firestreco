# FireTV Web Remote

## Descrição do Projeto
O **FireTV Web Remote** é uma aplicação web moderna desenvolvida para controlar dispositivos Amazon FireTV (e Android TV compatíveis) através de qualquer navegador. Utilizando Python (FastAPI) no backend e uma interface leve em HTML/JS, o projeto oferece uma alternativa poderosa ao controle físico, ideal para quem está no computador ou deseja funcionalidades avançadas de entrada de dados.

O sistema se comunica com o dispositivo via ADB (Android Debug Bridge), permitindo não apenas o envio de comandos básicos de navegação, mas também o lançamento direto de aplicativos e visualização remota da tela.

## Diferenciais
*   **Interface Web Universal e Responsiva**: Acessível de qualquer PC, smartphone ou tablet conectado à mesma rede, sem necessidade de instalar aplicativos clientes.
*   **Live Preview (Espelhamento)**: Funcionalidade distinta que permite visualizar a tela do FireTV em tempo real diretamente no navegador (via MJPEG), possibilitando o controle remoto mesmo sem visada direta para a TV.
*   **Entrada de Texto Ágil**: Digite buscas, senhas e URLs usando o teclado físico ou virtual do seu dispositivo, eliminando a dificuldade de digitação com o controle remoto padrão.
*   **Gerenciador de Apps Personalizável**: Sistema flexível para criar, editar, importar e exportar atalhos para seus aplicativos favoritos, suportando comandos complexos de inicialização (Intents).
*   **Controles Completos**: Mapeamento total das teclas de navegação, mídia (play/pause/volume) e funções do sistema (Home, Menu, Voltar).

## Objetivos Futuros
*   **Otimização de Streaming**: Implementar métodos de captura de tela mais eficientes (como WebRTC ou H.264) para aumentar a taxa de quadros e reduzir a latência do Live Preview.
*   **Autenticação e Segurança**: Adicionar camada de login/senha para restringir o acesso ao controle na rede local.
*   **Suporte Multi-Dispositivos**: Interface para gerenciar e alternar instantaneamente entre múltiplos FireTVs na mesma rede.
*   **Descoberta de Dispositivos**: Implementar descoberta de dispositivos na rede local para seleção via interface.
*   **Modo Mouse/Touchpad**: Implementar emulação de mouse para controlar aplicativos que não são otimizados para navegação por controle remoto.
*   **Macros de Automação**: Criar scripts de sequência de botões para automatizar tarefas rotineiras (ex: "Abrir Youtube e buscar canal X").
*   **Listar Pacotes Instalados**: Implementar método para listar pacotes instalados no dispositivo e facilite a importação de atalhos.