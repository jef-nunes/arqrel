## Sobre
O que esse programa faz:
I. Inicia uma busca por arquivos no caminho especificado pelo usuário
II. Para cada arquivo encontrado, cria um dicionário python
contendo os metadados do arquivo. adiciona tambem um atributo
de hash sha256, e classifica o arquivo dentro de umas das categorias:
  - arquivos de configuração
  - shell script linux
  - arquivos fonte de linguagens
  - bytecode de linguagens
  - executável windows
  - arquivo de lotes windows
  - script powershell windows
  - arquivos do pacote office windows
  - arquivos de mídia
  - outros binários
III. Ao fim da busca são criados dois relatórios:
  1. summary.json: resumo sobre os resultados.
  2. attributes.json: detalhes sobre cada arquivo encontrado.
     
