from config import (OP_LOGIC_ONE_CHAR_SET, OP_RELATIONAL_ONE_CHAR_SET, OP_ARITIMETIC_ONE_CHAR_SET,
                    DELIMETER_CHAR_SET, STOP_ERRORS, ASCII,RESERVED_WORDS,TIPOS)

from interfaces import ComentarioBlocoAberto, Token, TokenDefeituoso

import os
import re

class analisador_sintatico:
    def __init__(self) -> None:
        self.current_token = None
        self.next_token = None
        self.token_list = None
        

        # lista de erros sintaticos encontrados
        self.errors = []

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

    #função para analisar formação da estrutura de mais alto nivel do programa 
    def funcao_algortimo(self):
        # variavel para controle dos estados
        current_state= 0
        # atualiza o token atual, elimina 'ALGORITMO'
        self.get_next_token()
        # enquanto existirem tokens na lista o laço é executado
        while(self.current_token != None):
            match current_state:
                case 0:
                    if(self.current_token.token == '{'):
                        self.get_next_token()
                        current_state = 1
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
                            pass
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
                            pass
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
                            current_state='fim'
                case 3: # verifica as opções de formação possivéis após blocos de registros
                    match(self.current_token.token):
                        case 'funcao':
                            self.funcao_listagem_funcoes()
                            current_state = 4
                        case 'principal':
                            self.funcao_principal()
                            current_state=5
                        case _:
                            current_state='fim'
                case 4: #verifica as opções de formação possivéis após declaração de funções
                    if(self.current_token.token == 'funcao'):
                        self.funcao_listagem_funcoes()
                        current_state=4
                    elif(self.current_token.token == 'principal'):
                        self.funcao_principal()
                        current_state=5
                    elif(self.current_token.token == '}'):
                        current_state=5
                case 5:
                    fim_producao = True
                case _:
                   fim_producao = True

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
                            current_state = 4
                        case _:
                            # como um bloco pode iniciar com varias opções
                            # o caso default passa para o estado de fomrção do bloco
                            current_state=3
                case 1:
                    # após formação de um bloco de constantes
                    match(self.current_token.token):
                        case 'variaveis':
                            self.funcao_bloco_variaveis()
                            current_state = 2
                        case 'retorno':
                            self.funcao_retorno()
                            current_state = 4
                        case _:
                            # como um bloco pode iniciar com varias opções
                            # o caso default passa para o estado de fomrção do bloco
                            current_state=3
                case 2:
                    # após formação de um bloco de variaveis
                    match(self.current_token.token):
                        case 'retorno':
                            self.funcao_retorno()
                            current_state = 4
                        case _:
                            # como um bloco pode iniciar com varias opções
                            # o caso default passa para o estado de fomrção do bloco
                            current_state=3
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
                case 6:
                    fim_producao = True
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
                            pass
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
                            if(self.current_token.code == 'PRE'):
                                pass
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
                    if(self.current_token.token in TIPOS):
                        current_state=1
                        self.get_next_token()
                case 1:
                     if(self.current_token.code == 'IDE'):
                        current_state=2
                        self.get_next_token()
                case 2:
                    if(self.current_token.token == '('):
                        self.funcao_listagem_parametros()
                        current_state=3
                case 3:
                    if(self.current_token.token == '{'):
                        current_state=4
                        self.get_next_token()
                case 4:
                    if(self.current_token.token == '}'):
                        current_state=5
                        self.get_next_token()
                case 5:
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
                case 1:
                    if(self.current_token.token == '{'):
                        current_state=2
                        self.get_next_token()
                case 2:
                    if(self.current_token.token == '}'):
                        current_state=3
                        self.get_next_token()
                case 3:
                    fim_producao=True
                case _:
                    pass
    
    #--------------------------------------------------------------------------------------
    ''' funções relacionadas ao bloco de constantes
    | função para declaração e listagem de constantes numericas
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
                case 1:
                    if(self.current_token.token == '='):
                        current_state= 2
                        self.get_next_token()
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
                case 1:
                    if(self.current_token.token == '='):
                        current_state= 2
                        self.get_next_token()
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
                case 1:
                    if(self.current_token.token == '='):
                        current_state= 2
                        self.get_next_token()
                case 2:
                    if(self.current_token.code == 'CAC'):
                        current_state = 3
                        self.get_next_token()
                case 3:
                    if(self.current_token.token == ';'):
                        current_state= 4
                        self.get_next_token()
                    elif(self.current_token.token ==','):
                        current_state =0
                        self.get_next_token()
                case 4:
                    fim_producao = True
                case _:
                    pass
    # função para declaração e listagem de constantes de cadeias de caracteres
    def funcao_declaracao_constantes_cadeia(self):
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
                case 1:
                    if(self.current_token.token == '='):
                        current_state= 2
                        self.get_next_token()
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
                            current_state = 1 # atribuição desnescessaria, remover depois
                        case _:
                            pass
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
                case 1:
                   self.funcao_formacao_expressao_numerica()
                   current_state=2
                case 2:
                     if(self.current_token.token == ']'):
                        current_state=3
                        self.get_next_token()
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
                case 1:
                    if(self.current_token.code =='IDE'):
                        current_state=2
                        self.get_next_token()
                case 2:
                    if(self.current_token.token =='['):
                        #chama a função de produção de vetor
                        self.funcao_formacao_vetor_matriz()
                        current_state=3
                        print('proximo token',self.current_token)
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
                case 2:
                    fim_producao=True
                case _:
                    pass    
    
    # função que analisa formação da formação do uso de um identificador,vetor,registro ou chamada defunção
    def funcao_formacao_ideVeRe_chamada(self):
        count = 0
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
                    elif(self.current_token == '('):
                        current_state=3
                    else:
                        current_state=7
                case 1:
                    # como é esperada uma expressão númerica
                    # faz a chamada para expressão númerica
                    self.funcao_formacao_expressao_numerica()
                    current_state=4
                case 2:
                    if(self.current_token.code == 'IDE'):
                        #finalizou a produção
                        self.get_next_token()
                        #retorna para o estado inicial
                        current_state= 6
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
                case 5:
                    if(self.current_token.token == ')'):
                        #finalizou a produção
                        self.get_next_token()
                        #volta para o inicio
                        current_state=6
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
                case 1:
                    if(self.current_token.token == ','):
                        current_state=0
                        self.get_next_token()
                    elif(self.current_token.token ==')'):
                        current_state=2
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
                case 2:
                    fim_producao
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
                            self.funcao_bloco_enquanto()
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
                        case _:
                            if(self.current_token.code =='IDE'):
                                #vai para o estado de reatribuuição
                                current_state=1
                case 1:
                    #chama a função de reatribuição
                    self.funcao_reatribuicao()
                    current_state=0
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
                # após abertura de parenteses
                case 3:
                     if(self.current_token.token == ')'):
                        self.get_next_token()
                        current_state=1
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
                        current_state=4
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
                        current_state=4
                case 3:
                    # após receber uma abertura de parnteses
                    # finalizada outra chamada de expressao numerica
                    if(self.current_token.token == ')'):
                      self.get_next_token()
                      current_state=2
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
                        print('passei aqui')
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
                    print('recebi o retorno')
                    current_state=3
                case 3:
                    # após receber uma expressão geral
                    # agora precisa ser o fecha parenteses
                    if(self.current_token.token == ')'):
                        self.get_next_token()
                        print('estou passando o token',self.current_token.token)
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
                      self.get_next_token()
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
                    print('cabou')
                case _:
                    pass
        print('encerrei a expresao geral')
        return None
   
   #--------------------------------------------------------------------------------------------------
    '''
    |   Funções relacionadas ao bloco
    |   se, enquanto,leia,escreva,reatribuição
    |
    '''
    # método que analisa a formação de um bloco se
    def funcao_se(self):
        pass
    
    # método que analisa a formação de um bloco senão
    def funcao_senao(self):
        pass
    #método que analisa a formação de um bloco enquanto
    def funcao_enquanto(self):
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
                case 1:
                    # chama o mesmo método de listagem de variaveis
                    self.funcao_listagem_parametros_leia()
                    current_state=2
                case 2:
                    if(self.current_token.token == ')'):
                        self.get_next_token()
                        current_state=3
                case 3:
                    if(self.current_token.token == ';'):
                        self.get_next_token()
                        current_state=4
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
                case 3:
                    if(self.current_token.token == ';'):
                        self.get_next_token()
                        current_state=4
                case 4:
                    fim_producao= True
                case _:
                    pass

    # método que analisa a formação de uma expressão de reatribuição
    def funcao_reatribuicao(self):
        pass

    # método executa a analise da formação da sintaxe do programa
    def proxima_producao(self):
        self.get_next_token()

        if( self.current_token.token == 'ALGORITMO'):
            self.funcao_algortimo()
    
    
a = analisador_sintatico()

a.token_list= a.read_tokens()
#print(a.token_list,'\n\n')
a.proxima_producao()
#a.get_next_token()


while(a.current_token !=None):
    print('nova funcao leia')
    a.funcao_escreva()
