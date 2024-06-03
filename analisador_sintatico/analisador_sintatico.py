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
                        case tipo if tipo in TIPOS:
                            self.funcao_listagem_funcoes()
                            current_state = 'fim'
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
                        case tipo if tipo in TIPOS:
                            self.funcao_listagem_funcoes()
                            current_state = 'fim'
                        case _:
                            pass
                case 2:#verifica as opções de formação possiveis após um bloco de variavies
                    match(self.current_token.token):
                        case 'registro':
                            self.funcao_registro()
                            current_state = 2
                        case tipo if tipo in TIPOS:
                            self.funcao_listagem_funcoes()
                            current_state = 3
                        case _:
                            current_state='fim'
                case 3: # verifica as opções de formação possivéis após blocos de registros
                    match(self.current_token.token):
                        case tipo if tipo in TIPOS:
                            self.funcao_listagem_funcoes()
                            current_state = 3
                        case _:
                            current_state='fim'
                case 4: #verifica as opções de formação possivéis após declaração de funções
                    pass
                case 5:
                    fim_producao = True
                case _:
                   fim_producao = True
           
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
                            self.funcao_declaracao_constantes_inteiras()
                        case 'real':
                            self.funcao_declaracao_constantes_reais()
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
        # atualiza para o proximo token, elimina 'tipo de retorno'
        self.get_next_token()

        while(self.current_token != None and not fim_producao):
            match(current_state):
                case 0:
                    if(self.current_token.code == 'IDE'):
                        current_state=1
                        self.get_next_token()
                case 1:
                    if(self.current_token.token == '('):
                        self.funcao_listagem_parametros()
                        current_state=2
                case 2:
                    if(self.current_token.token == '{'):
                        current_state=3
                        self.get_next_token()
                case 3:
                    if(self.current_token.token == '}'):
                        current_state=4
                        self.get_next_token()
                case 4:
                    fim_producao=True
                case _:
                    pass

    # função para analisar formação da declarção da função principal
    def funcao_principal(self):
        pass
    
    #--------------------------------------------------------------------------------------
    ''' funções relacionadas ao bloco de constantes
    | função para declaração e listagem de constantes inteiras
    | existe a possibilidade juntar todas estas funções em uma unica
    | mas deixo para depois
    '''
    def funcao_declaracao_constantes_inteiras(self):
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
                    if(self.current_token.code == 'NRO'):
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
    # função para declaração e listagem de constantes reais
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
                    if(self.current_token.code == 'NRO'):
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
        
    # função para declaração e listagem de constantes de caracteres
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
                    if(self.current_token.token == 'verdadeiro' or self.current_token.token == 'falso'):
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
                    if(self.current_token.code == 'IDE' or self.current_token.code == 'NRO'):
                        current_state=2
                        self.get_next_token()
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
    # função que anaçisa formação da listagem de parametros de uma função
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
                        current_state=3
                        self.get_next_token()
                case 1:
                    if(self.current_token.code =='IDE'):
                        current_state=2
                        self.get_next_token()
                case 2:
                    if(self.current_token.token ==')'):
                        current_state=3
                        self.get_next_token()
                    elif(self.current_token.token == ','):
                        current_state=0
                        self.get_next_token()
                case 3:
                    fim_producao=True
                case _:
                    pass
    #----------------------------------------------------------------------------------------------------
   
   
   # método executa a analise da formação da sintaxe do programa
    def proxima_producao(self):
        self.get_next_token()

        if( self.current_token.token == 'ALGORITMO'):
            self.funcao_algortimo()

a = analisador_sintatico()

a.token_list= a.read_tokens()
#print(a.token_list,'\n\n')
a.proxima_producao()