import redis
from utils import conectar_redis


CHAVE_PIX = 'pix:cliente:3300:semana1'
CHAVE_PUSH = 'push:cliente:3300:semana1'
CHAVE_INTERACAO = 'interacao:cliente:3300:semana1'

DIAS_DA_SEMANA = {
    0: 'Domingo',
    1: 'Segunda-feira',
    2: 'Terça-feira',
    3: 'Quarta-feira',
    4: 'Quinta-feira',
    5: 'Sexta-feira',
    6: 'Sábado',
}


def registrar_interacoes(cliente):
    cliente.delete(CHAVE_PIX, CHAVE_PUSH, CHAVE_INTERACAO)

    for offset in (2, 5):
        cliente.setbit(CHAVE_PIX, offset, 1)

    for offset in (1, 2, 4):
        cliente.setbit(CHAVE_PUSH, offset, 1)


def obter_dias_com_interacao(cliente):
    return [
        offset for offset in range(7)
        if cliente.getbit(CHAVE_INTERACAO, offset)
    ]


def executar_case(cliente):
    registrar_interacoes(cliente)

    cliente.bitop(
        'OR',
        CHAVE_INTERACAO,
        CHAVE_PIX,
        CHAVE_PUSH,
    )

    dias_com_interacao = obter_dias_com_interacao(cliente)

    print('Total de dias com Pix ou Push:', len(dias_com_interacao))
    print(
        'Dias com interação:',
        [DIAS_DA_SEMANA[dia] for dia in dias_com_interacao],
    )


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
