import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from typing import List
from modelo_dados import RepositorioCategorias, RepositorioProdutos, RepositorioProdutividadesAnuais, Categoria, Produto, ProdutividadeAnual

class SiteEmbrapa:
    """
    Possui os métodos necessários para se fazer o webscrapping dos dados do site.
    Também gerencia um tipo de cache dos dados para quando o site estiver fora do ar.
    
    """
    def __init__(self):
        self.UrlBase = "http://vitibrasil.cnpuv.embrapa.br/index.php"
        self.repositorio_categorias = RepositorioCategorias()
        self.repositorio_produtos = RepositorioProdutos()
        self.repositorio_produtividades = RepositorioProdutividadesAnuais()

    def obterProducaoGeralPorAno(self, ano: int) -> List[ProdutividadeAnual]:
        """
        Recupera do site da embrapa, toda a produção de um ano.  Se o site estiver offline, retornará a produção de cache obtido previamente.
        
        """
        produtividadesEmCache = self.repositorio_produtividades.buscar_produtividadesPorAno(ano)
        if len(produtividadesEmCache) == 0:
            produtividadesEmCache = self.carregaRepoProdutividadePorAnoFromWebscrapping(ano)
        return produtividadesEmCache

    def obterProducaoTotalDeCategoriaPorAno(self, nomeCategoria: str, ano: int) -> int:
        """
        Recupera do site da embrapa, toda da produção de uma categoria em um ano.  Se o site estiver offline, retornará a produção de cache obtido previamente.
        
        """
        categoria = self.repositorio_categorias.buscar_categoria_por_nome(nomeCategoria)
        if categoria == None:
            return 0
        
        produtividadesEmCache = self.repositorio_produtividades.buscar_produtividadesPorAno(ano)
        if len(produtividadesEmCache) == 0:
            produtividadesEmCache = self.carregaRepoProdutividadePorAnoFromWebscrapping(ano)

        producao_total_categoria = self.repositorio_produtividades.buscarProdutividadeTotalDeCategoriaPorAno(categoria, ano)
        return producao_total_categoria

    def carregaRepoProdutividadePorAnoFromWebscrapping(self, ano: int) -> List[ProdutividadeAnual]:
        webscrapping = WebscrappingSiteEmbrapa(self.UrlBase)
        tags_tr_do_tbody = webscrapping.obterProducaoGeralPorAno(ano)

        categoriaAtual: Categoria = None
        produtoAtual: Produto = None

        """
            Carrega self.repositorio_produtos, self.repositorio_categorias e self.repositorio_produtividades com os elementos vindos do webscrapping
        """
        for tag_tr in tags_tr_do_tbody:
            tags_td = tag_tr.find_elements(By.TAG_NAME, "td")
            if(len(tags_td) == 2):
                if(tags_td[0].get_attribute("class") == "tb_item"):
                    nomeCategoria = tags_td[0].text
                    categoriaAtual = self.repositorio_categorias.buscar_categoria_por_nome(nomeCategoria)
                    if categoriaAtual == None:
                        categoriaAtual = Categoria(nomeCategoria)
                        self.repositorio_categorias.adicionar_categoria(categoriaAtual)
                elif(tags_td[0].get_attribute("class") == "tb_subitem"):
                    nomeProduto = tags_td[0].text
                    produtoAtual = self.repositorio_produtos.buscar_produto_por_nome_categoria(nomeProduto, categoriaAtual)
                    if produtoAtual == None:
                        produtoAtual = Produto(nomeProduto, categoriaAtual)
                        self.repositorio_produtos.adicionar_produto(produtoAtual)
                    produtividadeAnualAtual = ProdutividadeAnual(ano, tags_td[1].text, produtoAtual)
                    self.repositorio_produtividades.adicionar_produtividade(produtividadeAnualAtual)
        return self.repositorio_produtividades.buscar_produtividadesPorAno(ano)


class WebscrappingSiteEmbrapa:
    """
    Realiza o webscrapping na página especifica do site, de acordo com o método utilizado. (Producao, Processamento etc...)

    """
    def __init__(self, urlBase: str):
        self.UrlBase = urlBase

    def obterProducaoGeralPorAno(self, ano: int) -> list:
        """
        Realiza o Webscrapping no site da embrapa.  Retornalista de elementos das tags_tr_do_tbody.

        """
        url = f"{self.UrlBase}?ano={ano}&opcao=opt_02" 
        xpath = "/html/body/table[4]/tbody/tr/td[2]/div/div/table[1]/tbody/tr"

        retorno = self.obterElementosTR(url, xpath)

        return retorno;


    def obterElementosTR(self, url: str, xpath_tbody: str) -> list:
        """
        Abre a página da url e obtem lista de WebElement

        """
        # Defina as opções do navegador
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")

        # O webdriver_manager cuida de baixar a versão correta do ChromeDriver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        # Abre a página no navegador
        driver.get(url)

        # Encontra todos os elementos <a> que têm links
        # link_elements = driver.find_elements('tag name', 'a')

        tags_tr_do_tbody = driver.find_elements(By.XPATH, xpath_tbody)

        return tags_tr_do_tbody
