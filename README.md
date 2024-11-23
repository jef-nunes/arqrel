## Sobre
*O que este programa faz:*

**I.** Inicia uma analise de arquivos no diretório especificado pelo usuário.

**II.** Para cada arquivo encontrado, cria um dicionário formatado contendo os atributos do arquivo. Também adiciona um atributo de hash SHA256 e um atributo de classificação, baseado na extensão do arquivo.

**III.** Ao final da busca, são gerados dois relatórios:<br>
+ estatisticas.json: um resumo dos resultados.<br>
+ atributos.json: detalhes dos atributos de cada arquivo encontrado.<br>

## Executando
Ao executar o programa o argumento "--path" deve ser passado, contendo o caminho do diretório no qual o programa irá analisar os arquivos.<br>

Exemplo:

```sh
python3 arqrel.py --path [insira o caminho]
