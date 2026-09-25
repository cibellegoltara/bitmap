import redis
from utils import conectar_redis


CHAVE_SEGURANCA = 'seguranca:cliente:7700:data:20250901'
MINIMO_DE_CHECAGENS = 4


def registrar_checagens(cliente):
    cliente.delete(CHAVE_SEGURANCA)

    for offset in (0, 1, 2):
        cliente.setbit(CHAVE_SEGURANCA, offset, 1)


def obter_resumo_seguranca(cliente):
    quantidade_de_checagens = cliente.bitcount(CHAVE_SEGURANCA)
    tamanho_em_bytes = cliente.strlen(CHAVE_SEGURANCA)

    return {
        'quantidade_de_checagens': quantidade_de_checagens,
        'pix_liberado': quantidade_de_checagens >= MINIMO_DE_CHECAGENS,
        'tamanho_em_bytes': tamanho_em_bytes,
    }


def executar_case(cliente):
    registrar_checagens(cliente)
    resumo = obter_resumo_seguranca(cliente)

    print(
        'Quantidade de checagens:',
        resumo['quantidade_de_checagens'],
    )
    print(
        'PIX de alto valor liberado:',
        resumo['pix_liberado'],
    )
    print(
        'Tamanho da string em bytes:',
        resumo['tamanho_em_bytes'],
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
