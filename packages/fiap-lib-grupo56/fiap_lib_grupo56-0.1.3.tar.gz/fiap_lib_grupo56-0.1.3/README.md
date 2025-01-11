# lib_grupo56

Uma biblioteca Python para o Tech Challenge - Fase 1 - 4MLET - Grupo 56

Membros du grupo 56:
Fábio Vargas Matos

# Objetivo do Tech Challenge - Fase 1

Desenvolver e publicar uma API para extração de dados acerca de produção de vinhos e outros produtos da uva.  Os dados são extraídos do site da Embrapa (https://vitibrasil.cnpuv.embrapa.br/)

# Objetivo da Biblioteca

* Modelo de dados

Fornecer as classes necessárias para o mapeamento dos dados extraídos do site e disponibilizados pela API.

Classes



## Instalação

Você pode instalar a biblioteca via pip:

```bash
pip install lib_grupo56
```

## O que está disponível

Modelo de Dados

Classes que modelam 

```python
from lib_grupo56.modelo_dados import 

valor_inicial = 1000
valor_final = 1500

retorno = calcular_retorno_investimento(valor_inicial, valor_final)
print(f"Retorno do investimento: {retorno:.2f}%")

valor_final_juros = calcular_juros_compostos(valor_inicial, 6, 5)
print(f"Valor final com juros compostos: R${valor_final_juros:.2f}")
```