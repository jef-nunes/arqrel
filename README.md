## 🐉 Sobre

O que esse programa faz:

I. Inicia uma busca por arquivos no caminho especificado pelo usuário

II. Para cada arquivo encontrado, cria um dicionário Python contendo os metadados do arquivo. Adiciona também um atributo de hash SHA256, e classifica o arquivo dentro de umas das categorias:

    Arquivos de configuração
    Shell script Linux
    Arquivos fonte de linguagens
    Bytecode de linguagens
    Executável Windows
    Arquivo de lotes Windows
    Script PowerShell Windows
    Arquivos do pacote Office Windows
    Arquivos de mídia
    Outros binários

III. Ao fim da busca, são criados dois relatórios:

    summary.json: resumo sobre os resultados.
    attributes.json: detalhes sobre cada arquivo encontrado.

## Executando

Para executar o programa chame o interpretador python, nome do programa e especifique uma flag --path a qual deve ser sucedida pelo caminho (sem aspas) do diretório o qual você deseja realizar uma busca:

Exemplo:

    python3 arqrel.py --path home

Para printar no terminal cada arquivo encontrado pelo programa, passe a flag -v (ou --verbose):

    python3 arqrel.py -v --path home 
