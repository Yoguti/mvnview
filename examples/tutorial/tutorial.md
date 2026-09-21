# Tutorial básico do MVNView

Este guia mostra como preparar o ambiente e executar os notebooks do projeto. O MVNView pode ser usado para extrair inforamções detectadas pelos sensores incerciais e criar plots complexos. 


Siga os passos utilizando o programa **VS Code**.

## 1. Estrutura dos arquivos

Execute os comandos a partir da pasta principal do projeto, aquela que contém
`pyproject.toml`, `capture_data`, `examples` e `mvnview`.

dentro da pasta */examples* estão os notebooks(**.ipynb**) que servem como tutoriais guiados. Eles utilizam arquivos **.mvnx** que devem ser colocados pelo usuário em */capture_data/raw_mvnx/files*

```text
capture_data/
├── raw_mvnx/files/
│   └── seu_arquivo.mvnx
└── converted_npz/files/
    └── seu_nome.npz
```

Coloque cada arquivo MVNX em:

```text
capture_data/raw_mvnx/files/NOME_DO_ARQUIVO.mvnx
```

Os notebooks salvam os arquivos convertidos em:

```text
capture_data/converted_npz/files/NOME_ESCOLHIDO.npz
```

Os caminhos são fixos nos notebooks. Só é preciso editar os nomes dos
arquivos nas células indicadas (logo no início de cada notebook **.ipynb**). 

## 2. Criar o ambiente virtual

No VS Code:

1. Abra a pasta principal do projeto no VS Code.
2. Pressione **Ctrl+Shift+P** para abrir a Paleta de Comandos.
3. Procure por **Python: Create Environment** e selecione essa opção.
4. Escolha **Venv** como o tipo de ambiente.
5. Escolha um interpretador Python instalado no computador.
6. Quando o VS Code perguntar pelas dependências, selecione
   `examples/tutorial/requirements.txt`.

O VS Code criará uma pasta `venv` na pasta principal do projeto, instalará as
dependências e selecionará esse ambiente para o projeto.

As dependências em *requirements.txt* são às bibliotecas necessárias para manipulação de matrizes e criação de plots.

## 4. Selecionar o interpretador no VS Code

1. Abra a pasta principal do projeto no VS Code.
2. Pressione **Ctrl+Shift+P** para abrir a Paleta de Comandos.
3. Procure por **Python: Select Interpreter**.
4. Escolha o interpretador do ambiente virtual:
   - Linux: `venv/bin/python`
   - Windows: `venv\Scripts\python.exe`
5. Abra o notebook e confirme que o kernel selecionado também é o ambiente
   `venv`.

## 5. Converter o MVNX para NPZ

Abra o notebook [introducao.ipynb](../introducao.ipynb) e execute as células
na ordem.

Na célula de localização dos arquivos, altere somente estas duas variáveis:

```python
NOME_ARQUIVO_MVNX = "seu_arquivo.mvnx"
NOME_ARQUIVO_NPZ = "seu_nome.npz"
```

O nome do MVNX precisa corresponder exatamente ao arquivo colocado em
`capture_data/raw_mvnx/files`. O resultado será salvo automaticamente em
`capture_data/converted_npz/files`.

## 6. Criar gráficos

Abra o notebook [plots-simples.ipynb](../plots-simples.ipynb). Na célula de
carregamento, altere somente:

```python
NOME_ARQUIVO_NPZ = "seu_nome.npz"
```

Esse nome deve ser o mesmo usado na conversão. Depois, execute as células na
ordem.

O nome do segmento usado nos gráficos também pode ser alterado, por exemplo:

```python
segmento_para_graficos = "Head"
```

ou:

```python
segmento_para_graficos = "RightShoulder"
```