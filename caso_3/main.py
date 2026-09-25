import redis
from utils import conectar_redis


def criar_chaves():
    return {
        'alfa': 'permissoes:pj:1001',
        'beta': 'permissoes:pj:1002',
        'comuns': 'permissoes:pj:comuns',
        'nao_contratados': 'permissoes:pj:nao_contratados',
    }


def registrar_permissoes(cliente, chaves):
    cliente.delete(*chaves.values())

    for offset in (0, 1, 3, 5):
        cliente.setbit(chaves['alfa'], offset, 1)

    for offset in (0, 1, 2, 4):
        cliente.setbit(chaves['beta'], offset, 1)


def obter_offsets_ativos(cliente, chave):
    return [
        offset for offset in range(7)
        if cliente.getbit(chave, offset)
    ]


def executar_case(cliente):
    chaves = criar_chaves()
    registrar_permissoes(cliente, chaves)

    cliente.bitop(
        'AND',
        chaves['comuns'],
        chaves['alfa'],
        chaves['beta'],
    )
    cliente.bitop(
        'NOT',
        chaves['nao_contratados'],
        chaves['alfa'],
    )

    permissoes_comuns = obter_offsets_ativos(
        cliente,
        chaves['comuns'],
    )
    modulos_nao_contratados = obter_offsets_ativos(
        cliente,
        chaves['nao_contratados'],
    )

    print('Permissões comuns:', permissoes_comuns)
    print(
        'Módulos não contratados pela Alfa Tech:',
        modulos_nao_contratados,
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
