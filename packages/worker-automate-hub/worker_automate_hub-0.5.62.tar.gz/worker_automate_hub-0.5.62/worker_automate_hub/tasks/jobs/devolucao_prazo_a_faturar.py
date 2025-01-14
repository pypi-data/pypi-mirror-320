import getpass
import warnings
import os
import re
import io
import uuid

import pyautogui
import pytesseract
from datetime import datetime, timedelta
from pywinauto.application import Application
from pypdf import PdfReader
from PIL import Image, ImageEnhance
from pywinauto.keyboard import send_keys
import win32clipboard
from pywinauto_recorder.player import set_combobox
from rich.console import Console
from worker_automate_hub.api.ahead_service import save_xml_to_downloads
from worker_automate_hub.api.client import (
    get_config_by_name,
    get_status_nf_emsys,
    send_file,
)
from worker_automate_hub.models.dto.rpa_historico_request_dto import (
    RpaHistoricoStatusEnum,
    RpaRetornoProcessoDTO,
    RpaTagDTO,
    RpaTagEnum,
)
from worker_automate_hub.models.dto.rpa_processo_entrada_dto import (
    RpaProcessoEntradaDTO,
)
from worker_automate_hub.utils.logger import logger
from worker_automate_hub.utils.util import (
    e_ultimo_dia_util,
    delete_xml,
    ocr_warnings,
    ocr_by_class,
    nf_busca_nf_saida,
    pessoas_ativa_cliente_fornecedor,
    nf_devolucao_liquidar_cupom,
    gerenciador_nf_header,
    cadastro_pre_venda_header,
    incluir_registro,
    is_window_open,
    is_window_open_by_class,
    kill_all_emsys,
    login_emsys,
    select_documento_type,
    set_variable,
    type_text_into_field,
    worker_sleep,
    post_partner,
)

pyautogui.PAUSE = 0.5
pyautogui.FAILSAFE = False
console = Console()


async def devolucao_prazo_a_faturar(task: RpaProcessoEntradaDTO) -> RpaRetornoProcessoDTO:
    """
    Processo que relazia entrada de notas no ERP EMSys(Linx).

    """
    try:
        #DEFINIR CONSTANTE DEFAULT PARA O ASSETS 
        ASSETS_PATH = "assets"
        # Get config from BOF
        config = await get_config_by_name("login_emsys")
        try:
            aliquota_icms = await get_config_by_name("Aliquota_ICMS")
            conconfig_aliquota_icms = aliquota_icms.conConfiguracao.get("aliquotas")
        except Exception as e:
            return RpaRetornoProcessoDTO(
                sucesso=False,
                retorno=f"Não foi possivel recuperar o valor da configuração de Aliquota, erro: {e}.",
                status=RpaHistoricoStatusEnum.Falha,
                tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
            )
        console.print(task)

        # Seta config entrada na var nota para melhor entendimento
        nota = task.configEntrada

        #Definindo Variaveis com Escopo global
        numero_cupom_fiscal = nota.get("numCupomNotaFiscal")
        cod_cliente_correto = nota.get("codClienteCorreto")
        cod_cliente_incorreto = nota.get("codClienteIncorreto")
        steps = ""
        numero_nota_fiscal = ""
        valor_nota_fiscal = ""
        item_arla = False
        cidade_cliente = ""
        data_hoje = datetime.today().strftime('%d/%m/%Y')
        multiplicador_timeout = int(float(task.sistemas[0].timeout))
        set_variable("timeout_multiplicador", multiplicador_timeout)

        #VERIFICANDO ENTRADA 
        historico_id = task.historico_id
        if historico_id:
            console.print("Historico ID recuperado com sucesso...\n")
        else:
            console.print("Não foi possivel recuperar o histórico do ID, não sendo possivel enviar os arquivo gerados como retorno...\n")
            return RpaRetornoProcessoDTO(
                sucesso=False,
                retorno="Não foi possivel recuperar o histórico do ID, não sendo possivel enviar os arquivo gerados como retorno",
                status=RpaHistoricoStatusEnum.Falha,
                tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
            ) 

        # Fecha a instancia do emsys - caso esteja aberta
        await kill_all_emsys()

        #Validar se é o ultimo dia 
        if await e_ultimo_dia_util():
            return RpaRetornoProcessoDTO(
                sucesso=False,
                retorno="Não será possivel processar devido a regra - 'Não deve ser processado nenhuma devolução no último dia útil do mês vigente'",
                status=RpaHistoricoStatusEnum.Falha,
                tags=[RpaTagDTO(descricao=RpaTagEnum.Negocio)]
        )

        #Realizando o login
        app = Application(backend="win32").start("C:\\Rezende\\EMSys3\\EMSys3.exe")
        warnings.filterwarnings("ignore",category=UserWarning,message="32-bit application should be automated using 32-bit Python")
        console.print("\nEMSys iniciando...", style="bold green")
        return_login = await login_emsys(config.conConfiguracao, app, task)
        if return_login.sucesso == True:
            console.print("Processo de login realizado com sucesso... \n")
        else:
            logger.info(f"\nError Message: {return_login.retorno}")
            console.print(f"\nError Message: {return_login.retorno}", style="bold red")
            return return_login

        #VALIDAR SE CLIENTE É FIDIC
        #REGRA PARA INICIAR ONDE PAROU, TEMPORARIO
        init = 1
        if init == 2:
            console.print("Validando se o Cliente é FIDC...\n")
            if nota.get("clienteFIDC").lower() == 'não':
                #HABILITAR CLIENTE E FORNECEDOR PARA COD INCORRETO
                console.print("Seguindo com o processo de habilitar Cliente e Fornecedor para andamento do processo.. \n")
                type_text_into_field("Pessoas", app["TFrmMenuPrincipal"]["Edit"], True, "50")
                pyautogui.press("enter")
                send_keys("{DOWN " + ("2") + "}")
                pyautogui.press("enter")
                
                await worker_sleep(2)
                console.print("Verificando se o cliente esta ativo como Cliente e como Fornecedor... \n")
                ativar_cliente_fornecedor = await pessoas_ativa_cliente_fornecedor(cod_cliente_incorreto, True, True)
                if ativar_cliente_fornecedor.sucesso == True:
                    steps += 'ETAPA 00 - CLIENTE E FORNECEDOR - ATIVADOS COM SUCESSO'
                    console.log(ativar_cliente_fornecedor.retorno, style="bold green")
                else:
                    return RpaRetornoProcessoDTO(
                        sucesso=False,
                        retorno=ativar_cliente_fornecedor.retorno,
                        status=RpaHistoricoStatusEnum.Falha, 
                        tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                    )
                
                #REALIZAR PROCESSO DE NOTA FISCAL DE SAIDA 
                type_text_into_field("Nota Fiscal de Saida", app["TFrmMenuPrincipal"]["Edit"], True, "50")
                pyautogui.press("enter")
                await worker_sleep(2)
                pyautogui.press('down')
                pyautogui.press("enter")
                console.print(f"\nPesquisa: 'Nota Fiscal de Saída' realizada com sucesso",style="bold green")
                await worker_sleep(6)

                busca_nf_saida = await nf_busca_nf_saida(numero_cupom_fiscal)
                if busca_nf_saida.sucesso == True:
                    console.log(busca_nf_saida.retorno, style="bold green")
                else:
                    retorno = f"{busca_nf_saida.retorno} \nEtapas Executadas:\n{steps}"
                    return RpaRetornoProcessoDTO(
                        sucesso=False,
                        retorno=retorno,
                        status=RpaHistoricoStatusEnum.Falha, 
                        tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                    )

                
                #VERIFICANDO A EXISTENCIA DE WARNINGS 
                console.print("Verificando a existência de Warning... \n")
                warning_pop_up = await is_window_open("Warning")
                if warning_pop_up["IsOpened"] == True:
                    console.print("possui Pop-up de Warning, analisando... \n")
                    ocr_pop_warning = await ocr_warnings(numero_cupom_fiscal)
                    if ocr_pop_warning.sucesso == True:
                        retorno = f"POP UP Warning não mapeado para seguimento do processo, mensagem: {ocr_pop_warning.retorno} \nEtapas Executadas:\n{steps}"
                        return RpaRetornoProcessoDTO(
                            sucesso=False,
                            retorno=retorno,
                            status=RpaHistoricoStatusEnum.Falha,
                            tags=[RpaTagDTO(descricao=RpaTagEnum.Negocio)]
                        )
                    else:
                        retorno = f"{ocr_pop_warning.retorno} \nEtapas Executadas:\n{steps}"
                        return RpaRetornoProcessoDTO(
                            sucesso=False,
                            retorno=retorno,
                            status=RpaHistoricoStatusEnum.Falha,
                            tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                        )
                else:
                    console.print("Não possui pop de Warning...\n")
                

                #VERIFICANDO SE O BOTÃO IR PARA A NOTA FATURA
                console.print("Verificando o status do Botão [Ir para Nota Fatura]...\n")
                try:
                    btn_ir_para_nota = pyautogui.locateOnScreen(ASSETS_PATH + "\\notas_saida\\ir_para_nota_a_fatura_esmaecido.png", confidence=0.8)
                    if btn_ir_para_nota:
                        console.print("Botão 'Ir para nota de faturar' inativo, seguindo com o processo...\n")
                        app = Application().connect(class_name="TFrmNotaFiscalSaida", timeout=60)
                        main_window = app["TFrmNotaFiscalSaida"]
                        main_window.set_focus()
                        main_window.close()
                    else:
                        retorno = f"Botão [Ir para nota de faturar] está ativo, impossibilitando realizar a devolução \nEtapas Executadas:\n{steps}"
                        return RpaRetornoProcessoDTO(
                            sucesso=False,
                            retorno=retorno,
                            status=RpaHistoricoStatusEnum.Falha,
                            tags=[RpaTagDTO(descricao=RpaTagEnum.Negocio)]
                        )     
                except Exception as e:
                    return RpaRetornoProcessoDTO(
                        sucesso=False,
                        retorno=f"Não foi possivel verificar o botão [Ir para nota de faturar], erro: {e}",
                        status=RpaHistoricoStatusEnum.Falha,
                        tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                    )

                #Para liquidar o cupom
                type_text_into_field("Titulos a receber", app["TFrmMenuPrincipal"]["Edit"], True, "50")
                pyautogui.press("enter")
                await worker_sleep(2)
                pyautogui.press("enter")

                
                liquidar_cupom = await nf_devolucao_liquidar_cupom(numero_cupom_fiscal, data_hoje)
                if liquidar_cupom.sucesso == True:
                    console.log(liquidar_cupom.retorno, style="bold green")
                    steps += 'ETAPA 01 - Processo de liquidar cupom finalizado com sucesso'
                else:
                    descricao_tag = liquidar_cupom.tags[0]
                    retorno = f"{liquidar_cupom.retorno} \nEtapas Executadas:\n{steps}"
                    return RpaRetornoProcessoDTO(
                        sucesso=False,
                        retorno=retorno,
                        status=RpaHistoricoStatusEnum.Falha, 
                        tags=[RpaTagDTO(descricao=descricao_tag.descricao)]
                    )

            
        #ETAPA 14 A 18
        #STEP 2 - EMISSAO DA NOTA 
        type_text_into_field("Nota Fiscal de Entrada", app["TFrmMenuPrincipal"]["Edit"], True, "50")
        pyautogui.press("enter")
        await worker_sleep(2)
        pyautogui.press("enter")
        console.print(f"\nPesquisa: 'Nota Fiscal de Entrada' realizada com sucesso",style="bold green",
        )

        # Procura campo documento
        console.print("Navegando pela Janela de Nota Fiscal de Entrada...\n")
        document_type = await select_documento_type("NFe - NOTA FISCAL ELETRONICA PROPRIA - DANFE SERIE 077")
        if document_type.sucesso == True:
            console.log(document_type.retorno, style="bold green")
        else:
            retorno = f"{document_type.retorno} \nEtapas Executadas:\n{steps}"
            return RpaRetornoProcessoDTO(
                sucesso=False,
                retorno=retorno,
                status=RpaHistoricoStatusEnum.Falha, 
                tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
            )

        await worker_sleep(4)

        app = Application().connect(class_name="TFrmNotaFiscalEntrada", timeout=60)
        main_window = app["TFrmNotaFiscalEntrada"]

        main_window.set_focus()
        await worker_sleep(3)

        console.print("Controles encontrados na janela 'Nota Fiscal de Entrada, navegando entre eles...\n")
        panel_TNotebook = main_window.child_window(class_name="TNotebook", found_index=0)
        panel_TPage = panel_TNotebook.child_window(class_name="TPage", found_index=0)
        panel_TPageControl = panel_TPage.child_window(class_name="TPageControl", found_index=0)
        panel_TTabSheet = panel_TPageControl.child_window(class_name="TTabSheet", found_index=0)

        #SELECIONANDO O TIPO NOTA
        console.print("SELECIONANDO O TIPO NOTA...\n")
        panel_tipo_nota = panel_TPageControl.child_window(class_name="TDBIGroupBox", found_index=1)
        radio_nota_devolucao = panel_tipo_nota.child_window(class_name="TDBIRadioButton", found_index=1)
        radio_nota_devolucao.click()
        await worker_sleep(1)

        #INSERINDO A ENTRADA E EMISSÃO 
        console.print("INSERINDO A ENTRADA E EMISSÃO ...\n")
        field_entrada = panel_TTabSheet.child_window(class_name="TDBIEditDate", found_index=1)
        field_emissao = panel_TTabSheet.child_window(class_name="TDBIEditDate", found_index=0)
        field_entrada.set_edit_text(data_hoje)
        field_emissao.set_edit_text(data_hoje)
        await worker_sleep(1)

        #INSERINDO CODIGO DO FORNECEDOR
        console.print("INSERINDO CODIGO DO FORNECEDOR ...\n")
        field_fornecedor = panel_TTabSheet.child_window(class_name="TDBIEditCode", found_index=0)
        field_fornecedor.set_edit_text(cod_cliente_incorreto)
        pyautogui.press("tab")

        #SELECIONAO A NOP 
        console.print("SELECIONAO A NOP...\n")
        select_box_nop_select = main_window.child_window(class_name="TDBIComboBox", found_index=0)
        select_box_nop_select.click()
        set_combobox("||List", "1662 - DEVOLUÇÃO DE VENDA MERC. ADQ. TERCEIROS- 1.662 DEV COMB C/FI")
        await worker_sleep(2)

        try:
            pesquisar_icon = pyautogui.locateOnScreen(ASSETS_PATH + "\\emsys\\selecionar_venda.png", confidence=0.8)
            pyautogui.click(pesquisar_icon)
            await worker_sleep(5)
        except Exception as e:
            retorno = f"Não foi possivel clicar no botão Selecionar Venda, erro: {e} \nEtapas Executadas:\n{steps}"
            return RpaRetornoProcessoDTO(
                sucesso=False,
                retorno=retorno,
                status=RpaHistoricoStatusEnum.Falha,
                tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
            )
        
        await worker_sleep(2)
        pesquisar_venda_devolucao = await is_window_open_by_class("TFrmPesquisarVendaDevolucao", "TFrmPesquisarVendaDevolucao")
        if pesquisar_venda_devolucao["IsOpened"] == True:
            app = Application().connect(class_name="TFrmPesquisarVendaDevolucao", timeout=60)
            main_window = app["TFrmPesquisarVendaDevolucao"]
            main_window.set_focus()

            panel_filtro = main_window.child_window(class_name="TGroupBox", found_index=0)
            #INSERINDO O NUMERO VENDA
            console.print("INSERINDO O NUMERO VENDA...\n")
            field_num_venda = panel_filtro.child_window(class_name="TDBIEditString", found_index=0)
            field_num_venda.set_edit_text(numero_cupom_fiscal)
            await worker_sleep(1)

            #INSERINDO O CODIGO DO CLIENTE
            console.print("INSERINDO O CODIGO DO CLIENTE...\n")
            field_cliente = panel_filtro.child_window(class_name="TDBIEditCode", found_index=0)
            field_cliente.set_edit_text(cod_cliente_incorreto)
            await worker_sleep(1)

            try:
                pesquisar_icon = pyautogui.locateOnScreen(ASSETS_PATH + "\\emsys\\icon_pesquisa_nota_saida.png", confidence=0.8)
                pyautogui.click(pesquisar_icon)
                await worker_sleep(5)
            except Exception as e:
                retorno = f"Não foi possivel clicar na Lupa para buscar a nota fiscal, erro: {e} \nEtapas Executadas:\n{steps}"
                return RpaRetornoProcessoDTO(
                    sucesso=False,
                    retorno=retorno,
                    status=RpaHistoricoStatusEnum.Falha,
                    tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                )
        
            i = 0
            max_attempts = 17

            while i < max_attempts:
                i += 1
                console.print("Verificando se a nota foi encontrada...\n")
                try:
                    main_window.set_focus()
                    no_data_full_path = "assets\\entrada_notas\\no_data_display.png"
                    img_no_data = pyautogui.locateCenterOnScreen(no_data_full_path, confidence=0.6)
                    if img_no_data:
                        console.print("'No data display' ainda aparente. Tentando novamente...")
                        await worker_sleep(10)
                except pyautogui.ImageNotFoundException:
                    console.print("'No data display' não encontrado na tela!")
                    break

                except Exception as e:
                    console.print(f"Ocorreu um erro: {e}")
                
            
            await worker_sleep(5)
            # VERIFICANDO A EXISTENCIA DE ERRO
            erro_pop_up = await is_window_open_by_class("TMessageForm")
            if erro_pop_up["IsOpened"] == True:
                retorno = f"Nota não encontrada no EMsys na tela de Pesquisa Vendas para Devolução \nEtapas Executadas:\n{steps}"
                return RpaRetornoProcessoDTO(
                    sucesso=False,
                    retorno=retorno,
                    status=RpaHistoricoStatusEnum.Falha,
                    tags=[RpaTagDTO(descricao=RpaTagEnum.Negocio)]
                )

            main_window.set_focus()
            try:
                selecionar_todos_itens = pyautogui.locateOnScreen(ASSETS_PATH + "\\emsys\\selecinar_todos_itens_quadro_azul.png", confidence=0.8)
                pyautogui.click(selecionar_todos_itens)
                await worker_sleep(5)
            except Exception as e:
                retorno = f"Não foi possivel clicar em selecionar todos os itens na tela de Pesquisar Vendas para Devolução, erro: {e} \nEtapas Executadas:\n{steps}"
                return RpaRetornoProcessoDTO(
                    sucesso=False,
                    retorno=retorno,
                    status=RpaHistoricoStatusEnum.Falha,
                    tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                )

            try:
                pesquisar_icon = pyautogui.locateOnScreen(ASSETS_PATH + "\\emsys\\inserir.png", confidence=0.8)
                pyautogui.click(pesquisar_icon)
                await worker_sleep(5)
            except Exception as e:
                retorno = f"Não foi possivel clicar em Inserir para selecionar a nota fiscal, erro: {e} \nEtapas Executadas:\n{steps}"
                return RpaRetornoProcessoDTO(
                    sucesso=False,
                    retorno=retorno,
                    status=RpaHistoricoStatusEnum.Falha,
                    tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                )

            await worker_sleep(5)
            console.print("Navegando pela Janela de Nota Fiscal de Entrada...\n")
            app = Application().connect(class_name="TFrmNotaFiscalEntrada")
            main_window = app["TFrmNotaFiscalEntrada"]

            main_window.set_focus()
            console.print("Acessando os itens da nota... \n")
            panel_TPage = main_window.child_window(class_name="TPage", title="Formulario")
            panel_TTabSheet = panel_TPage.child_window(class_name="TcxCustomInnerTreeView")
            panel_TTabSheet.wait("visible")
            panel_TTabSheet.click()
            send_keys("^({HOME})")
            await worker_sleep(1)
            send_keys("{DOWN " + ("1") + "}")

            # CONFIRMANDO SE A ABA DE ITENS FOI ACESSADA COM SUCESSO
            panel_TPage = main_window.child_window(class_name="TPage", title="Formulario")
            panel_TPage.wait("visible")
            panel_TTabSheet = panel_TPage.child_window(class_name="TTabSheet")
            title_n_serie = panel_TPage.child_window(title="N° Série")

            console.print("Verificando se os itens foram abertos com sucesso... \n")
            if not title_n_serie:
                retorno = f"Não foi possivel acessar a aba de 'Itens da nota \nEtapas Executadas:\n{steps}"
                console.print(f"Não foi possivel acessar a aba de 'Itens da nota...\n")
                return RpaRetornoProcessoDTO(
                    sucesso=False,
                    retorno=retorno,
                    status=RpaHistoricoStatusEnum.Falha,
                    tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                )

            await worker_sleep(2)

            console.print("Acessando os itens indivualmente... \n")
            send_keys("{TAB 2}", pause=0.1)
            await worker_sleep(2)

            index = 0
            last_line_item_emsys = 'x'
        
            try:
                while True:
                    await worker_sleep(2)
                    send_keys("^({HOME})")
                    await worker_sleep(1)
                    send_keys("{DOWN " + str(index) + "}", pause=0.1)
                    await worker_sleep(1)

                    with pyautogui.hold('ctrl'):
                        pyautogui.press('c')
                    await worker_sleep(1)
                    with pyautogui.hold('ctrl'):
                        pyautogui.press('c')

                    win32clipboard.OpenClipboard()
                    line_itens_emsys = win32clipboard.GetClipboardData().strip()
                    win32clipboard.CloseClipboard()
                    console.print(f"Linha atual copiada do Emsys: {line_itens_emsys}\nUltima Linha copiada: {last_line_item_emsys}")

                    if bool(line_itens_emsys):
                        if last_line_item_emsys == line_itens_emsys:
                            break
                        else:
                            last_line_item_emsys = line_itens_emsys

                    send_keys("+{F10}")
                    await worker_sleep(1)
                    send_keys("{DOWN 2}")
                    await worker_sleep(1)
                    send_keys("{ENTER}")
                    await worker_sleep(4)

                    app = Application().connect(title="Alteração de Item")
                    main_window = app["Alteração de Item"]

                    main_window.set_focus()

                    # ITERAGINDO COM O IPI
                    tpage_ipi = main_window.child_window(
                        class_name="TPanel", found_index=0
                    )
                    ipi = tpage_ipi.child_window(
                        class_name="TDBIComboBox", found_index=2
                    )

                    ipi_value = ipi.window_text()

                    console.print(
                        f"Trabalhando com os itens, valor do IP {ipi_value}... \n"
                    )
                    if "IPI - ENTRADAS OUTROS" in ipi_value:
                        console.print(f"IPI Corretamente selecionado ... \n")
                    else:
                        console.print(
                            f"Trabalhando com os itens, valor do IP em branco, selecionando IPI 0% ... \n"
                        )
                        ipi.click_input()
                        send_keys("^({HOME})")
                        send_keys("{DOWN 6}")
                        send_keys("{ENTER}")

                        await worker_sleep(4)
                        tpage_ipi = main_window.child_window(
                            class_name="TPanel", found_index=0
                        )
                        ipi = tpage_ipi.child_window(
                            class_name="TDBIComboBox", found_index=2
                        )

                        ipi_value = ipi.window_text()

                        if "IPI - ENTRADAS OUTROS" in ipi_value:
                            console.print(
                                f"Trabalhando com os itens, sucesso ao selecionar o valor do IPI ... \n"
                            )
                        else:
                            return RpaRetornoProcessoDTO(
                                sucesso=False,
                                retorno=f"Erro ao selecionar o IPI de unidade nos itens, IPI: {ipi_value}",
                                status=RpaHistoricoStatusEnum.Falha,
                                tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                            )

                        await worker_sleep(4)

                        console.print(f"Iten selecionado com sucesso, clicando em alterar ...\n")
                        try:
                            btn_alterar = main_window.child_window(title="&Alterar")
                            btn_alterar.click()
                        except:
                            btn_alterar = main_window.child_window(title="Alterar")
                            btn_alterar.click()
                        await worker_sleep(3)

                        confirm_pop_up = await is_window_open_by_class("TMessageForm","TMessageForm")
                        if confirm_pop_up["IsOpened"] == True:
                            app_confirm = Application().connect(
                            class_name="TMessageForm"
                            )
                            main_window_confirm = app_confirm["TMessageForm"]

                            btn_yes = main_window_confirm["&Yes"]
                            try:
                                btn_yes.click()
                                await worker_sleep(3)
                                console.print("O botão Yes foi clicado com sucesso.", style="green")
                                main_window.close()
                            except:
                                return RpaRetornoProcessoDTO(
                                    sucesso=False,
                                    retorno=f"Não foi possivel clicar em Yes durante a alteração da tributação IPI",
                                    status=RpaHistoricoStatusEnum.Falha,
                                    tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                                )
            except Exception as e:
                retorno = f"Erro ao trabalhar nas alterações dos itens, erro: {e} \nEtapas Executadas:\n{steps}"
                return RpaRetornoProcessoDTO(
                    sucesso=False,
                    retorno=retorno,
                    status=RpaHistoricoStatusEnum.Falha,
                    tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                )

            await worker_sleep(5)
            console.print("Navegando pela Janela de Nota Fiscal de Entrada - Acessando a Janela de Pagamento...\n")
            app = Application().connect(class_name="TFrmNotaFiscalEntrada")
            main_window = app["TFrmNotaFiscalEntrada"]

            main_window.set_focus()
            console.log("Seleciona Pagamento", style="bold yellow")
            try:
                pyautogui.click(623, 374)
                await worker_sleep(1)
                send_keys("{DOWN " + ("4") + "}")
            except Exception as e:
                panel_TPage = main_window.child_window(class_name="TPage", title="Formulario")
                panel_TTabSheet = panel_TPage.child_window(class_name="TcxCustomInnerTreeView")
                panel_TTabSheet.wait("visible")
                panel_TTabSheet.click()
                send_keys("{DOWN " + ("2") + "}")

            
            if nota.get("cliente_fidc").lower() == 'não':
                try:
                    panel_TPage = main_window.child_window(class_name="TPage", title="Formulario")
                    panel_TTabSheet = panel_TPage.child_window(class_name="TPageControl")
                    panel_TabPagamento = panel_TTabSheet.child_window(class_name="TTabSheet")
                    panel_TabPagamentoCaixa = panel_TTabSheet.child_window(title="Pagamento Pelo Caixa")
                    tipo_cobranca = panel_TabPagamentoCaixa.child_window(class_name="TDBIComboBox", found_index=0)

                    console.print(f"Selecionando a Especie de Caixa... \n")
                    tipo_cobranca.click()
                    await worker_sleep(1)
                    set_combobox("||List", "13 - DEVOLUCAO DE VENDA")

                    await worker_sleep(2)

                    console.print(f"Capturando o valor em Valores Restante... \n")
                    tab_valores = panel_TabPagamento.child_window(title="Valores")
                    valores_restantes = tab_valores.child_window(
                        class_name="TDBIEditNumber", found_index=1
                    )
                    valores_restantes_text = valores_restantes.window_text()
                    valor_nota_fiscal = valores_restantes_text
                    console.print(f"Valor capturado {valores_restantes_text}, inserindo no campo Valor em Pagamento pelo Caixa... \n")

                    valor = panel_TabPagamentoCaixa.child_window(class_name="TDBIEditNumber", found_index=0)
                    valor.set_edit_text(valores_restantes_text)
                except Exception as e:
                    retorno = f"Não foi possivel realizar as atividades na aba de 'Pagamento', erro: {e} \nEtapas Executadas:\n{steps}"
                    return RpaRetornoProcessoDTO(
                        sucesso=False,
                        retorno=retorno,
                        status=RpaHistoricoStatusEnum.Falha,
                        tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                    )
            else:
                try:
                    panel_TPage = main_window.child_window(class_name="TPage", title="Formulario")
                    panel_TTabSheet = panel_TPage.child_window(class_name="TPageControl")
                    panel_TabPagamento = panel_TTabSheet.child_window(class_name="TTabSheet")
                    panel_TabParcelamento = panel_TTabSheet.child_window(title="Parcelamento")
                    tipo_cobranca = panel_TabParcelamento.child_window(class_name="TDBIComboBox", found_index=0)

                    console.print("Verificando o tipo de cobrança selecionado... \n")
                    tipo_selecionado = tipo_cobranca.window_text()
                    if "boleto" in tipo_selecionado.lower():
                        console.print(f"Tipo de cobrança corretamente selecionado {tipo_selecionado}... \n")
                    else:
                        console.print(f"Tipo de cobrança não foi selecionado corretamente, interagindo com o campo para selecionar o campo corretamente... \n")
                        tipo_cobranca.click()
                        await worker_sleep(1)
                        set_combobox("||List", "BANCO DO BRASIL BOLETO")
                        

                    tab_valores = panel_TabPagamento.child_window(title="Valores")
                    valores_restantes = tab_valores.child_window(class_name="TDBIEditNumber", found_index=1)
                    valores_informado = tab_valores.child_window(class_name="TDBIEditNumber", found_index=2)

                    vencimento = panel_TabParcelamento.child_window(class_name="TDBIEditDate")
                    data_hoje_obj = datetime.strptime(data_hoje, '%d/%m/%Y')
                    nova_data = data_hoje_obj + timedelta(days=5)
                    data_vencimento = nova_data.strftime('%d/%m/%Y')
                    console.print(f'Data de Vencimento a ser inserida: {data_vencimento}')
                    vencimento.set_edit_text(data_vencimento)

                    await worker_sleep(2)
                    console.print(f"Inserindo o valor {valores_restantes_text}... \n")
                    valor = panel_TabParcelamento.child_window(class_name="TDBIEditNumber", found_index=3)
                    valor.set_edit_text(valores_restantes_text)

                    await worker_sleep(2)
                    console.print(f"Adicionando o pagamento... \n")
                    btn_add = panel_TabParcelamento.child_window(class_name="TDBIBitBtn", found_index=1)
                    btn_add.click()

                    await worker_sleep(4)
                    console.print(f"Verificando se o pagamento foi adicionado com sucesso... \n")
                    valores_informado = tab_valores.child_window(class_name="TDBIEditNumber", found_index=2)
                    valores_informado_text = valores_informado.window_text()
                    if '0,00' in valores_informado_text and len(valores_informado_text) == 3:
                        return RpaRetornoProcessoDTO(
                            sucesso=False,
                            retorno=f"Erro ao adicionar o pagamento, valor informado {valores_informado_text}.",
                            status=RpaHistoricoStatusEnum.Falha,
                            tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                        )
                    console.print(f"Processo de incluir pagamento realizado com sucesso... \n")

                except Exception as e:
                    retorno = f"Erro ao processar tela 'Pagamento', erro: {e} \nEtapas Executadas:\n{steps}"
                    return RpaRetornoProcessoDTO(
                        sucesso=False,
                        retorno=retorno,
                        status=RpaHistoricoStatusEnum.Falha,
                        tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                    )

            # Inclui registro
            console.print(f"Incluindo registro...\n")
            try:
                ASSETS_PATH = "assets"
                inserir_registro = pyautogui.locateOnScreen(ASSETS_PATH + "\\entrada_notas\\IncluirRegistro.png", confidence=0.8)
                pyautogui.click(inserir_registro)
            except Exception as e:
                console.print(
                    f"Não foi possivel incluir o registro utilizando reconhecimento de imagem, Error: {e}...\n tentando inserir via posição...\n"
                )
                await incluir_registro()
                

                await worker_sleep(5)
                console.print("Verificando a existencia de POP-UP de Itens que Ultrapassam a Variação Máxima de Custo ...\n")
                itens_variacao_maxima = await is_window_open_by_class("TFrmTelaSelecao", "TFrmTelaSelecao")
                if itens_variacao_maxima["IsOpened"] == True:
                    app = Application().connect(class_name="TFrmTelaSelecao")
                    main_window = app["TFrmTelaSelecao"]
                    send_keys("%o")
                

                #VERIFICANDO SE A NOTA FOI INCLUIDA COM SUCESSO
                console.print("Verificando a se a Nota foi incluida com sucesso... \n")
                try:
                    app = Application().connect(title="Information", timeout=180)
                    main_window = app["Information"]
                    main_window.set_focus()

                    #EXTRAINDO O NUMERO DA NOTA 
                    window_rect = main_window.rectangle()
                    screenshot = pyautogui.screenshot(
                        region=(
                            window_rect.left,
                            window_rect.top,
                            window_rect.width(),
                            window_rect.height(),
                        )
                    )
                    username = getpass.getuser()
                    short_uuid = str(uuid.uuid4()).replace('-', '')[:6]
                    path_to_png = f"C:\\Users\\{username}\\Downloads\\aviso_popup_{short_uuid}.png"
                    screenshot.save(path_to_png)
                    console.print(f"Print salvo em {path_to_png}...\n")

                    console.print(
                        f"Preparando a imagem para maior resolução e assertividade no OCR...\n"
                    )
                    image = Image.open(path_to_png)
                    image = image.convert("L")
                    enhancer = ImageEnhance.Contrast(image)
                    image = enhancer.enhance(2.0)
                    image.save(path_to_png)
                    console.print(f"Imagem preparada com sucesso...\n")
                    console.print(f"Realizando OCR...\n")
                    captured_text = pytesseract.image_to_string(Image.open(path_to_png))
                    console.print(f"Texto Full capturado {captured_text}...\n")
                    os.remove(path_to_png)
                    pattern = r"sequ[êe]ncia:\s*(\d+)"
                    match = re.search(pattern, captured_text)

                    if match:
                        numero_nota_fiscal = match.group(1)


                    app = Application().connect(title="Information", timeout=180)
                    main_window = app["Information"]
                    main_window.set_focus()
                    btn_ok = main_window.child_window(class_name="TButton", found_index=0)
                    btn_ok.click()
                    await worker_sleep(3)
                    steps += 'ETAPA 02 - Nota fiscal de Entrada Incluida com sucesso'
                except Exception as e:
                    retorno = f"Não foi possivel obter a confirmação de Nota fiscal incluida com sucesso \nEtapas Executadas:\n{steps}"
                    return RpaRetornoProcessoDTO(
                        sucesso=False,
                        retorno=retorno,
                        status=RpaHistoricoStatusEnum.Falha,
                        tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                    )
        else:
            retorno = f"Não foi possivel obter a confirmação de Nota fiscal incluida com sucesso \nEtapas Executadas:\n{steps}"
            return RpaRetornoProcessoDTO(
                sucesso=False,
                retorno=f"Não foi possivel abrir a tela de Pesquisar Venda para Devolução, erro: {e}",
                status=RpaHistoricoStatusEnum.Falha,
                tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
            )

        app = Application().connect(class_name="TFrmNotaFiscalEntrada")
        main_window = app["TFrmNotaFiscalEntrada"]
        main_window.close()

        #STEP 3 
        type_text_into_field("Gerenciador de Notas Fiscais", app["TFrmMenuPrincipal"]["Edit"], True, "50")
        pyautogui.press("enter")
        await worker_sleep(2)
        pyautogui.press("enter")
        console.print(f"\nPesquisa: 'Gerenciador de Notas Fiscais' realizada com sucesso",style="bold green")
        pesquisar_venda_devolucao = await is_window_open_by_class("TFrmGerenciadorNFe2", "TFrmGerenciadorNFe2")
        if pesquisar_venda_devolucao["IsOpened"] == True:
            selecionar_itens_gerenciador_nfe = await gerenciador_nf_header(data_hoje, cod_cliente_incorreto)
            if selecionar_itens_gerenciador_nfe.sucesso:
                console.print("PROCESSO EXECUTADO COM SUCESSO, SEGUINDO COM O PROCESSO PARA TRANSMITIR A NF-E...\n")
                app = Application().connect(class_name="TFrmGerenciadorNFe2", timeout=60)
                main_window = app["TFrmGerenciadorNFe2"]
                main_window.set_focus()

                tpanel_footer = main_window.child_window(class_name="TPanel", found_index=1)
                btn_transmitir = tpanel_footer.child_window(class_name="TBitBtn", found_index=5)
                btn_transmitir.click()
                await worker_sleep(3)

                max_attempts = 10
                i = 0
                
                while i < max_attempts:
                    try:
                        app = Application().connect(class_name="TFrmProcessamentoFEe2", timeout=10)
                        main_window = app["TFrmProcessamentoFEe2"]

                        await worker_sleep(5)
                        information_pop_up = await is_window_open_by_class("TMessageForm", "TMessageForm")
                        if information_pop_up["IsOpened"] == True:
                            msg_pop_up = await ocr_by_class(numero_nota_fiscal, "TMessageForm", "TMessageForm")
                            if msg_pop_up.sucesso:
                                if 'operação concl' in msg_pop_up or 'operacao concl' in msg_pop_up:
                                    information_operacao_concluida = main_window.child_window(class_name="TMessageForm")
                                    btn_ok = information_operacao_concluida.child_window(class_name="TButton")
                                    btn_ok.click()
                                    await worker_sleep(4)
                                    main_window.close()
                                    break
                                else:
                                    retorno = f"Pop up nao mapeado para seguimento do robo {msg_pop_up} \nEtapas Executadas:\n{steps}"
                                    return RpaRetornoProcessoDTO(
                                        sucesso=False,
                                        retorno=retorno,
                                        status=RpaHistoricoStatusEnum.Falha,
                                        tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                                    )
                            else:
                                retorno = f"Não foi possivel realizar a confirmação do msg do OCR \nEtapas Executadas:\n{steps}"
                                return RpaRetornoProcessoDTO(
                                    sucesso=False,
                                    retorno=retorno,
                                    status=RpaHistoricoStatusEnum.Falha,
                                    tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                                )
                    except Exception as e:
                        pass


                    i += 1
                    await worker_sleep(10)
                

                if i == max_attempts:
                    console.print("Número máximo de tentativas atingido. Encerrando...")
                    retorno = f"Tempo esgotado e numero de tentativas atingido, não foi possivel obter o retorno de conclusão para transmissão na tela de Gerenciador NF-e \nEtapas Executadas:\n{steps}"
                    return RpaRetornoProcessoDTO(
                        sucesso=False,
                        retorno=retorno,
                        status=RpaHistoricoStatusEnum.Falha,
                        tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                    )
                

                #PROCESSO DE IMPRESSÃO 
                app = Application().connect(class_name="TFrmGerenciadorNFe2", timeout=60)
                main_window = app["TFrmGerenciadorNFe2"]
                main_window.set_focus()
                tpanel_footer = main_window.child_window(class_name="TPanel", found_index=1)
                btn_imprimir_danfe = tpanel_footer.child_window(class_name="TBitBtn", found_index=0)
                btn_imprimir_danfe.click()
                await worker_sleep(5)

                app = Application().connect(class_name="TFrmConfigurarTemplateDANF2", timeout=60)
                main_window = app["TFrmGerenciadorNFe2"]
                main_window.set_focus()
                btn_selecionar_pdf = main_window.child_window(class_name="TRadioButton", found_index=1)
                btn_selecionar_pdf.click()
                await worker_sleep(2)

                btn_gerar = main_window.child_window(class_name="TBitBtn", found_index=1)
                btn_gerar.click()
                await worker_sleep(2)
                steps += 'ETAPA 03 - PROCESSO DE TRANSMITIR NF-e EXECUTADO COM SUCESSO '


                app = Application().connect(title="Salvar par arquivo")
                main_window = app["Salvar"]
                console.print("Tela 'Salvar' encontrada!")

                console.print("Interagindo com a tela 'Salvar'...\n")
                username = getpass.getuser()
                path_to_txt = f"C:\\Users\\{username}\\Downloads\\DEVOLUÇÃO PRAZO A FATURAR {numero_cupom_fiscal}"

                main_window.type_keys("%n")
                pyautogui.write(path_to_txt)
                await worker_sleep(1)
                main_window.type_keys("%l")
                console.print("Arquivo salvo com sucesso...\n")
                await worker_sleep(6)

                with open(path_to_txt, 'rb') as file:
                    file_bytes = io.BytesIO(file.read())

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                desArquivo = f"DEVOLUÇÃO PRAZO A FATURAR {numero_cupom_fiscal}.pdf"
                try:
                    await send_file(historico_id, desArquivo, "pdf", file_bytes, file_extension="pdf")
                    os.remove(path_to_txt)
                except Exception as e:
                    result = f"Arquivo DEVOLUÇÃO PRAZO A FATURAR gerado com sucesso, porém gerou erro ao realizar o envio para o backoffice {e} - Arquivo ainda salvo na dispositivo utilizado no diretório {path_to_txt}! \nEtapas Executadas:\n{steps}"
                    console.print(result, style="bold red")
                    return RpaRetornoProcessoDTO(
                        sucesso=False,
                        retorno=result,
                        status=RpaHistoricoStatusEnum.Falha,
                        tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                    )

                app = Application().connect(class_name="TFrmConfigurarTemplateDANF2", timeout=60)
                main_window = app["TFrmGerenciadorNFe2"]
                main_window.close()

                app = Application().connect(class_name="TFrmGerenciadorNFe2", timeout=60)
                main_window = app["TFrmGerenciadorNFe2"]
                main_window.close()


            else:
                retorno = f"{selecionar_itens_gerenciador_nfe} \nEtapas Executadas:\n{steps}"
                return RpaRetornoProcessoDTO(
                    sucesso=False,
                    retorno=retorno,
                    status=RpaHistoricoStatusEnum.Falha, 
                    tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                )
        else:
            retorno = f"Não foi possivel abrir a tela de Gerenciador de Notas Fiscais \nEtapas Executadas:\n{steps}"
            return RpaRetornoProcessoDTO(
                sucesso=False,
                retorno=retorno,
                status=RpaHistoricoStatusEnum.Falha, 
                tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
            )


        #STEP 4 
        #PRE VENDA
        type_text_into_field("Cadastro Pré venda", app["TFrmMenuPrincipal"]["Edit"], True, "50")
        pyautogui.press("enter")
        await worker_sleep(2)
        pyautogui.press("enter")
        console.print(f"\nPesquisa: 'Cadastro Pré venda' realizada com sucesso",style="bold green")
        cadastro_pre_venda = await is_window_open_by_class("TFrmPreVenda", "TFrmPreVenda")
        if cadastro_pre_venda["IsOpened"] == True:
            preenchimento_header_pre_venda = await cadastro_pre_venda_header("5656 - VENDA DE COMB OU LUB ADQ DE TERCEIRO C/ FIN S/ ESTOQUE", cod_cliente_correto, "21 DIAS")
            if preenchimento_header_pre_venda.sucesso:
                try:
                    cidade_cliente = preenchimento_header_pre_venda.retorno
                    console.print(f"\nPreenchimento cabeçalho da pre venda preenchido com sucesso, seguindo com o processo.. ",style="bold green")
                    app = Application().connect(class_name="TFrmPreVenda", timeout=60)
                    main_window = app["TFrmPreVenda"]
                    main_window.set_focus()
                    
                    console.print("Navegando nos elementos...\n")
                    panel_TPage= main_window.child_window(class_name="TPage", found_index=0)
                    panel_menu_itens= main_window.child_window(class_name="TcxCustomInnerTreeView", found_index=0)

                    console.print("Acessando a janela de Itens...\n")
                    panel_menu_itens.click()
                    await worker_sleep(1)
                    send_keys("^({HOME})")
                    await worker_sleep(1)
                    pyautogui.press('down')
                    console.print(nota.get('itens'))

                    for item in nota.get('itens'):
                        quantidade = item['novaQuantidade']
                        preco = item['novoPreco']
                        descricao = item['descricao']

                        if 'arla' in descricao.lower():
                            item_arla = True

                        app = Application().connect(class_name="TFrmPreVenda", timeout=60)
                        main_window = app["TFrmPreVenda"]
                        main_window.set_focus()
                        
                        console.print("Itens acessado com sucesso, clicando em Incluir...\n")
                        panel_TGroup_Box= panel_TPage.child_window(class_name="TGroupBox", found_index=0)
                        btn_incluir = panel_TGroup_Box.child_window(class_name="TDBIBitBtn", found_index=4)
                        btn_incluir.click()
                        await worker_sleep(2)
                        console.print("Incluir clicado com sucesso...\n")

                        #VERIFICANDO A EXISTENCIA DE WARNINGS 
                        console.print("Verificando a existência de Warning... \n")
                        warning_pop_up = await is_window_open("Warning")
                        if warning_pop_up["IsOpened"] == True:
                            console.print("possui Pop-up de Warning, analisando... \n")
                            ocr_pop_warning = await ocr_warnings(numero_cupom_fiscal)
                            if ocr_pop_warning.sucesso == True:
                                return RpaRetornoProcessoDTO(
                                    sucesso=False,
                                    retorno=f"POP UP Warning não mapeado para seguimento do processo, mensagem: {ocr_pop_warning.retorno}",
                                    status=RpaHistoricoStatusEnum.Falha,
                                    tags=[RpaTagDTO(descricao=RpaTagEnum.Negocio)]
                                )
                            else:
                                return RpaRetornoProcessoDTO(
                                    sucesso=False,
                                    retorno=f"POP UP Warning não mapeado para seguimento do processo",
                                    status=RpaHistoricoStatusEnum.Falha,
                                    tags=[RpaTagDTO(descricao=RpaTagEnum.Negocio)]
                                )


                        console.print("Clicando sobre a lupa para inserir o almoxarifado...\n")
                        app = Application().connect(class_name="TFrmIncluiItemPreVenda", timeout=60)
                        main_window = app["TFrmIncluiItemPreVenda"]
                        main_window.set_focus()
                        panel_TGroup_Box= panel_TPage.child_window(class_name="TPanel", found_index=2)
                        lupa_almoxarifaco = panel_TPage.child_window(class_name="TDBIBitBtn", found_index=1)
                        lupa_almoxarifaco.click()
                        console.print("Lupa clicado com sucesso inserindo a descrição do almoxarifado...\n")

                        app = Application().connect(class_name="TfrmDialogBuscaGeral", timeout=60)
                        main_window = app["TfrmDialogBuscaGeral"]
                        main_window.set_focus()

                        field_descricao_almoxarifado = main_window.child_window(class_name="TEdit", found_index=0)
                        field_descricao_almoxarifado.set_edit_text(descricao)
                        await worker_sleep(2)

                        btn_lupa_pesquisar = main_window.child_window(class_name="TBitBtn", found_index=0)
                        btn_lupa_pesquisar.click()
                        await worker_sleep(2)

                        main_window.set_focus()
                        send_keys("%o")
                        console.print("Processo finalizado com sucesso, seguindo com a seleção da natureza...\n")

                        app = Application().connect(class_name="TFrmIncluiItemPreVenda", timeout=60)
                        main_window = app["TFrmIncluiItemPreVenda"]
                        main_window.set_focus()
                        panel_TGroup_Box= panel_TPage.child_window(class_name="TPanel", found_index=2)
                        natureza_oper_select = panel_TPage.child_window(class_name="TDBIComboBox", found_index=0)
                        natureza_oper_select.click()
                        await worker_sleep(1)
                        set_combobox("||List", "5656 - VENDA DE COMB OU LUB ADQ DE TERCEIRO C/ FIN S/ ESTOQUE")
                        await worker_sleep(1)
                        console.print("Natureza da operação selecionado com sucesso, preenchendo os itens...\n")

                        #INSERINDO A QUANTIDADE
                        main_window.set_focus()
                        panel_TPage_Control= main_window.child_window(class_name="TcxPageControl", found_index=0)
                        panel_tabSheet = panel_TPage_Control.child_window(class_name="TcxTabSheet", found_index=0)

                        field_quantidade = panel_tabSheet.child_window(class_name="TDBIEditNumber", found_index=9)
                        console.print("Inserindo a quantidade de Itens...\n")
                        field_quantidade.set_edit_text(quantidade)
                        await worker_sleep(1)

                        #INSERINDO O VALOR INDIVIDUAL DO ITEM
                        console.print("Inserindo o valor indivual do Item...\n")
                        btn_valor_unitario = panel_tabSheet.child_window(class_name="TDBIBitBtn", found_index=0)
                        btn_valor_unitario.click()
                        await worker_sleep(2)

                        app = Application().connect(class_name="TFrmInputBoxNumero", timeout=60)
                        main_window = app["TFrmInputBoxNumero"]
                        main_window.set_focus()

                        field_valor = main_window.child_window(class_name="TDBIEditNumber", found_index=0)
                        field_valor.set_edit_text(preco)
                        await worker_sleep(2)

                        main_window.set_focus()
                        send_keys("%o")

                        app = Application().connect(class_name="TFrmIncluiItemPreVenda", timeout=60)
                        main_window = app["TFrmIncluiItemPreVenda"]
                        main_window.set_focus()
                        send_keys("%i")
                        await worker_sleep(2)
                        main_window.close()


                    # Inclui registro
                    console.print(f"Incluindo registro...\n")
                    try:
                        ASSETS_PATH = "assets"
                        inserir_registro = pyautogui.locateOnScreen(ASSETS_PATH + "\\entrada_notas\\IncluirRegistro.png", confidence=0.8)
                        pyautogui.click(inserir_registro)
                    except Exception as e:
                        console.print(
                            f"Não foi possivel incluir o registro utilizando reconhecimento de imagem, Error: {e}...\n tentando inserir via posição...\n"
                        )
                        await incluir_registro()

                    
                    #VERIFICANDO A EXISTENCIA DE WARNINGS 
                    console.print("Verificando a existência de Warning... \n")
                    warning_pop_up = await is_window_open("Warning")
                    if warning_pop_up["IsOpened"] == True:
                        console.print("possui Pop-up de Warning, analisando... \n")
                        ocr_pop_warning = await ocr_warnings(numero_cupom_fiscal)
                        if ocr_pop_warning.sucesso == True:
                            retorno = f"POP UP Warning não mapeado para seguimento do processo, mensagem: {ocr_pop_warning.retorno} \nEtapas Executadas:\n{steps}"
                            return RpaRetornoProcessoDTO(
                                sucesso=False,
                                retorno=retorno,
                                status=RpaHistoricoStatusEnum.Falha,
                                tags=[RpaTagDTO(descricao=RpaTagEnum.Negocio)]
                            )
                        else:
                            retorno = f"POP UP Warning não mapeado para seguimento do processo \nEtapas Executadas:\n{steps}"
                            return RpaRetornoProcessoDTO(
                                sucesso=False,
                                retorno=retorno,
                                status=RpaHistoricoStatusEnum.Falha,
                                tags=[RpaTagDTO(descricao=RpaTagEnum.Negocio)]
                            )
                    
                    steps += 'ETAPA 04 - PRE VENDA INCLUIDA COM SUCESSO'
                    #VERIFICANDO SE A PRÉ VENDA FOI INCLUIDA COM SUCESSO
                    app = Application().connect(class_name="TFrmIncluiItemPreVenda", timeout=60)
                    main_window = app["Informação"]
                    main_window.set_focus()

                    btn_ok = main_window.child_window(class_name="Button")
                    btn_ok.click()

                    #CONFIRMANDO POP UP DE PRÉ VENDA
                    app = Application().connect(class_name="TFrmIncluiItemPreVenda", timeout=60)
                    main_window = app["Confirm"]
                    main_window.set_focus()

                    btn_yes = main_window.child_window(class_name="TButton", found_index=1)
                    btn_yes.click()

                    #CONFIRMANDO NA TELA DE PRE VENDA
                    app = Application().connect(class_name="TFrmIncluiItemPreVenda", timeout=60)
                    main_window = app["TFrmIncluiItemPreVenda"]
                    main_window.set_focus()

                    panel_Tnotebook = main_window.child_window(class_name="TNotebook", found_index=0)
                    panel_Tnotebook = panel_Tnotebook.child_window(class_name="TPage", found_index=0)
                    btn_confirmar = panel_Tnotebook.child_window(class_name="TBitBtn", found_index=11)
                    btn_confirmar.click()
                    await worker_sleep(3)

                    app = Application().connect(class_name="TFrmIncluiItemPreVenda", timeout=60)
                    main_window = app["Confirm"]
                    main_window.set_focus()

                    btn_yes = main_window.child_window(class_name="TButton", found_index=1)
                    btn_yes.click()
                    await worker_sleep(3)

                    app = Application().connect(class_name="TFrmIncluiItemPreVenda", timeout=60)
                    main_window = app["Warning"]
                    main_window.set_focus()

                    btn_ok = main_window.child_window(class_name="TButton", found_index=0)
                    btn_ok.click()
                    await worker_sleep(3)


                    app = Application().connect(class_name="TFrmIncluiItemPreVenda", timeout=60)
                    main_window = app["Confirm"]
                    main_window.set_focus()

                    btn_yes = main_window.child_window(class_name="TButton", found_index=1)
                    btn_yes.click()
                    await worker_sleep(3)

                    #APROVAR CREDITO
                    app = Application().connect(class_name="TFrmIncluiItemPreVenda", timeout=60)
                    main_window = app["TFrmIncluiItemPreVenda"]
                    main_window.set_focus()

                    panel_Tnotebook = main_window.child_window(class_name="TNotebook", found_index=0)
                    panel_Tnotebook = panel_Tnotebook.child_window(class_name="TPage", found_index=0)
                    btn_aprovar_credito = panel_Tnotebook.child_window(class_name="TBitBtn", found_index=8)
                    btn_aprovar_credito.click()
                    await worker_sleep(2)


                    app = Application().connect(class_name="TFrmIncluiItemPreVenda", timeout=60)
                    main_window = app["Confirm"]
                    main_window.set_focus()

                    btn_yes = main_window.child_window(class_name="TButton", found_index=1)
                    btn_yes.click()
                    await worker_sleep(3)

                    app = Application().connect(class_name="TFrmIncluiItemPreVenda", timeout=60)
                    main_window = app["Informação"]
                    main_window.set_focus()

                    btn_ok = main_window.child_window(class_name="Button")
                    btn_ok.click()


                    #FATURAR
                    app = Application().connect(class_name="TFrmIncluiItemPreVenda", timeout=60)
                    main_window = app["TFrmIncluiItemPreVenda"]
                    main_window.set_focus()

                    panel_Tnotebook = main_window.child_window(class_name="TNotebook", found_index=0)
                    panel_Tnotebook = panel_Tnotebook.child_window(class_name="TPage", found_index=0)
                    btn_faturar = panel_Tnotebook.child_window(class_name="TBitBtn", found_index=1)
                    btn_faturar.click()
                    await worker_sleep(2)

                    app = Application().connect(class_name="TFrmIncluiItemPreVenda", timeout=60)
                    main_window = app["Confirm"]
                    main_window.set_focus()

                    btn_no = main_window.child_window(class_name="TButton", found_index=0)
                    btn_no.click()
                    await worker_sleep(3)

                    app = Application().connect(title="Parcelas - Nota Fiscal Saída", timeout=60)
                    main_window = app.window(title="Parcelas - Nota Fiscal Saída")
                    main_window.set_focus()
                    send_keys("%n")
                    await worker_sleep(3)

                    information_pop_up = await is_window_open("Information")
                    if information_pop_up["IsOpened"] == True:
                        app = Application().connect(title="Information", timeout=180)
                        main_window = app["Information"]
                        main_window.set_focus()
                        btn_ok = main_window.child_window(class_name="TButton", found_index=0)
                        btn_ok.click()

                    await worker_sleep(30)

                    #FATURAMENTO PRÉ-VENDA
                    app = Application().connect(class_name="TFrmDadosFaturamentoPreVenda", timeout=60)
                    main_window = app["TFrmDadosFaturamentoPreVenda"]
                    main_window.set_focus()

                    #VERIFICANDO SE POSSUI POP UP WARNING
                    warning_boo = False
                    try:
                        app = Application().connect(class_name="TFrmDadosFaturamentoPreVenda", timeout=60)
                        main_window = app["Warning"]
                        main_window.set_focus()
                        btn_ok = main_window.child_window(class_name="TButton", found_index=0)
                        btn_ok.click()
                        await worker_sleep(3)
                        warning_boo = True
                    except:
                        pass

                    #ALTERANDO TRIBUTO DOS ITENS 
                    if warning_boo:
                        console.print('Acessando a tela de Itens')
                        app = Application().connect(class_name="TFrmDadosFaturamentoPreVenda", timeout=60)
                        main_window = app["TFrmDadosFaturamentoPreVenda"]
                        main_window.set_focus()
                        send_keys("%i")
                        await worker_sleep(2)
                        send_keys("%g")
                        await worker_sleep(2)

                        app = Application().connect(class_name="TFrmDadosTributacaoProdutoPreVenda", timeout=60)
                        main_window = app["TFrmDadosTributacaoProdutoPreVenda"]

                        tpanel_dados_tributacao = main_window.child_window(class_name="TPanel", found_index=1)
                        tributacao_icms_select = tpanel_dados_tributacao.child_window(class_name="TDBIComboBox", found_index=3)


                        if not item_arla:
                            tributacao_icms_select.click()
                            await worker_sleep(1)
                            set_combobox("||List", "061 - 061- MONOFASICO")
                        else:
                            aliquota = None
                            for item in conconfig_aliquota_icms:
                                if cidade_cliente in item["estado"]:
                                    aliquota = item["aliquota"]
                                    break

                            if aliquota:
                                console.print(f"A alíquota para o estado {cidade_cliente} é: {aliquota}")
                                tributacao_icms_select.click()
                                await worker_sleep(1)
                                tributacao = f"000 - 000- ICMS - {aliquota}%"
                                set_combobox("||List", tributacao)
                            else:
                                retorno = f"Estado {cidade_cliente} não encontrado \nEtapas Executadas:\n{steps}"
                                return RpaRetornoProcessoDTO(
                                    sucesso=False,
                                    retorno=retorno,
                                    status=RpaHistoricoStatusEnum.Falha,
                                    tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                                )

                        send_keys("%o")


                    app = Application().connect(class_name="TFrmDadosFaturamentoPreVenda", timeout=60)
                    main_window = app["TFrmDadosFaturamentoPreVenda"]
                    main_window.set_focus()
                    send_keys("%m")
                    await worker_sleep(2)
                    pyautogui.hotkey('shift', 'left')

                    panel_tab_sheet = main_window.child_window(class_name="TcxTabSheet", found_index=0)
                    field_observacao = panel_tab_sheet.child_window(class_name="TDBIMemo")
                    text_campo_observacao = f"Nome do Motorista: {nota.get("nomeMotorista")} - Placa: {nota.get("placaClienteCorreto")} - Quilometragem do Veículo: {nota.get("quilometragemVeiculo")}"
                    field_observacao.set_edit_text(text_campo_observacao)
                    send_keys("%o")
                    await worker_sleep(2)

                    app = Application().connect(class_name="TFrmDadosFaturamentoPreVenda", timeout=60)
                    main_window = app["Confirm"]
                    main_window.set_focus()

                    btn_yes = main_window.child_window(class_name="TButton", found_index=1)
                    btn_yes.click()
                    await worker_sleep(5)

                    app = Application().connect(class_name="TFrmDadosFaturamentoPreVenda", timeout=60)
                    main_window = app["TMessageForm"]
                    main_window.set_focus()
                    send_keys("%i")
                    await worker_sleep(15)

                    app = Application().connect(class_name="TFrmAguarde", timeout=60)
                    main_window = app["TppPrintDialog"]
                    tpanel_btn_ok = main_window.child_window(class_name="TPanel", found_index=1)
                    btn_ok_print_screen = tpanel_btn_ok.child_window(class_name="TButton", found_index=1)
                    btn_ok_print_screen.click()

                    #NAVEGANDO NA TELA DE SALVAR RELATORIO
                    tpanel_main_window = main_window.child_window(class_name="HWNDView", found_index=0)
                    tpanel_element = tpanel_main_window.child_window(class_name="Element", found_index=0)
                    tpanel_background = tpanel_element.child_window(class_name="PreviewBackground", found_index=0)
                    field_diretorio_path = tpanel_background.child_window(class_name="AppControlHost", found_index=0)

                    username = getpass.getuser()
                    path_to_txt = f"C:\\Users\\{username}\\Downloads\\NOVA VENDA {numero_cupom_fiscal}"
                    field_diretorio_path.set_edit_text(path_to_txt)

                    main_window.set_focus()
                    send_keys("%l")
                    await worker_sleep(5)

                    with open(path_to_txt, 'rb') as file:
                        file_bytes = io.BytesIO(file.read())

                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    desArquivo = f"NOVA VENDA {numero_cupom_fiscal}.pdf"
                    try:
                        await send_file(historico_id, desArquivo, "pdf", file_bytes, file_extension="pdf")
                        os.remove(path_to_txt)
                    except Exception as e:
                        result = f"Arquivo NOVA VENDA gerado com sucesso, porém gerou erro ao realizar o envio para o backoffice {e} - Arquivo ainda salvo na dispositivo utilizado no diretório {path_to_txt} !"
                        console.print(result, style="bold red")
                        return RpaRetornoProcessoDTO(
                            sucesso=False,
                            retorno=result,
                            status=RpaHistoricoStatusEnum.Falha,
                            tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                        )


                    app = Application().connect(class_name="TFrmProcessamentoFEe2", timeout=60)
                    main_window = app["TFrmProcessamentoFEe2"]
                    main_window.close()
                    await worker_sleep(2)

                    app = Application().connect(class_name="TFrmGerenciadorNFe2", timeout=60)
                    main_window = app["Confirm"]
                    main_window.set_focus()
                    send_keys("%n")


                    #GERAR RELATORIO FINAL 
                    type_text_into_field("Rel. Boletim Caixa", app["TFrmMenuPrincipal"]["Edit"], True, "50")
                    pyautogui.press("enter")
                    await worker_sleep(2)
                    pyautogui.press("enter")
                    await worker_sleep(5)


                    app = Application().connect(class_name="TFrmRelBoletimCaixa", timeout=60)
                    main_window = app["TGroupBox"]
                    
                    dt_inicio = main_window.child_window(class_name="TDBIEditDate", found_index=0)
                    dt_inicio.set_edit_text(data_hoje)
                    dt_final = main_window.child_window(class_name="TDBIEditDate", found_index=1)
                    dt_final.set_edit_text(data_hoje)

                    #SELECIONANDO A ESPECIE
                    select_especie = main_window.child_window(class_name="TDBIComboBox", found_index=0)
                    select_especie.click()
                    set_combobox("||List", "13 - DEVOLUCAO DE VENDA")
                    send_keys("%g")

                    #CLICANDO NO ICONE DE IMPRIMIR 
                    await worker_sleep(2)
                    screen_width, screen_height = pyautogui.size()
                    x = 10
                    y = screen_height - 280 - (96 * 2) / .254
                    pyautogui.click(x,y)

                    #INSERINDO O DIRETORIO E SALVANDO O ARQUIVO
                    app = Application().connect(title="Salvar Saída de Impressão como")
                    main_window = app["Dialog"]
                    console.print("Tela 'Salvar' encontrada!")

                    console.print("Interagindo com a tela 'Salvar'...\n")
                    username = getpass.getuser()
                    path_to_txt = f"C:\\Users\\{username}\\Downloads\\CAIXA 13 DEVOLUÇÃO {numero_cupom_fiscal}"

                    main_window.type_keys("%n")
                    pyautogui.write(path_to_txt)
                    await worker_sleep(1)
                    main_window.type_keys("%l")
                    console.print("Arquivo salvo com sucesso...\n")
                    await worker_sleep(5)
                    
                    txt = ""
                    with open(f"{path_to_txt}.pdf", "rb") as f:
                        reader = PdfReader(f)
                        txt = ""
                        for p in reader.pages:
                            txt += p.extract_text()

                    ultimo_valor = txt[-1]
                    penultimo_valor = txt[-2]

                    if ultimo_valor == penultimo_valor:
                        console.print("Valores no relatorio corretamente gerados...\n")
                        with open(path_to_txt, 'rb') as file:
                            file_bytes = io.BytesIO(file.read())

                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        desArquivo = f"CAIXA 13 DEVOLUÇÃO {numero_cupom_fiscal}.pdf"
                        try:
                            await send_file(historico_id, desArquivo, "pdf", file_bytes, file_extension="pdf")
                            os.remove(path_to_txt)
                            retorno = f"Processo de devolução executado com sucesso \nEtapas Executadas:\n{steps}"

                            try:
                                url_retorno = nota.get("urlRetorno")
                                identificador = nota.get("identificador")

                                if url_retorno and identificador:
                                    await post_partner(url_retorno, identificador, numero_nota_fiscal, valor_nota_fiscal)
                                else:
                                    console.print("Não foi possivel obter o valor de urlRetorno/identificador")
                            except:
                                console.print(f"Erro ao obter os dados ou enviar a requisição: {e}")
                            
                            return RpaRetornoProcessoDTO(
                                sucesso=True,
                                retorno=retorno,
                                status=RpaHistoricoStatusEnum.Sucesso)
                        except Exception as e:
                            result = f"Arquivo CAIXA 13 DEVOLUÇÃO gerado com sucesso, porém gerou erro ao realizar o envio para o backoffice {e} - Arquivo ainda salvo na dispositivo utilizado no diretório {path_to_txt} !"
                            console.print(result, style="bold red")
                            return RpaRetornoProcessoDTO(
                                sucesso=False,
                                retorno=result,
                                status=RpaHistoricoStatusEnum.Falha,
                                tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                            )
                    else:
                        return RpaRetornoProcessoDTO(
                            sucesso=False,
                            retorno=f"O valor de entrada {penultimo_valor} não esta batendo com o valor de saída {ultimo_valor}, por favor verificar. \nEtapas Executadas:\n{steps}",
                            status=RpaHistoricoStatusEnum.Falha,
                            tags=[RpaTagDTO(descricao=RpaTagEnum.Negocio)]
                        )
                except Exception as e:
                    retorno = f"Não foi possivel concluir o processo de pré venda {e} \nEtapas Executadas:\n{steps}"
                    return RpaRetornoProcessoDTO(
                        sucesso=False,
                        retorno=retorno,
                        status=RpaHistoricoStatusEnum.Falha, 
                        tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                    )
            else:
                retorno = f"{preenchimento_header_pre_venda.retorno} \nEtapas Executadas:\n{steps}"
                return RpaRetornoProcessoDTO(
                    sucesso=False,
                    retorno=retorno,
                    status=RpaHistoricoStatusEnum.Falha, 
                    tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                )
    except Exception as ex:
        retorno = f"Erro Processo Devolução Prazo a Faturar: {str(ex)} \nEtapas Executadas:\n{steps}"
        logger.error(retorno)
        console.print(retorno, style="bold red")
        return RpaRetornoProcessoDTO(
            sucesso=False,
            retorno=retorno,
            status=RpaHistoricoStatusEnum.Falha,
        )
