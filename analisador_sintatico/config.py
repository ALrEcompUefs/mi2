OP_LOGIC_ONE_CHAR_SET = set(['!','&', '|'])
OP_RELATIONAL_ONE_CHAR_SET = set(['<','>','='])
OP_ARITIMETIC_ONE_CHAR_SET = set(['+','-','*',"/"])
DELIMETER_CHAR_SET = set(['.', '{' , '}' , ';' , ',' , '(' , ')' ,']','['])
RESERVED_WORDS = set(['algoritmo', 'principal', 'variaveis','constantes', 'registro', 'funcao','retorno', 'vazio', 'se', 'senao', 'enquanto','leia', 'escreva', 'inteiro', 'real', 'booleano','char', 'cadeia', 'verdadeiro', 'falso'])
STOP_ERRORS = set(['!','&','|','=','>','<','+','-','*','/','.','{','}',';','(',')',']','[',','])
TIPOS = set(['booleano','inteiro','real','char','cadeia','vazio'])
ASCII = set(chr(i) for i in range(32, 127) if i != 34)


REGEX_BLOCK_COMMENT_PATTERN = r'/\*.*?\*/'

END_COMMENT_BLOCK_PATTER = r'^.*\*/'