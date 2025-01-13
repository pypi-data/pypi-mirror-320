import pandas as pd
import locale
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from typing import List
from modelo_dados.producao import Categoria_prod, Produto_prod, ProdutividadeAnual
from modelo_dados.producao import RepositorioCategorias_prod, RepositorioProdutos_prod, RepositorioProdutividadesAnuais
from modelo_dados.processamento import EnumTipoUva_proc, Categoria_proc, Cultivar_proc, ProcessamentoAnual
from modelo_dados.processamento import RepositorioCategorias_proc, RepositorioCultivar_proc, RepositorioProcessamentosAnuais
from modelo_dados.comercializacao import Categoria_com, Produto_com, ComercializacaoAnual
from modelo_dados.comercializacao import RepositorioCategorias_com, RepositorioProdutos_com, RepositorioComercializacoesAnuais

class SiteEmbrapa:
    """
    Possui os métodos necessários para se fazer o webscrapping dos dados do site.
    Também gerencia um tipo de cache dos dados para quando o site estiver fora do ar.
    
    """
    def __init__(self):

        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

        self.webscrapping = WebscrappingSiteEmbrapa("http://vitibrasil.cnpuv.embrapa.br/index.php")

        self.repositorio_categorias_prod = RepositorioCategorias_prod()
        self.repositorio_produtos_prod = RepositorioProdutos_prod()
        self.repositorio_produtividades = RepositorioProdutividadesAnuais()

        self.repositorio_categorias_proc = RepositorioCategorias_proc()
        self.repositorio_cultivares_proc = RepositorioCultivar_proc()
        self.repositorio_processamentos = RepositorioProcessamentosAnuais()

        self.repositorio_categorias_com = RepositorioCategorias_com()
        self.repositorio_produtos_com = RepositorioProdutos_com()
        self.repositorio_comercializacoes = RepositorioComercializacoesAnuais()

    def obterProducoesPorAno(self, ano: int) -> List[ProdutividadeAnual]:
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
        produtividadesEmCache = self.repositorio_produtividades.buscar_produtividadesPorAno(ano)
        if len(produtividadesEmCache) == 0:
            produtividadesEmCache = self.carregaRepoProdutividadePorAnoFromWebscrapping(ano)

        categoria = self.repositorio_categorias_prod.buscar_categoria_por_nome(nomeCategoria)
        if categoria == None:
            return 0
        
        producao_total_categoria = self.repositorio_produtividades.buscarProdutividadeTotalDeCategoriaPorAno(categoria, ano)
        return producao_total_categoria

    def obterProcessamentoPorAnoTipoUva(self, ano: int, tipo_uva: EnumTipoUva_proc) -> List[ProcessamentoAnual]:
        """
        Recupera do site da embrapa, toda o processamento de um ano e tipo uva.  Se o site estiver offline, retornará o processamento de cache obtido previamente.
        
        """
        processamentoEmCache = self.repositorio_processamentos.buscar_processamentosPorAno_TipoUva(ano, tipo_uva)
        if len(processamentoEmCache) == 0:
            processamentoEmCache = self.carregaRepoProcessamentoPorAnoTipoUvaFromWebscrapping(ano, tipo_uva)
        return processamentoEmCache

    def obterProcessamentoTotalDeCategoriaPorAnoTipoUva(self, nomeCategoria: str, ano: int, tipo_uva: EnumTipoUva_proc) -> int:
        """
        Recupera do site da embrapa, toda da processamento de uma categoria em um ano, por TipoUva.  Se o site estiver offline, retornará o processamento de cache obtido previamente.
        
        """
        processamentoEmCache = self.repositorio_processamentos.buscar_processamentosPorAno_TipoUva(ano, tipo_uva)
        if len(processamentoEmCache) == 0:
            processamentoEmCache = self.carregaRepoProcessamentoPorAnoTipoUvaFromWebscrapping(ano, tipo_uva)

        categoria = self.repositorio_categorias_proc.buscar_categoria_por_nome(nomeCategoria)
        if categoria == None:
            return 0
        
        processamento_total_categoria = self.repositorio_processamentos.buscarProcessamentoTotalDeCategoriaPorAno_TipoUva(categoria, ano, tipo_uva)
        return processamento_total_categoria

    def obterComercializacoesPorAno(self, ano: int) -> List[ComercializacaoAnual]:
        """
        Recupera do site da embrapa, toda a comercialização de um ano.  Se o site estiver offline, retornará a produção de cache obtido previamente.
        
        """
        comercializacoesEmCache = self.repositorio_comercializacoes.buscar_comercializacoesPorAno(ano)
        if len(comercializacoesEmCache) == 0:
            comercializacoesEmCache = self.carregaRepoComercializacaoPorAnoFromWebscrapping(ano)
        return comercializacoesEmCache

    def obterComercializacaoTotalDeCategoriaPorAno(self, nomeCategoria: str, ano: int) -> int:
        """
        Recupera do site da embrapa, toda da comercialização de uma categoria em um ano.  Se o site estiver offline, retornará a produção de cache obtido previamente.
        
        """
        comercializacoesEmCache = self.repositorio_comercializacoes.buscar_comercializacoesPorAno(ano)
        if len(comercializacoesEmCache) == 0:
            comercializacoesEmCache = self.carregaRepoComercializacaoPorAnoFromWebscrapping(ano)

        categoria = self.repositorio_categorias_com.buscar_categoria_por_nome(nomeCategoria)
        if categoria == None:
            return 0
        
        comercializacao_total_categoria = self.repositorio_comercializacoes.buscarComercializacaoTotalDeCategoriaPorAno(categoria, ano)
        return comercializacao_total_categoria
    
    def carregaRepoProdutividadePorAnoFromWebscrapping(self, ano: int) -> List[ProdutividadeAnual]:
        tags_tr_do_tbody = self.webscrapping.obterProducaoPorAno(ano)

        categoriaAtual: Categoria_prod = None
        produtoAtual: Produto_prod = None
        produtividadeAnualAtual: ProdutividadeAnual = None

        """
            Carrega self.repositorio_produtos_prod, self.repositorio_categorias_prod e self.repositorio_produtividades com os elementos vindos do webscrapping
        """
        for tag_tr in tags_tr_do_tbody:
            tags_td = tag_tr.find_elements(By.TAG_NAME, "td")
            if(len(tags_td) == 2):
                if(tags_td[0].get_attribute("class") == "tb_item"):
                    nomeCategoria = tags_td[0].text
                    categoriaAtual = self.repositorio_categorias_prod.buscar_categoria_por_nome(nomeCategoria)
                    if categoriaAtual == None:
                        categoriaAtual = Categoria_prod(nomeCategoria)
                        self.repositorio_categorias_prod.adicionar_categoria(categoriaAtual)
                elif(tags_td[0].get_attribute("class") == "tb_subitem"):
                    nomeProduto = tags_td[0].text
                    produtoAtual = self.repositorio_produtos_prod.buscar_produto_por_nome_categoria(nomeProduto, categoriaAtual)
                    if produtoAtual == None:
                        produtoAtual = Produto_prod(nomeProduto, categoriaAtual)
                        self.repositorio_produtos_prod.adicionar_produto(produtoAtual)
                    produtividadeAnualAtual = ProdutividadeAnual(ano, tags_td[1].text, produtoAtual)
                    self.repositorio_produtividades.adicionar_produtividade(produtividadeAnualAtual)
        return self.repositorio_produtividades.buscar_produtividadesPorAno(ano)

    def carregaRepoProcessamentoPorAnoTipoUvaFromWebscrapping(self, ano: int, tipo_uva: EnumTipoUva_proc) -> List[ProcessamentoAnual]:
        tags_tr_do_tbody = self.webscrapping.obterProcessamentoPorAno_TipoUva(ano, tipo_uva)

        categoriaAtual: Categoria_proc = None
        cultivarAtual: Cultivar_proc = None
        processamentoAnualAtual: ProcessamentoAnual = None

        """
            Carrega self.repositorio_produtos_proc, self.repositorio_categorias_proc e self.repositorio_processamentos com os elementos vindos do webscrapping
        """
        for tag_tr in tags_tr_do_tbody:
            tags_td = tag_tr.find_elements(By.TAG_NAME, "td")
            if(len(tags_td) == 2):
                if(tags_td[0].get_attribute("class") == "tb_item"):
                    nomeCategoria = tags_td[0].text
                    categoriaAtual = self.repositorio_categorias_proc.buscar_categoria_por_nome(nomeCategoria)
                    if categoriaAtual == None:
                        categoriaAtual = Categoria_proc(nomeCategoria)
                        self.repositorio_categorias_proc.adicionar_categoria(categoriaAtual)
                    # no caso de SEMCLASSIFICACAO, o site não possui tb_subitem, apresentado o total de produção na própria categoria
                    # neste caso, estamos criando um processamento com o total processado para refletir nas consultas de totalização
                    if tipo_uva == EnumTipoUva_proc.SEMCLASSIFICACAO:
                        nomeCultivar = nomeCategoria
                        cultivarAtual = self.repositorio_cultivares_proc.buscar_cultivar_por_nome_categoria_tipo(nomeCultivar, categoriaAtual, tipo_uva)
                        if cultivarAtual == None:
                            cultivarAtual = Cultivar_proc(nomeCultivar, categoriaAtual, tipo_uva)
                            self.repositorio_cultivares_proc.adicionar_cultivar(cultivarAtual)
                        processamentoAnualAtual = ProcessamentoAnual(ano, tags_td[1].text, cultivarAtual)
                        self.repositorio_processamentos.adicionar_processamento(processamentoAnualAtual)
                elif(tags_td[0].get_attribute("class") == "tb_subitem"):
                    nomeCultivar = tags_td[0].text
                    cultivarAtual = self.repositorio_cultivares_proc.buscar_cultivar_por_nome_categoria_tipo(nomeCultivar, categoriaAtual, tipo_uva)
                    if cultivarAtual == None:
                        cultivarAtual = Cultivar_proc(nomeCultivar, categoriaAtual, tipo_uva)
                        self.repositorio_cultivares_proc.adicionar_cultivar(cultivarAtual)
                    processamentoAnualAtual = ProcessamentoAnual(ano, tags_td[1].text, cultivarAtual)
                    self.repositorio_processamentos.adicionar_processamento(processamentoAnualAtual)
        return self.repositorio_processamentos.buscar_processamentosPorAno_TipoUva(ano, tipo_uva)

    def carregaRepoComercializacaoPorAnoFromWebscrapping(self, ano: int) -> List[ProdutividadeAnual]:
        tags_tr_do_tbody = self.webscrapping.obterComercializacaoPorAno(ano)

        categoriaAtual: Categoria_prod = None
        produtoAtual: Produto_prod = None
        comercializacaoAnualAtual: ComercializacaoAnual = None
        ultima_tag_foi_categoria: bool = False

        """
            Carrega self.repositorio_produtos_com, self.repositorio_categorias_com e self.repositorio_comercializacoes com os elementos vindos do webscrapping
        """
        for tag_tr in tags_tr_do_tbody:
            tags_td = tag_tr.find_elements(By.TAG_NAME, "td")
            if(len(tags_td) == 2):
                if tags_td[0].get_attribute("class") == "tb_item":
                    if ultima_tag_foi_categoria == True:
                        # variáveis nomeCategoria e categoriaAtual estão com valores da linha anterior(linha de categoria que não tem produtos listados abaixo)
                        nomeProduto = nomeCategoria 
                        produtoAtual = self.repositorio_produtos_com.buscar_produto_por_nome_categoria(nomeProduto, categoriaAtual)
                        if produtoAtual == None:
                            produtoAtual = Produto_com(nomeProduto, categoriaAtual)
                            self.repositorio_produtos_com.adicionar_produto(produtoAtual)
                        comercializacaoAnualAtual = ComercializacaoAnual(ano, quantidadeCategoria, produtoAtual) # quantidadeCategoria foi setado na linha de categoria anterior.  No loop anterior do for.
                        self.repositorio_comercializacoes.adicionar_comercializacao(comercializacaoAnualAtual)
                    # processa os dados da linha atual (tag_tr) do tbody do site.  Linha da categoria atual
                    nomeCategoria = tags_td[0].text
                    quantidadeCategoria = tags_td[1].text
                    categoriaAtual = self.repositorio_categorias_com.buscar_categoria_por_nome(nomeCategoria)
                    if categoriaAtual == None:
                        categoriaAtual = Categoria_com(nomeCategoria)
                        self.repositorio_categorias_com.adicionar_categoria(categoriaAtual)
                    ultima_tag_foi_categoria = True
                elif(tags_td[0].get_attribute("class") == "tb_subitem"):
                    nomeProduto = tags_td[0].text
                    produtoAtual = self.repositorio_produtos_com.buscar_produto_por_nome_categoria(nomeProduto, categoriaAtual)
                    if produtoAtual == None:
                        produtoAtual = Produto_com(nomeProduto, categoriaAtual)
                        self.repositorio_produtos_com.adicionar_produto(produtoAtual)
                    comercializacaoAnualAtual = ComercializacaoAnual(ano, tags_td[1].text, produtoAtual)
                    self.repositorio_comercializacoes.adicionar_comercializacao(comercializacaoAnualAtual)
                    ultima_tag_foi_categoria = False
        return self.repositorio_comercializacoes.buscar_comercializacoesPorAno(ano)


class WebscrappingSiteEmbrapa:
    """
    Realiza o webscrapping na página especifica do site, de acordo com o método utilizado. (Producao, Processamento etc...)

    """
    def __init__(self, urlBase: str):
        self.UrlBase = urlBase
                # Defina as opções do navegador
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        # Adiciona o modo headless
        # chrome_options.add_argument("--headless")
        # (Opcional) Evita possíveis erros de hardware/gpu
        # chrome_options.add_argument("--disable-gpu")

        # O webdriver_manager cuida de baixar a versão correta do ChromeDriver
        self.driverChrome = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def obterProducaoPorAno(self, ano: int) -> list:
        """
        Realiza o Webscrapping no site da embrapa.  Retornalista de elementos das tags_tr_do_tbody.

        """
        url = f"{self.UrlBase}?ano={ano}&opcao=opt_02" 
        xpath = "/html/body/table[4]/tbody/tr/td[2]/div/div/table[1]/tbody/tr"

        retorno = self.obterElementosTR(url, xpath)

        return retorno;

    def obterProcessamentoPorAno_TipoUva(self, ano: int, tipo_uva: EnumTipoUva_proc) -> list:
        """
        Realiza o Webscrapping no site da embrapa.  Retornalista de elementos das tags_tr_do_tbody.

        """
        if tipo_uva == EnumTipoUva_proc.VINIFERAS:
            subopcao_tipouva = "subopt_01"
        elif tipo_uva == EnumTipoUva_proc.AMERICANASEHIBRIDAS:
            subopcao_tipouva = "subopt_02"
        elif tipo_uva == EnumTipoUva_proc.UVASDEMESA:
            subopcao_tipouva = "subopt_03"
        elif tipo_uva == EnumTipoUva_proc.SEMCLASSIFICACAO:
            subopcao_tipouva = "subopt_04"
        else:
            subopcao_tipouva = "subopt_04"

        url = f"{self.UrlBase}?ano={ano}&opcao=opt_03&subopcao={subopcao_tipouva}" 
        xpath = "/html/body/table[4]/tbody/tr/td[2]/div/div/table[1]/tbody/tr"

        retorno = self.obterElementosTR(url, xpath)

        return retorno;

    def obterComercializacaoPorAno(self, ano: int) -> list:
        """
        Realiza o Webscrapping no site da embrapa.  Retornalista de elementos das tags_tr_do_tbody.

        """
        url = f"{self.UrlBase}?ano={ano}&opcao=opt_04" 
        xpath = "/html/body/table[4]/tbody/tr/td[2]/div/div/table[1]/tbody/tr"

        retorno = self.obterElementosTR(url, xpath)

        return retorno;

    def obterElementosTR(self, url: str, xpath_tbody: str) -> list:
        """
        Abre a página da url e obtem lista de WebElement

        """
        # Abre a página no navegador
        self.driverChrome.get(url)

        # Encontra todos os elementos <a> que têm links
        # link_elements = driver.find_elements('tag name', 'a')

        tags_tr_do_tbody = self.driverChrome.find_elements(By.XPATH, xpath_tbody)

        return tags_tr_do_tbody
