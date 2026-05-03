# Projeto de RPA desenvolvido em Python
# RPA File Organizer

Projeto de automação desenvolvido em Python para organizar arquivos automaticamente em diretorios com base no tipo de arquivo, simulando uma rotina administrativa comum em empresas.

## Funcionalidades

- Monitora uma pasta em tempo real
- Move arquivos para subpastas por categoria
- Organiza arquivos ja existentes ao iniciar o robo
- Evita sobrescrita ao renomear arquivos com nomes duplicados

## Tecnologias

- Python
- Watchdog
- Shutil
- Pathlib

## Estrutura de organizacao

Os arquivos sao separados em pastas como:

- `Imagens`
- `Documentos`
- `Planilhas`
- `Apresentacoes`
- `Compactados`
- `Midias`
- `Executaveis`
- `Outros`

## Como executar

1. Tenha o Python 3.10 ou superior instalado.
2. Crie e ative um ambiente virtual:

```bash
python -m venv .venv
```

Se o comando `python` nao estiver disponivel no Windows, use:

```powershell
py -m venv .venv
```

No Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

3. Instale as dependencias:

```bash
pip install -r requirements.txt
```

4. Execute o robo:

```bash
python main.py
```

Alternativa no Windows:

```powershell
py main.py
```

Por padrao, o script monitora a pasta `entrada`, criada automaticamente se ainda nao existir.

## Opcoes de uso

Monitorar uma pasta especifica:

```bash
python main.py --source "C:\caminho\da\pasta"
```

Definir uma pasta de destino diferente:

```bash
python main.py --source "C:\caminho\da\pasta" --destination "C:\caminho\organizados"
```

## Exemplo de fluxo

1. Inicie o script.
2. Adicione arquivos na pasta monitorada.
3. O robo identifica o tipo do arquivo.
4. O arquivo e movido automaticamente para a subpasta correspondente.

## Possiveis melhorias

- Adicionar interface grafica
- Registrar logs em arquivo
- Permitir categorias personalizadas por configuracao
- Criar testes automatizados


## Licença

- Este projeto está sob licença MIT