# Disco Elysium: Save Editor
 
[🇺🇸 Read in English](README.md)
 
> **Usuários de Windows:** O executável compilado está disponível na [página de Releases](https://github.com/Lilja-J/saveEditorDiscoElysium/releases/latest) ([Download Direto](https://github.com/Lilja-J/saveEditorDiscoElysium/releases/latest/download/DiscoElysiumSaveEditor.exe)), sem necessidade de instalar Python.
 
Uma ferramenta local com interface gráfica (GUI) simples para editar os arquivos de save do jogo Disco Elysium. 
 
Construído em Python, o script acessa diretamente os arquivos `.json` de dentro dos arquivos comprimidos (`.zip`) gerados pelas versões mais recentes do jogo, modificando os dados e reempacotando o save de forma atômica, sem sujar o sistema de arquivos com extrações temporárias.
 
## Funcionalidades
* **Seleção Visual de Pasta e Arquivo:** Escolha a pasta `SaveGames` ou abra qualquer arquivo `.zip` diretamente pela interface, sem precisar mexer no código.
* **Detecção Automática:** Localiza automaticamente os diretórios de saves mais comuns (Steam/Proton, Bottles, Heroic/GOG).
* **Configuração Persistente:** Salva sua pasta preferida para carregar direto nas próximas vezes.
* **Edição de Recursos:** Altera Skill Points e Dinheiro (Reál).
* **Edição de Atributos:** Permite modificar os 4 atributos base (Intellect, Psyche, Fysique, Motorics).
* **Edição de Sub-Habilidades:** Controle total sobre as 24 habilidades do jogo.
* **Modo Deus (Max Tudo):** Preenche todos os atributos e perícias em 20, Dinheiro em 999.00 Reál e 999 Skill Points de forma segura.
* **Manipulação in-memory:** Lê e atualiza o `2nd.ntwtf.json` direto no ZIP sem extrair nada em disco.
 
## Estrutura do Projeto
```text
saveEditorDiscoElysium/
├── main.py          # Código principal da aplicação
├── readme.md        # Documentação em Inglês
└── README.pt.md     # Documentação em Português
```
 
## Pré-requisitos
O projeto não possui dependências externas que exijam `pip install`. Ele utiliza apenas bibliotecas nativas do Python 3:
* `os`, `glob`, `json`, `zipfile`, `tempfile`, `shutil`, `re`
* `tkinter` (Para a interface gráfica)
 
> **Nota para usuários de Linux:** Dependendo da sua distribuição, a biblioteca `tkinter` pode não vir instalada por padrão com o Python. Se necessário, instale via terminal com: `sudo apt-get install python3-tk`
 
## Como Usar
 
**1. Clonar e Executar:**
```bash
git clone https://github.com/Lilja-J/saveEditorDiscoElysium.git
cd saveEditorDiscoElysium
python3 main.py
```
 
**2. Carregando o Save:**
* O editor tentará carregar o último quicksave automaticamente.
* Caso necessário, clique em **"Select Folder"** para escolher sua pasta de saves ou em **"Open Save (.zip)"** para abrir qualquer save específico.
 
**3. Editando e Salvando:**
* Altere os campos ou clique em **"GOD MODE (MAX ALL)"**.
* Clique em **"Save Changes to ZIP"** e carregue o jogo.
 
---
 
## Gerando um Executável Standalone (Opcional)
 
Caso queira compilar o script em um executável independente:
 
### Windows:
```cmd
pip install pyinstaller
pyinstaller --onefile --noconsole --name "DiscoElysiumSaveEditor" main.py
```
*(O executável será gerado em `dist\DiscoElysiumSaveEditor.exe`)*
 
### Linux:
```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --name "DiscoElysiumSaveEditor" main.py
chmod +x dist/DiscoElysiumSaveEditor
```
*(O binário será gerado em `dist/DiscoElysiumSaveEditor`)*