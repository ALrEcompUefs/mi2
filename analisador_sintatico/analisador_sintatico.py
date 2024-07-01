from config import (OP_LOGIC_ONE_CHAR_SET, OP_RELATIONAL_ONE_CHAR_SET, OP_ARITIMETIC_ONE_CHAR_SET,
                    DELIMETER_CHAR_SET, STOP_ERRORS, ASCII,RESERVED_WORDS,TIPOS)

from interfaces import ComentarioBlocoAberto, Token, SintaxeMalFormada

import os
import re

class analisador_sintatico:
    def __init__(self) -> None:
        self.current_token = None
        self.next_token = None
        self.token_list = None

        # lista de erros sintaticos encontrados
        self.sintaxe_errors_list = []
    #---------------------------------------------------------------------------------------------------------
    '''
    |   Funções para operação da maquina de estados
    '''
    
    # função que atualiza o tokens atual e proximo
    def get_next_token(self):
        if len(self.token_list) >0: 
            # obtém primeiro token da lista
            self.current_token= self.token_list[0]
            print(self.current_token)
            #print(self.current_token,'\n')
            #remove o token da lista
            self.token_list.pop(0)
        else:
            self.current_token= None
            print('\n\ntodos os tokens foram consumidos\n\n')

    # função que realiza a recuperação de erro do analisador sintatico
    # rcupera erros para tokens por valor
    def recuperacao_de_erro(self,expected_token)->int:

        start_line = self.current_token.line
        end_line='EOF'

        # token lido
        read_token = self.current_token.token
        # executa o while até encontrar o token esperado ou que não existam mais tokens

        while(self.current_token != None and self.current_token.token not in expected_token ):
            self.get_next_token()

        # após encerrar verifica se encontrou o token ou não
        if(self.current_token != None):
            # se não for vazio então encontrou o token
            end_line =self.current_token.line

        self.sintaxe_errors_list.append(SintaxeMalFormada(start_line,end_line,read_token,expected_token))

    # função que realiza a recuperação de erro do analisador sintatico
    # recupera erros para tokens por tipo
    def recuperacao_de_erro_tipo(self,expected_type)->int:

        start_line = self.current_token.line
        end_line='EOF'

        # tipo de token lido
        read_token = self.current_token.code
        # executa o while até encontrar o token esperado ou que não existam mais tokens

        while(self.current_token != None and self.current_token.code not in expected_type ):
            self.get_next_token()

        # após encerrar verifica se encontrou o token ou não
        if(self.current_token != None):
            # se não for vazio então encontrou o token
            end_line =self.current_token.line

        self.sintaxe_errors_list.append(SintaxeMalFormada(start_line,end_line,read_token,expected_type))

    # função que realiza a recuperação de erro do analisador sintatico
    # recupera erros para tokens por tipo e valor
    def recuperacao_de_erro_tipo_valor(self,expected_token,expected_type):

        start_line = self.current_token.line
        end_line='EOF'

        # token lido
        read_token = self.current_token.token
        # executa o while até encontrar o token esperado ou que não existam mais tokens

        while(self.current_token != None and self.current_token.token not in expected_token and self.current_token.code not in expected_type):
            self.get_next_token()

        # após encerrar verifica se encontrou o token ou não
        if(self.current_token != None):
            # se não for vazio então encontrou o token
            end_line =self.current_token.line

        self.sintaxe_errors_list.append(SintaxeMalFormada(start_line,end_line,read_token,expected_type))

    def read_tokens(self)->list[Token]:
        ark='entrada.txt'
        tokens=[]
        pattern = re.compile(r"(\d+)\s+([A-Z]+)\s+(.+)")
        with open(ark, 'r', encoding='utf-8') as file:
            for line in file:
                match = pattern.match(line.strip())
                if match:
                    line_number = int(match.group(1))
                    code = match.group(2)
                    token = match.group(3)
                    tokens.append(Token(line=line_number, code=code, token=token))
        return tokens
    #---------------------------------------------------------------------------------------------------------
    '''
    |   Funções que fazem a analise de formação das produções de nivél mais alto da gramatica
    |   algoritmo,corpo,funções,bloco,escopo,constantes,variavies registros
    '''
    #função para analisar formação da estrutura de mais alto nivel do programa 
    def funcao_algortimo(self):
        # variavel para controle dos estados
        current_state= 0
        # atualiza o token atual, elimina 'ALGORITMO'
        self.get_next_token()

        # enquanto existirem tokens na lista o laço é executado
        while(self.current_token != None):
            print(current_state)
            match current_state:
                case 0:
                    if(self.current_token.token == '{'):
                        self.get_next_token()
                        current_state = 1
                    else:
                        self.recuperacao_de_erro(['{'])
                case 1: 
                    if(self.current_token.token == '}'):
                        current_state=4
                        self.get_next_token() 
                    else:
                        current_state=2
                case 2:
                    # neste estado começa uma produção de bloco
                    self.funcao_corpo()
                    current_state= 3
                case 3: #remover depois
                    if(self.current_token.token == '}'):
                        current_state=4
                        self.get_next_token()
                    else:
                        self.recuperacao_de_erro(['}'])
                case 4:
                    # era esperado que não houvesse tokens após o fecha chaves
                    #chama a recuperação de erros até consumir todos tokens
                    self.recuperacao_de_erro([None])
                case _:
                    pass
        
    # funcão para analisar formação de um bloco
    def funcao_corpo(self):
        # variavel para controle dos estados
        current_state= 0
        #variavel que define o fim da estrutura em produção
        fim_producao = False
        while(self.current_token != None and not fim_producao):
           
            match(current_state):
                case 0:
                    # no caso 0 verifica qual o token que inicia a estrutura corpo
                    # outro match case para as opções possivéis {constantes,variaveis,registro,funcao,principal}
                    match(self.current_token.token):
                        case 'constantes':
                            self.funcao_bloco_constantes()
                            current_state = 1
                        case 'variaveis':
                            self.funcao_bloco_variaveis()
                            current_state = 2
                        case 'registro':
                            self.funcao_registro()
                            current_state = 2
                        case 'funcao':
                            self.funcao_listagem_funcoes()
                            current_state = 4
                        case 'principal':
                            self.funcao_principal()
                            current_state=5
                        case _:
                            # se nenhum dos casos anteriores aparecer então chama a recuperação de erro
                            self.recuperacao_de_erro(['constantes','variaveis','registro','funcao','principal'])
                case 1: #verifica as opções de formação possiveis após um bloco de constantes
                    match(self.current_token.token):
                        case 'variaveis':
                            self.funcao_bloco_variaveis()
                            current_state = 2
                        case 'registro':
                            self.funcao_registro()
                            current_state = 2
                        case 'funcao':
                            self.funcao_listagem_funcoes()
                            current_state = 4
                        case 'principal':
                            self.funcao_principal()
                            current_state=5
                        case _:
                            # se nenhum dos casos anteriores aparecer então chama a recuperação de erro
                            self.recuperacao_de_erro(['variaveis','registro','funcao','principal'])
                case 2:#verifica as opções de formação possiveis após um bloco de variavies
                    match(self.current_token.token):
                        case 'registro':
                            self.funcao_registro()
                            current_state = 2
                        case 'funcao':
                            self.funcao_listagem_funcoes()
                            current_state = 4
                        case 'principal':
                            self.funcao_principal()
                            current_state=5
                        case _:
                            # se nenhum dos casos anteriores aparecer então chama a recuperação de erro
                            self.recuperacao_de_erro(['registro','funcao','principal'])
                case 3: # verifica as opções de formação possivéis após blocos de registros
                    match(self.current_token.token):
                        case 'funcao':
                            self.funcao_listagem_funcoes()
                            current_state = 4
                        case 'principal':
                            self.funcao_principal()
                            current_state=5
                        case _:
                            # se nenhum dos casos anteriores aparecer então chama a recuperação de erro
                            self.recuperacao_de_erro(['funcao','principal'])
                case 4: #verifica as opções de formação possivéis após declaração de funções
                    if(self.current_token.token == 'funcao'):
                        self.funcao_listagem_funcoes()
                        current_state=4
                    elif(self.current_token.token == 'principal'):
                        self.funcao_principal()
                        current_state=5
                    else:
                        # se nenhum dos casos anteriores aparecer então chama a recuperação de erro
                        self.recuperacao_de_erro(['funcao','principal'])
                case 5:
                    fim_producao = True
                case _:
                   pass

    # função para formação de um escopo
    def funcao_escopo(self):
        # variavel para controle dos estados
        current_state= 0
        #variavel que define o fim da estrutura em produção
        fim_producao = False

        while(self.current_token != None and not fim_producao):
            match(current_state):
                case 0:
                    # no caso 0 verifica qual o token que inicia a estrutura do escopo
                    # outro match case para as opções possivéis {constantes,variaveis,bloco,retorno}
                    match(self.current_token.token):
                        case 'constantes':
                            self.funcao_bloco_constantes()
                            current_state = 1
                        case 'variaveis':
                            self.funcao_bloco_variaveis()
                            current_state = 2
                        case 'retorno':
                            self.funcao_retorno()
                            current_state = 5
                        case 'se':
                            current_state=3
                        case 'enquanto':
                            current_state=3
                        case 'leia':
                            current_state=3
                        case 'escreva':
                            current_state=3
                        case 'retorno':
                            current_state=3
                        case _:
                            # se por fim não leu um IDE vai pra recuperação de erro
                            if(self.current_token.code == 'IDE'):
                                current_state=3
                            else:
                                self.recuperacao_de_erro_tipo(['se','enquanto','leia','escreva','retorno','}'],['IDE'])
                case 1:
                    # após formação de um bloco de constantes
                    match(self.current_token.token):
                        case 'variaveis':
                            self.funcao_bloco_variaveis()
                            current_state = 2
                        case 'retorno':
                            self.funcao_retorno()
                            current_state = 5
                        case 'se':
                            current_state=3
                        case 'enquanto':
                            current_state=3
                        case 'leia':
                            current_state=3
                        case 'escreva':
                            current_state=3
                        case 'retorno':
                            current_state=3
                        case _:
                            # se por fim não leu um IDE vai pra recuperação de erro
                            if(self.current_token.code == 'IDE'):
                                current_state=3
                            else:
                                self.recuperacao_de_erro_tipo(['se','enquanto','leia','escreva','retorno','}'],['IDE'])
                case 2:
                    # após formação de um bloco de variaveis
                    match(self.current_token.token):
                        case 'retorno':
                            self.funcao_retorno()
                            current_state = 5
                        case 'se':
                            current_state=3
                        case 'enquanto':
                            current_state=3
                        case 'leia':
                            current_state=3
                        case 'escreva':
                            current_state=3
                        case 'retorno':
                            current_state=3
                        case _:
                            # se por fim não leu um IDE vai pra recuperação de erro
                            if(self.current_token.code == 'IDE'):
                                current_state=3
                            else:
                                self.recuperacao_de_erro_tipo(['se','enquanto','leia','escreva','retorno','}'],['IDE'])
                case 3:
                    # estado de formação do bloco
                    self.funcao_bloco()
                    current_state=4
                case 4:
                    #chama a função para retorno
                    self.funcao_retorno()
                    # vai para o estado final
                    current_state=5
                case 5:
                    if(self.current_token.token =='}'):
                        current_state=6
                    else:
                        self.recuperacao_de_erro(['}'])
                case 6:
                    fim_producao = True
                case _:
                    pass
    
    # função de formação do bloco
    def funcao_bloco(self):
        current_state = 0
        #variavel que define o fim da estrutura em produção
        fim_producao = False

        while(self.current_token != None and not fim_producao):
            match(current_state):
                case 0:
                    # no caso 0 verifica qual o token que inicia a estrutura corpo
                    # outro match case para as opções possivéis {se,enquanto,leia,escreva,reatribuicao}
                    match(self.current_token.token):
                        case 'se':
                            #chama a funcao_se e permanece no estado atual
                            self.funcao_se()
                        case 'enquanto':
                            #chama a enquanto e permanece no estado atual
                            self.funcao_enquanto()
                        case 'leia':
                            #chama a leia e permanece no estado atual
                            self.funcao_leia()
                        case 'escreva':
                            #chama a escreva e permanece no estado atual
                            self.funcao_escreva()
                        case 'retorno':
                            # um retorno é o fim para um bloco
                            # vai para o estado final
                            current_state=2
                        case '}':
                            # um retorno é o fim para um bloco
                            # vai para o estado final
                            current_state=2
                        case _:
                            if(self.current_token.code =='IDE'):
                                self.funcao_reatribuicao()
                                current_state=1
                            else:
                                self.recuperacao_de_erro_tipo(['se','enquanto','leia','escreva','retorno','}'],['IDE'])
                case 1:
                    #chama a função de reatribuição
                    current_state=0
                case 2:
                    fim_producao= True
                case _:
                    pass
        
    #função para analisar formação da declaração de um bloco de constantes
    def funcao_bloco_constantes(self):
        current_state = 0
        #variavel que define o fim da estrutura em produção
        fim_producao = False
        # atualiza para o proximo token, elimina 'constantes'
        self.get_next_token()

        while(self.current_token !=None and not fim_producao):
            match(current_state):
                case 0:
                    if(self.current_token.token == '{'):
                        current_state=1
                        self.get_next_token()
                    else:
                        self.recuperacao_de_erro(['{'])
                case 1:
                    match(self.current_token.token):
                        case '}': # um fechamento de chaves leva direto para o estado final
                            self.get_next_token()
                            current_state=2
                        case 'inteiro':
                            self.funcao_declaracao_constantes_numericas()
                        case 'real':
                            self.funcao_declaracao_constantes_numericas()
                        case 'booleano':
                            self.funcao_declaracao_constantes_booleanos()
                        case 'char':
                            self.funcao_declaracao_constantes_char()
                        case 'cadeia':
                            self.funcao_declaracao_constantes_char()
                        case _:
                            self.recuperacao_de_erro(['}','inteiro','real', 'booleano', 'char','cadeia'])
                case 2: #ultimo estado
                    fim_producao = True
                case _:
                    pass
            
    #função para analisar formação de um bloco de variaveis
    def funcao_bloco_variaveis(self):
        current_state = 0
        #variavel que define o fim da estrutura em produção
        fim_producao = False
        # atualiza para o proximo token, elimina 'variaveis' 
        # ou se for um registro elimina o 'IDE'
        self.get_next_token()

        while(self.current_token !=None and not fim_producao):
            match(current_state):
                case 0:
                    if(self.current_token.token == '{'):
                        current_state=1
                        self.get_next_token()
                    else:
                        self.recuperacao_de_erro(['}'])
                case 1:
                    match(self.current_token.token):
                        case '}':
                            self.get_next_token()
                            current_state=2
                        case 'inteiro':
                            self.funcao_declaracao_variavel()
                        case 'real':
                            self.funcao_declaracao_variavel()
                        case 'booleano':
                            self.funcao_declaracao_variavel()
                        case 'char':
                            self.funcao_declaracao_variavel()
                        case 'cadeia':
                            self.funcao_declaracao_variavel()
                        case _:
                            if(self.current_token.code == 'IDE'):
                                self.funcao_declaracao_variavel()
                            else:
                                self.recuperacao_de_erro_tipo_valor(['}','inteiro','real','booleano','char','cadeia'],['IDE'])
                case 2:
                    fim_producao=True
                case _:
                    pass
    
    def funcao_registro(self):
        current_state = 0
        #variavel que define o fim da estrutura em produção
        fim_producao = False
        # atualiza para o proximo token, elimina 'registro'
        self.get_next_token()

        while(self.current_token !=None and not fim_producao):
            match(current_state):
                case 0:
                    if(self.current_token.code == 'IDE'):
                        self.funcao_bloco_variaveis()
                        current_state=1
                    else:
                        self.recuperacao_de_erro_tipo(['IDE'])
                case 1:
                    fim_producao=True
                case _:
                    pass

    # função para analisar formação de uma listagem de funções
    def funcao_listagem_funcoes(self):
        current_state = 0
        #variavel que define o fim da estrutura em produção
        fim_producao = False
        # atualiza para o proximo token, elimina funcao
        self.get_next_token()

        while(self.current_token != None and not fim_producao):
            match(current_state):
                case 0:
                    if(self.current_token.token in TIPOS or self.current_token.code =='IDE'):
                        current_state=1
                        self.get_next_token()
                    else:
                        self.recuperacao_de_erro_tipo_valor(['booleano','inteiro','real','char','cadeia','vazio'],['IDE'])
                case 1:
                    if(self.current_token.code == 'IDE'):
                        current_state=2
                        self.get_next_token()
                    else:
                        self.recuperacao_de_erro_tipo(['IDE'])
                case 2:
                    if(self.current_token.token == '('):
                        self.funcao_listagem_parametros()
                        current_state=3
                    else:
                        self.recuperacao_de_erro(['('])
                case 3:
                    if(self.current_token.token == '{'):
                        current_state=4
                        self.get_next_token()
                    else:
                        self.recuperacao_de_erro(['{'])
                case 4:
                    # após { espera um escopo ou um }
                    if(self.current_token.token == '}'):
                        current_state=6
                        self.get_next_token()
                    else:
                        self.funcao_escopo()
                        current_state=5
                case 5:
                    if(self.current_token.token == '}'):
                        current_state=6
                        self.get_next_token()
                    else:
                        self.recuperacao_de_erro(['}'])
                case 6:
                    fim_producao=True
                case _:
                    pass

    # função para analisar formação da declarção da função principal
    def funcao_principal(self):
        current_state = 0
        #variavel que define o fim da estrutura em produção
        fim_producao = False
        # atualiza para o proximo token, elimina principal
        self.get_next_token()

        while(self.current_token != None and not fim_producao):
            match(current_state):
                case 0:
                    if(self.current_token.token == '('):
                        self.funcao_listagem_parametros()
                        current_state=1
                    else:
                        self.recuperacao_de_erro([')'])
                case 1:
                    if(self.current_token.token == '{'):
                        current_state=2
                        self.get_next_token()
                    else:
                        self.recuperacao_de_erro(['{'])
                case 2:
                    # após { espera um escopo ou um }
                    if(self.current_token.token == '}'):
                        current_state=5
                        self.get_next_token()
                    else:
                        self.funcao_escopo()
                        current_state=4
                case 4:
                    if(self.current_token.token == '}'):
                        current_state=5
                        self.get_next_token()
                    else:
                        self.recuperacao_de_erro(['}'])
                case 5:
                    fim_producao=True
                case _:
                    pass
    
    #--------------------------------------------------------------------------------------
    ''' 
    |   Funções relacionadas ao bloco de constantes
    |   declarção númerica,cadeia
    '''
    def funcao_declaracao_constantes_numericas(self):
        current_state = 0
        # atualiza para o proximo token, elimina 'inteiro'
        self.get_next_token()
        #variavel que define o fim da estrutura em produção
        fim_producao = False

        while(self.current_token !=None and not fim_producao):
            match(current_state):
                case 0:
                    if(self.current_token.code == 'IDE'):
                        current_state= 1
                        self.get_next_token()
                    else:
                        self.recuperacao_de_erro_tipo(['IDE'])
                case 1:
                    if(self.current_token.token == '='):
                        current_state= 2
                        self.get_next_token()
                    else:
                        self.recuperacao_de_erro(['='])
                case 2:
                    #após um = espera uma expressão numérica
                    self.funcao_formacao_expressao_numerica()
                    current_state = 3
                case 3:
                    if(self.current_token.token == ';'):
                        current_state= 4
                        self.get_next_token()
                    elif(self.current_token.token ==','):
                        current_state =0
                        self.get_next_token()
                    else:
                        self.recuperacao_de_erro([';',','])
                case 4:
                    fim_producao = True
                case _:
                    pass
    # função para declaração e listagem de constantes reais
    # não é mais utilizada
    def funcao_declaracao_constantes_reais(self):
        current_state = 0
        # atualiza para o proximo token, elimina 'real'
        self.get_next_token()
        #variavel que define o fim da estrutura em produção
        fim_producao = False

        while(self.current_token !=None and not fim_producao):
            match(current_state):
                case 0:
                    if(self.current_token.code == 'IDE'):
                        current_state= 1
                        self.get_next_token()
                    else:
                        self.recuperacao_de_erro_tipo(['IDE'])
                case 1:
                    if(self.current_token.token == '='):
                        current_state= 2
                        self.get_next_token()
                    else:
                        self.recuperacao_de_erro(['='])
                case 2:
                    self.funcao_formacao_expressao_numerica()
                    current_state = 3
                case 3:
                    if(self.current_token.token == ';'):
                        current_state= 4
                        self.get_next_token()
                    elif(self.current_token.token ==','):
                        current_state =0
                        self.get_next_token()
                    else:
                        self.recuperacao_de_erro([';',','])
                case 4:
                    fim_producao = True
                case _:
                    pass
        
    # função para declaração e listagem de constantes de caracteres e cadeias
    def funcao_declaracao_constantes_char(self):
        current_state = 0
        # atualiza para o proximo token, elimina 'char'
        self.get_next_token()
        #variavel que define o fim da estrutura em produção
        fim_producao = False

        while(self.current_token !=None and not fim_producao):
            match(current_state):
                case 0:
                    if(self.current_token.code == 'IDE'):
                        current_state= 1
                        self.get_next_token()
                    else:
                        self.recuperacao_de_erro_tipo(['IDE'])
                case 1:
                    if(self.current_token.token == '='):
                        current_state= 2
                        self.get_next_token()
                    else:
                        self.recuperacao_de_erro(['='])
                case 2:
                    if(self.current_token.code == 'CAC'):
                        current_state = 3
                        self.get_next_token()
                    else:
                        self.recuperacao_de_erro_tipo(['CAC'])
                case 3:
                    if(self.current_token.token == ';'):
                        current_state= 4
                        self.get_next_token()
                    elif(self.current_token.token ==','):
                        current_state =0
                        self.get_next_token()
                    else:
                        self.recuperacao_de_erro([';',','])
                case 4:
                    fim_producao = True
                case _:
                    pass
    
    # função para declaração e listagem de constantes de cadeias de caracteres
    def funcao_declaracao_constantes_booleanos(self):
        current_state = 0
        # atualiza para o proximo token, elimina 'char'
        self.get_next_token()
        #variavel que define o fim da estrutura em produção
        fim_producao = False

        while(self.current_token !=None and not fim_producao):
            match(current_state):
                case 0:
                    if(self.current_token.code == 'IDE'):
                        current_state= 1
                        self.get_next_token()
                    else:
                        self.recuperacao_de_erro_tipo(['IDE'])
                case 1:
                    if(self.current_token.token == '='):
                        current_state= 2
                        self.get_next_token()
                    else:
                        self.recuperacao_de_erro(['='])
                case 2:
                    # após um = espera uma expressão booleana
                    self.funcao_formacao_expressao_booleana()
                    current_state = 3
                case 3:
                    if(self.current_token.token == ';'):
                        current_state= 4
                        self.get_next_token()
                    elif(self.current_token.token ==','):
                        current_state =0
                        self.get_next_token()
                    else:
                        self.recuperacao_de_erro([';',','])
                case 4:
                    fim_producao = True
                case _:
                    pass
    #--------------------------------------------------------------------------------------------------

    #--------------------------------------------------------------------------------------------------
    '''
    |   Funções relacionadas a produções de declarações de variaveis
    |   versão otimizada para reduzir funções
    |
    '''
    def funcao_declaracao_variavel(self):
        current_state = 0
        # atualiza para o proximo token, elimina o tipo
        self.get_next_token()
        #variavel que define o fim da estrutura em produção
        fim_producao = False

        while(self.current_token != None and not fim_producao):
            match(current_state):
                case 0:
                    if(self.current_token.code == 'IDE'):
                        current_state=1
                        self.get_next_token()
                    else:
                        self.recuperacao_de_erro_tipo(['IDE'])
                case 1:
                    match(self.current_token.token):
                        case ';':
                            current_state=2
                            self.get_next_token()
                        case ',':
                            current_state=0
                            self.get_next_token()
                        case '[':
                            self.funcao_formacao_vetor_matriz()
                        case _:
                            self.recuperacao_de_erro([';',',','['])
                case 2:
                    fim_producao=True
                case _:
                    pass
    # função que analisa a fomaração da declaração de um vetor ou matriz
    def funcao_formacao_vetor_matriz(self):
        current_state = 0
        #variavel que define o fim da estrutura em produção
        fim_producao = False

        while(self.current_token != None and not fim_producao):
            match(current_state):
                case 0:
                    if(self.current_token.token == '['):
                        current_state=1
                        self.get_next_token()
                    else:
                        self.recuperacao_de_erro(['['])
                case 1:
                   self.funcao_formacao_expressao_numerica()
                   current_state=2
                case 2:
                    if(self.current_token.token == ']'):
                        current_state=3
                        self.get_next_token()
                    else:
                        self.recuperacao_de_erro([']'])
                case 3:
                    if(self.current_token.token == '['):
                        current_state=1
                        self.get_next_token()
                    else:
                        current_state=4
                case 4:
                    fim_producao = True
                case _:
                    pass
    #-------------------------------------------------------------------------------------------------------
    # função que analisa formação da listagem de parametros de uma função
    def funcao_listagem_parametros(self):
        current_state = 0
        #variavel que define o fim da estrutura em produção
        fim_producao = False
        # atualiza para o proximo token, elimina '('
        self.get_next_token()

        while(self.current_token != None and not fim_producao):
            match(current_state):
                case 0:
                    if(self.current_token.token in TIPOS):
                        current_state=1
                        self.get_next_token()
                    elif(self.current_token.token ==')'):
                        current_state=4
                        self.get_next_token()
                    else:
                        self.recuperacao_de_erro_tipo_valor(['booleano','inteiro','real','char','cadeia','vazio'],[')'])
                case 1:
                    if(self.current_token.code =='IDE'):
                        current_state=2
                        self.get_next_token()
                    else:
                        self.recuperacao_de_erro_tipo(['IDE'])
                case 2:
                    if(self.current_token.token =='['):
                        #chama a função de produção de vetor
                        self.funcao_formacao_vetor_matriz()
                        current_state=3
                    else:
                        #caso contrario passa para o estado 3
                        current_state=3
                case 3:
                    if(self.current_token.token ==')'):
                        current_state=4
                        self.get_next_token()
                    elif(self.current_token.token == ','):
                        current_state=0
                        self.get_next_token()
                    else:
                        self.recuperacao_de_erro([')',','])
                case 4:
                    fim_producao=True
                case _:
                    pass
    #----------------------------------------------------------------------------------------------------

    # funcão que analisa a formação de declaração de parametros de uma função
    def funcao_listagem_parametros_chamada(self):
        current_state = 0
        #variavel que define o fim da estrutura em produção
        fim_producao = False
        # atualiza para o proximo token, elimina '('
        self.get_next_token()

        while(self.current_token != None and not fim_producao):
            match(current_state):
                case 0:
                    if(self.current_token.token == ')'):
                        current_state=2
                    else:
                        # chama a expressão geral
                        self.funcao_formacao_expressao_geral()
                        current_state=1    
                case 1:
                    if(self.current_token.token == ')'):
                        #finaliza chamada
                        current_state=2
                    elif(self.current_token.token == ','):
                        self.get_next_token()
                        current_state=0
                    else:
                        self.recuperacao_de_erro([')',','])
                case 2:
                    fim_producao=True
                case _:
                    pass    
    
    # função que analisa formação da formação do uso de um identificador,vetor,registro ou chamada defunção
    def funcao_formacao_ideVeRe_chamada(self):
        current_state = 0
        #variavel que define o fim da estrutura em produção
        fim_producao = False

        while(self.current_token != None and not fim_producao):
            match(current_state):
                case 0:
                    if(self.current_token.token == '['):
                        current_state=1
                        self.get_next_token()
                    elif(self.current_token.token =='.'):
                        current_state=2
                        self.get_next_token()
                    elif(self.current_token.token == '('):
                        current_state=3
                    else:
                        self.recuperacao_de_erro(['[','.','('])
                case 1:
                    # como é esperada uma expressão númerica
                    # faz a chamada para expressão númerica
                    self.funcao_formacao_expressao_numerica()
                    current_state=4
                case 2:
                    if(self.current_token.code == 'IDE'):
                        self.get_next_token()
                        current_state= 6
                    else:
                        self.recuperacao_de_erro_tipo(['IDE'])
                case 3:
                    #chama leitura de parametros de função
                    self.funcao_listagem_parametros_chamada()
                    current_state=5
                case 4:
                    if(self.current_token.token == ']'):
                        #finalizou a produção
                        self.get_next_token()
                        #volta para o inicio
                        current_state=6
                    else:
                        self.recuperacao_de_erro([']'])
                case 5:
                    if(self.current_token.token == ')'):
                        #finalizou a produção
                        self.get_next_token()
                        #volta para o inicio
                        current_state=6
                    else:
                        self.recuperacao_de_erro([')'])
                case 6:
                    if(self.current_token.token == '[' or self.current_token.token == '.' or self.current_token.token == ')'):
                        current_state=0
                    else:
                        current_state=7
                case 7:
                    fim_producao= True
                case _:
                    pass
    
    # Listagem dos parametros da função leia
    def funcao_listagem_parametros_leia(self):
        current_state = 0
        #variavel que define o fim da estrutura em produção
        fim_producao = False

        while(self.current_token != None and not fim_producao):
            match(current_state):
                case 0:
                    if(self.current_token.code == 'IDE'):
                        self.get_next_token()
                        self.funcao_formacao_ideVeRe_chamada()
                        current_state=1
                    elif(self.current_token.token ==')'):
                        current_state=2
                    else:
                        self.recuperacao_de_erro_tipo_valor([')',['IDE']])
                case 1:
                    if(self.current_token.token == ','):
                        current_state=0
                        self.get_next_token()
                    elif(self.current_token.token ==')'):
                        current_state=2
                    else:
                        self.recuperacao_de_erro([',',')'])
                case 2:
                    fim_producao=True
                case _:
                    pass 
    # função do retorno
    def funcao_retorno(self):
        current_state = 0
        #variavel que define o fim da estrutura em produção
        fim_producao = False
        # elimina o 'retorno'
        self.get_next_token()

        while(self.current_token != None and not fim_producao):
            match(current_state):
                case 0:
                    if(self.current_token.token ==';'):
                        #vai direto para o estado final
                        current_state=2
                        self.get_next_token()
                    else:
                        #chama produção da expressão geral
                        self.funcao_formacao_expressao_geral()
                        current_state=1
                case 1:
                    if(self.current_token.token ==';'):
                        current_state=2
                        self.get_next_token()
                    else:
                        self.recuperacao_de_erro(';')
                case 2:
                    fim_producao= True
                case _:
                    pass
                
   #--------------------------------------------------------------------------------------------------
    '''
    |   Funções relacionadas a produções de expressões
    |   númericas, relacionais , aritimeticas
    |
    '''
   
    def funcao_formacao_expressao_booleana(self):
        current_state = 0
        #variavel que define o fim da estrutura em produção
        fim_producao = False
        # devido a recursão da função boolena não a elminação do primeiro token de formação

        while(self.current_token != None and not fim_producao):
            match(current_state):
                # Estado inicial
                case 0:
                    if(self.current_token.token =='verdadeiro' or self.current_token.token =='falso'):
                        current_state=1
                        self.get_next_token()
                    elif(self.current_token.code =='IDE'):
                        self.get_next_token()
                        self.funcao_formacao_ideVeRe_chamada()
                        current_state=1
                    elif(self.current_token.token == '||' or self.current_token.token == '&&' or self.current_token.token == '!'):
                        current_state=2
                        self.get_next_token()
                    elif(self.current_token.token == '('):
                        #consome o token atual
                        self.get_next_token()
                        # chama a função de formação da expressão booleana
                        self.funcao_formacao_expressao_booleana()
                        current_state=3
                    else:
                        self.recuperacao_de_erro_tipo_valor(['verdadeiro','falso','||','&&','!','('],['IDE'])
                # Estado após receber um identificador ou valor booleano ou (
                case 1:
                    if(self.current_token.token == '||' or self.current_token.token == '&&'):
                        current_state=2
                        self.get_next_token()
                    elif(self.current_token.token == ')'):
                        #finaliza esta expressão booleana
                        current_state=4
                    elif(self.current_token.token == ';' or self.current_token.token == ','):
                        current_state=4
                    else:
                        self.recuperacao_de_erro(['||','&&',';',',',')'])
                #estado após receber !,&& ou ||
                case 2:
                    if(self.current_token.token =='verdadeiro' or self.current_token.token =='falso'):
                        current_state=1
                        self.get_next_token()
                    elif(self.current_token.code =='IDE'):
                        self.get_next_token()
                        self.funcao_formacao_ideVeRe_chamada()
                        current_state=1
                    elif(self.current_token.token == '('):
                        self.get_next_token()
                        self.funcao_formacao_expressao_booleana()
                        current_state=3
                    elif(self.current_token.token == '!'):
                        self.get_next_token()
                        current_state=2
                    else:
                        self.recuperacao_de_erro_tipo_valor(['verdadeiro','falso','!','('],['IDE'])
                # após abertura de parenteses
                case 3:
                    if(self.current_token.token == ')'):
                        self.get_next_token()
                        current_state=1
                    else:
                        self.recuperacao_de_erro([')'])
                case 4:
                    fim_producao = True
                case _:
                    pass
        return None
    
    # expressão númerica
    def funcao_formacao_expressao_numerica(self):
        current_state = 0
        #variavel que define o fim da estrutura em produção
        fim_producao = False
        # devido a recursão da expressão não há elminação do primeiro token de formação

        while(self.current_token != None and not fim_producao):
            match(current_state):
                case 0:
                    if(self.current_token.token == '+' or self.current_token.token == '-'):
                        self.get_next_token()
                        current_state=1
                    elif(self.current_token.token == '*' or self.current_token.token == '/'):
                        self.get_next_token()
                        current_state =1
                    elif(self.current_token.token =='('):
                        # após um abre parenteses espera uma expressao numerica
                        # faz a chamada recursiva para a função
                        #self.funcao_formacao_expressao_numerica()
                        self.get_next_token()
                        self.funcao_formacao_expressao_numerica()
                        current_state=3
                    elif(self.current_token.code == 'IDE'):
                        self.get_next_token()
                        self.funcao_formacao_ideVeRe_chamada()
                        current_state=2
                    elif(self.current_token.code == 'NRO'):
                        self.get_next_token()
                        current_state=2
                    else:
                        self.recuperacao_de_erro_tipo_valor(['+','-','/','*','('],['IDE','NRO'])
                case 1:
                    # após um operador exige obrigatoriamente um numero,IDE ou (
                    if(self.current_token.code == 'NRO'):
                        self.get_next_token()
                        current_state=2
                    elif(self.current_token.code == 'IDE'):
                        self.get_next_token()
                        self.funcao_formacao_ideVeRe_chamada()
                        current_state=2
                    elif(self.current_token.token == '('):
                        # após um abre parenteses espera uma expressao numerica
                        # faz a chamada recursiva para a função
                        # self.funcao_formacao_expressao_numerica()
                        self.get_next_token()
                        self.funcao_formacao_expressao_numerica()
                        current_state=3
                    else:
                        self.recuperacao_de_erro_tipo_valor(['('],['IDE','('])
                case 2:
                    # após um número,ide ou ) exige ser um operador,) ou fim da expressão
                    if(self.current_token.token =='+' or self.current_token.token =='-'):
                        self.get_next_token()
                        current_state=1
                    elif(self.current_token.token =='*' or self.current_token.token =='/'):
                        self.get_next_token()
                        current_state=1
                    elif(self.current_token.token ==')'):
                        current_state=4
                    elif(self.current_token.token == ';' or self.current_token.token == ',' or self.current_token.token == ']'):
                        current_state=4
                    else:
                        self.recuperacao_de_erro(['+','-','*','/',')',';',',',']'])
                case 3:
                    # após receber uma abertura de parenteses
                    # finalizada outra chamada de expressao numerica
                    if(self.current_token.token == ')'):
                      self.get_next_token()
                      current_state=2
                    else:
                        self.recuperacao_de_erro([')'])
                case 4:
                    fim_producao=True
                case _:
                    pass
        return None

    # a bendita expressão geral
    def funcao_formacao_expressao_geral(self):
        current_state = 0
        #variavel que define o fim da estrutura em produção
        fim_producao = False
        # devido a recursão da expressão geral não há elminação do primeiro token de formação

        while(self.current_token != None and not fim_producao):
            #print('estado',current_state,' token',self.current_token)
            match(current_state):
                # estado inicial da expressão geral
                case 0:
                    # corrirgir esse trecho depois
                    # pode ser otimizado
                    if(self.current_token.token == 'verdadeiro' or self.current_token.token == 'falso'):
                        self.get_next_token()
                        current_state = 4
                    elif(self.current_token.code == 'NRO' or self.current_token.code == 'CAC'):
                        self.get_next_token()
                        current_state = 4
                    elif(self.current_token.code == 'IDE'):
                        self.get_next_token()
                        current_state=1
                    elif(self.current_token.token == '!'):
                        self.funcao_formacao_expressao_booleana()
                        current_state = 6
                    elif(self.current_token.token == '('):
                        self.get_next_token()
                        current_state=2
                case 1:
                    # chama a função referente para essa produção
                    self.funcao_formacao_ideVeRe_chamada()
                    current_state=4
                case 2:
                    # é uma expressão geral entre parenteses
                    # deve ser feita a chamada a função e depois retorno para esse estado
                    # para que o fecha parenteses possa ser considerado
                    self.funcao_formacao_expressao_geral()
                    current_state=3
                case 3:
                    # após receber uma expressão geral
                    # agora precisa ser o fecha parenteses
                    if(self.current_token.token == ')'):
                        self.get_next_token()
                        current_state=4
                case 4:
                    # Esse é o estado E0 do automato
                    #todas transições possivéis são listadas
                    #todas as opções possivéis a partir do estado 3
                    if(self.current_token.token=='*' or self.current_token.token == '/'):
                        # chama a função para produção de expressão númerica
                        self.funcao_formacao_expressao_numerica()
                        current_state=5
                    elif(self.current_token.token=='+' or self.current_token.token == '-'):
                        # chama a função para produção de expressão númerica
                        self.funcao_formacao_expressao_numerica()
                        current_state=5
                    elif(self.current_token.token in ['>','<','>=','<=','==','!=']):
                        self.get_next_token()
                        current_state=0
                    elif(self.current_token.token == '&&'):
                        self.get_next_token()
                        current_state = 0
                    elif(self.current_token.token == '||'):
                        self.get_next_token()
                        current_state = 0
                    elif(self.current_token.token == ')'):
                      #finalizou a recursão da expressão geral
                      #retorna vai para o estado final e faz o retorno da função
                      current_state=11
                    elif(self.current_token.token == ';'):
                      #self.get_next_token()
                      current_state = 11
                    elif(self.current_token.token == ','):
                      current_state = 11
                    else:
                        # este else inviabiliza o tratamento de erro em expressões gerais
                        # por enquanto é a opção para finalizar uma expressão geral
                        current_state=11
                case 5:
                    if(self.current_token.token in ['>','<','>=','<=','==','!=']):
                        # consumindo o operador
                        self.get_next_token()
                        #volta para o estado inicial
                        current_state=0
                    elif(self.current_token.token == '&&'):
                        # consumindo o operador
                        self.get_next_token()
                        #volta para o estado inicial
                        current_state = 0
                    elif(self.current_token.token == '||'):
                        # consumindo o operador
                        self.get_next_token()
                        #volta para o estado inicial
                        current_state = 0
                    else:
                        # este else inviabiliza o tratamento de erro em expressões gerais
                        # por enquanto é a opção para finalizar uma expressão geral
                        current_state=11
                case 6:
                    if(self.current_token.token in ['>','<','>=','<=','==','!=']):
                        self.get_next_token()
                        current_state=0
                    elif(self.current_token.token == '&&'):
                        self.get_next_token()
                        current_state = 0
                    elif(self.current_token.token == '||'):
                        self.get_next_token()
                        current_state = 0
                    else:
                        # este else inviabiliza o tratamento de erro em expressões gerais
                        # por enquanto é a opção para finalizar uma expressão geral
                        current_state=11
                case 7:
                    pass
                case 11:
                    fim_producao= True
                case _:
                    pass
        return None
   
   #--------------------------------------------------------------------------------------------------
    '''
    |   Funções relacionadas ao bloco
    |   se, enquanto,leia,escreva,reatribuição
    |
    '''
    # método que analisa a formação de um bloco se
    def funcao_se(self):
        current_state = 0
        #variavel que define o fim da estrutura em produção
        fim_producao = False
        # Elimina o 'se'
        self.get_next_token()

        while(self.current_token != None and not fim_producao):
            match(current_state):
                case 0:
                    if(self.current_token.token =='('):
                        self.get_next_token()
                        current_state=1
                    else:
                        self.recuperacao_de_erro(['('])
                case 1:
                    # após um ( espera uma expressão geral
                    self.funcao_formacao_expressao_geral()
                    current_state=2
                case 2:
                    if(self.current_token.token ==')'):
                        self.get_next_token()
                        current_state=3
                    else:
                        self.recuperacao_de_erro([')'])
                case 3:
                    if(self.current_token.token =='{'):
                        self.get_next_token()
                        current_state=4
                    else:
                        self.recuperacao_de_erro(['{'])
                case 4:
                    # após { espera um bloco ou um }
                    if(self.current_token.token == '}'):
                        self.get_next_token()
                        current_state=6
                    else:
                        self.funcao_bloco()
                        current_state = 5
                case 5:
                    if(self.current_token.token == '}'):
                        self.get_next_token()
                        current_state=6
                    else:
                        self.recuperacao_de_erro(['}'])
                case 6:
                    if(self.current_token.token =='senao'):
                        self.funcao_senao()
                        current_state=7
                    else:
                        current_state=7
                case 7:
                    fim_producao= True
                case _:
                    pass
    # método que analisa a formação de um bloco senão
    def funcao_senao(self):
        current_state = 0
        #variavel que define o fim da estrutura em produção
        fim_producao = False
        # Elimina o 'senao'
        self.get_next_token()

        while(self.current_token != None and not fim_producao):
            match(current_state):
                case 0:
                    if(self.current_token.token =='{'):
                        self.get_next_token()
                        current_state=1
                    else:
                        self.recuperacao_de_erro(['{'])
                case 1:
                    # após { espera um bloco ou um }
                    if(self.current_token.token == '}'):
                        self.get_next_token()
                        current_state=3
                    else:
                        self.funcao_bloco()
                        current_state = 2
                case 2:
                    if(self.current_token.token == '}'):
                        self.get_next_token()
                        current_state=3
                    else:
                        self.recuperacao_de_erro(['}'])
                case 3:
                    fim_producao= True
                case _:
                    pass
    #método que analisa a formação de um bloco enquanto
    def funcao_enquanto(self):
        current_state = 0
        #variavel que define o fim da estrutura em produção
        fim_producao = False
        # Elimina o 'enquanto'
        self.get_next_token()

        while(self.current_token != None and not fim_producao):
            match(current_state):
                case 0:
                    if(self.current_token.token =='('):
                        self.get_next_token()
                        current_state=1
                    else:
                        self.recuperacao_de_erro(['('])
                case 1:
                    # após um ( espera uma expressão geral
                    self.funcao_formacao_expressao_geral()
                    current_state=2
                case 2:
                    if(self.current_token.token ==')'):
                        self.get_next_token()
                        current_state=3
                    else:
                        self.recuperacao_de_erro([')'])
                case 3:
                    if(self.current_token.token =='{'):
                        self.get_next_token()
                        current_state=4
                    else:
                        self.recuperacao_de_erro(['{'])
                case 4:
                    # após { espera um bloco ou um }
                    if(self.current_token.token == '}'):
                        self.get_next_token()
                        current_state=6
                    else:
                        self.funcao_bloco()
                        current_state = 5
                case 5:
                    if(self.current_token.token == '}'):
                        self.get_next_token()
                        current_state=6
                    else:
                        self.recuperacao_de_erro(['}'])
                case 6:
                    fim_producao= True
                case _:
                    pass

    # método que analisa a formação de uma função leia
    def funcao_leia(self):
        current_state = 0
        #variavel que define o fim da estrutura em produção
        fim_producao = False
        # Elimina o 'leia'
        self.get_next_token()

        while(self.current_token != None and not fim_producao):
            match(current_state):
                case 0:
                    if(self.current_token.token == '('):
                        self.get_next_token()
                        current_state=1
                    else:
                        self.recuperacao_de_erro(['('])
                case 1:
                    # chama o mesmo método de listagem de variaveis
                    self.funcao_listagem_parametros_leia()
                    current_state=2
                case 2:
                    if(self.current_token.token == ')'):
                        self.get_next_token()
                        current_state=3
                    else:
                        self.recuperacao_de_erro([')'])
                case 3:
                    if(self.current_token.token == ';'):
                        self.get_next_token()
                        current_state=4
                    else:
                        self.recuperacao_de_erro([';'])
                case 4:
                    fim_producao= True
                case _:
                    pass

    # método que analisa a formação de uma função escreva
    def funcao_escreva(self):
        current_state = 0
        #variavel que define o fim da estrutura em produção
        fim_producao = False
        # Elimina o 'escreva'
        self.get_next_token()

        while(self.current_token != None and not fim_producao):
            match(current_state):
                case 0:
                    if(self.current_token.token == '('):
                        current_state=1
                    else:
                        self.recuperacao_de_erro(['('])
                case 1:
                    if(self.current_token.token == ')'):
                        self.get_next_token()
                        current_state=3
                    else:
                        # chama o mesmo método de listagem de chamada de função
                        self.funcao_listagem_parametros_chamada()
                        current_state=2
                case 2:
                    if(self.current_token.token == ')'):
                        self.get_next_token()
                        current_state=3
                    else:
                        self.recuperacao_de_erro([')'])
                case 3:
                    if(self.current_token.token == ';'):
                        self.get_next_token()
                        current_state=4
                    else:
                        self.recuperacao_de_erro([';'])
                case 4:
                    fim_producao= True
                case _:
                    pass

    # método que analisa a formação de uma expressão de reatribuição
    def funcao_reatribuicao(self):
        current_state = 0
        #variavel que define o fim da estrutura em produção
        fim_producao = False
        # Elimina o IDE
        self.get_next_token()

        while(self.current_token != None and not fim_producao):
            #print('travei em:',current_state,'token',self.current_token)
            match(current_state):
                case 0:
                    if(self.current_token.token == '['):
                        self.get_next_token()
                        current_state=1
                    elif(self.current_token.token == '.'):
                        self.get_next_token()
                        current_state=3
                    elif(self.current_token.token == '='):
                        self.get_next_token()
                        current_state=4
                    else:
                        self.recuperacao_de_erro(['[','.','='])
                case 1:
                    #após um [ espera uma expressão númerica
                    self.funcao_formacao_expressao_numerica()
                    current_state=2
                case 2:
                    if(self.current_token.token == ']'):
                        self.get_next_token()
                        current_state=0
                    else:
                        self.recuperacao_de_erro([']'])
                case 3:
                    if(self.current_token.code == 'IDE'):
                        self.get_next_token()
                        current_state=0
                    else:
                        self.recuperacao_de_erro_tipo(['IDE'])
                case 4:
                    # após um = espera uma expressão geral
                    self.funcao_formacao_expressao_geral()
                    current_state=5
                case 5:
                    if(self.current_token.token == ';'):
                        self.get_next_token()
                        current_state=6
                    else:
                        self.recuperacao_de_erro([';'])
                case 6:
                    fim_producao = True
                case _:
                    pass

    # método executa a analise da formação da sintaxe do programa
    def proxima_producao(self):
        # variavel de controle dos estados
        current_state =0
        #obtém primeiro token
        self.get_next_token()
        # variavel para controle do laço
        fim_programa = False
        while(not fim_programa):
            match(current_state):
                case 0:
                    if( self.current_token.token == 'algoritmo'):
                        self.funcao_algortimo()
                        current_state =2
                    else:
                        current_state=1
                # estado para recuperação de erro
                case 1:
                    expected_token = ['algoritmo']
                    self.recuperacao_de_erro(expected_token)
                    current_state=0
                # Estado final
                case 2:
                    fim_programa=True
                    print('programa analisado')
                    print('Erros encontrados')
                    if (self.sintaxe_errors_list != None):
                        print(self.sintaxe_errors_list)
                    
                
a = analisador_sintatico()

a.token_list= a.read_tokens()
#print(a.token_list,'\n\n')
a.proxima_producao()
#a.get_next_token()

'''
while(a.current_token !=None):
    print('novo escopo')
    a.funcao_escopo()
    a.get_next_token()
    '''