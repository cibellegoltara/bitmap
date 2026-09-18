import redis
from utils import conectar_redis

MES = 7
DIAS_NO_MES = 31
DIAS_PARA_ISENCAO = 15

def criar_chave_acessos(cliente_id):
    return f'acesso:cliente:{cliente_id}:mes{MES}'

def validar_dia(dia):
    if not 1 <= dia <= DIAS_NO_MES:
        raise ValueError(f'O dia deve estar entre 1 e {DIAS_NO_MES}.')

def registrar_acesso(cliente, cliente_id, dia):
    validar_dia(dia)
    chave = criar_chave_acessos(cliente_id)
    offset = dia - 1
    valor_anterior = cliente.setbit(chave, offset, 1)
    return valor_anterior == 0

def cliente_acessou_no_dia(cliente, cliente_id, dia):
    validar_dia(dia)
    chave = criar_chave_acessos(cliente_id)
    return bool(cliente.getbit(chave, dia - 1))

def obter_resumo_mensal(cliente, cliente_id):
    chave = criar_chave_acessos(cliente_id)
    dias_ativos = cliente.bitcount(chave)
    return {
        'dias_ativos': dias_ativos,
        'tem_isencao': dias_ativos >= DIAS_PARA_ISENCAO,
    }

def executar_menu(cliente):
    while True:
        print('\n--- MONITORAMENTO DE ACESSOS DE JULHO ---')
        print('1 - Registrar acesso')
        print('2 - Verificar acesso em um dia')
        print('3 - Consultar total de dias ativos e isenção')
        print('4 - Sair')
        opcao = input('Escolha uma opção: ')

        if opcao == '4':
            print('Tchau do Davi e Cibelle')
            break

        if opcao not in {'1', '2', '3'}:
            print('Opção inválida.')
            continue

        cliente_id = input('ID do cliente: ')

        try:
            if opcao == '1':
                dia = int(input('Dia do acesso em julho (1-31): '))
                novo_acesso = registrar_acesso(cliente, cliente_id, dia)
                if novo_acesso:
                    print(f'Acesso do dia {dia} registrado.')
                else:
                    print(f'O dia {dia} já estava registrado como ativo.')
            elif opcao == '2':
                dia = int(input('Dia de julho para verificar (1-31): '))
                acessou = cliente_acessou_no_dia(cliente, cliente_id, dia)
                print('Houve acesso nesse dia.' if acessou else 'Não houve acesso nesse dia.')
            else:
                resumo = obter_resumo_mensal(cliente, cliente_id)
                print(f'Dias ativos em julho: {resumo['dias_ativos']}')
                if resumo['tem_isencao']:
                    print('Cliente elegível à isenção da taxa.')
                else:
                    faltam = DIAS_PARA_ISENCAO - resumo['dias_ativos']
                    print(f'Sem isenção; faltam {faltam} dia(s) ativo(s).')
        except ValueError as ve:
            print(f'Entrada inválida: {ve}')


def main():
    cliente = conectar_redis()
    try:
        cliente.ping()
    except redis.RedisError as re:
        print(f'Não foi possível conectar ao Redis: {re}')
        print('Configure REDIS_URL no arquivo .env com a URL e credenciais do seu Redis.')
        return

    executar_menu(cliente)


if __name__ == '__main__':
    main()