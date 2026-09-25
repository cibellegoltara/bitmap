import redis
from utils import conectar_redis

CHAVE_DEBITO = 'cartao:debito:cliente:8820:mes8'
CHAVE_CREDITO = 'cartao:credito:cliente:8820:mes8'
CHAVE_AMBOS = 'cartao:ambos:cliente:8820:mes8'
CHAVE_EXCLUSIVO = 'cartao:exclusivo:cliente:8820:mes8'

def registrar_utilizacoes(cliente):
    cliente.delete(CHAVE_DEBITO, CHAVE_CREDITO, CHAVE_AMBOS, CHAVE_EXCLUSIVO)

    for dia in (2, 10):
        cliente.setbit(CHAVE_DEBITO, dia - 1, 1)

    for dia in (10, 20):
        cliente.setbit(CHAVE_CREDITO, dia - 1, 1)

def obter_resumo_utilizacao(cliente):
    cliente.bitop('AND', CHAVE_AMBOS, CHAVE_DEBITO, CHAVE_CREDITO)
    cliente.bitop('XOR', CHAVE_EXCLUSIVO, CHAVE_DEBITO, CHAVE_CREDITO)

    return {
        'dias_com_ambas': cliente.bitcount(CHAVE_AMBOS),
        'dias_com_apenas_uma': cliente.bitcount(CHAVE_EXCLUSIVO),
    }

def executar_case(cliente):
    registrar_utilizacoes(cliente)
    resumo = obter_resumo_utilizacao(cliente)

    print('Dias em que o cliente usou débito e crédito:', resumo['dias_com_ambas'],)
    print('Dias em que o cliente usou apenas uma modalidade:', resumo['dias_com_apenas_uma'])

def main():
    cliente = conectar_redis()

    try:
        cliente.ping()
    except redis.RedisError as erro:
        print(f'Não foi possível conectar ao Redis: {erro}')
        return

    executar_case(cliente)

if __name__ == '__main__':
    main()