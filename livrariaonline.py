import datetime
import mysql.connector
import re

def conectar_bd():
    try:
        return mysql.connector.connect(
            host="localhost",   
            user="root",       
            password="",        
            port="3307",       
            database="Livraria"
        )
    except mysql.connector.Error as err:
        print(f"Erro ao conectar ao banco de dados: {err}")
        return None

def executar_query(query, params=None, fetch=False):
    try:
        conn = conectar_bd()
        if conn is None:
            return None
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            if fetch:
                result = cursor.fetchall()
                conn.close()
                return result
            else:
                conn.commit()
                conn.close()
    except mysql.connector.Error as err:
        print(f"Erro ao executar a query: {err}")
        return None

def validar_email(email):
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.fullmatch(regex, email))

def cadastrar_cliente():
    nome = input("Digite o nome do cliente: ")
    if not nome.strip():
        print("Erro: Nome não pode ser vazio.")
        return

    email = input("Digite o email do cliente: ")
    if not validar_email(email):
        print("Erro: Email inválido.")
        return

    query = "INSERT INTO CLIENTES (Nome, Email) VALUES (%s, %s)"
    if executar_query(query, (nome, email)):
        print(f"Cliente {nome} cadastrado com sucesso!")
    else:
        print("Erro ao cadastrar cliente.")

def listar_clientes():
    clientes = executar_query("SELECT * FROM CLIENTES", fetch=True)
    if clientes:
        for cliente in clientes:
            print(f"ID: {cliente[0]}, Nome: {cliente[1]}, Email: {cliente[2]}")
    else:
        print("Nenhum cliente cadastrado.")

def cadastrar_autor():
    nome = input("Digite o nome do autor: ")
    if not nome.strip():
        print("Erro: Nome não pode ser vazio.")
        return

    data_nascimento = input("Digite a data de nascimento do autor (AAAA-MM-DD): ")
    try:
        datetime.datetime.strptime(data_nascimento, '%Y-%m-%d')
    except ValueError:
        print("Erro: Formato de data inválido.")
        return

    nacionalidade = input("Digite a nacionalidade do autor: ")
    if not nacionalidade.strip():
        print("Erro: Nacionalidade não pode ser vazia.")
        return

    query = "INSERT INTO AUTORES (Nome, Data_Nascimento, Nacionalidade) VALUES (%s, %s, %s)"
    if executar_query(query, (nome, data_nascimento, nacionalidade)):
        print(f"Autor {nome} cadastrado com sucesso!")

def listar_autores():
    autores = executar_query("SELECT * FROM AUTORES", fetch=True)
    if autores:
        for autor in autores:
            print(f"ID: {autor[0]} | Nome: {autor[1]} | Nascimento: {autor[2]} | Nacionalidade: {autor[3]}")
    else:
        print("Nenhum autor cadastrado.")

def cadastrar_livro():
    titulo = input("Digite o título do livro: ")
    if not titulo.strip():
        print("Erro: O título não pode ser vazio.")
        return

    autor_id = input("Digite o ID do autor do livro: ")
    try:
        autor_id = int(autor_id)
    except ValueError:
        print("Erro: ID do autor deve ser um número.")
        return

    if not executar_query("SELECT * FROM AUTORES WHERE ID_Autor = %s", (autor_id,), fetch=True):
        print("Erro: Autor não encontrado.")
        return

    try:
        preco = float(input("Digite o preço do livro: "))
        estoque = int(input("Digite o estoque do livro: "))
        if preco <= 0 or estoque < 0:
            print("Erro: Preço deve ser positivo e estoque não pode ser negativo.")
            return
    except ValueError:
        print("Erro: Preço ou estoque inválido.")
        return

    query = "INSERT INTO LIVROS (Titulo, ID_Autor, Preco, Estoque) VALUES (%s, %s, %s, %s)"
    if executar_query(query, (titulo, autor_id, preco, estoque)):
        print(f"Livro '{titulo}' cadastrado com sucesso!")

def listar_livros():
    livros = executar_query("SELECT * FROM LIVROS", fetch=True)
    if livros:
        for livro in livros:
            print(f"ID: {livro[0]} | Título: {livro[1]} | Preço: R${livro[3]:.2f} | Estoque: {livro[4]}")
    else:
        print("Nenhum livro cadastrado.")

def realizar_pedido():
    cliente_id = input("Digite o ID do cliente: ")
    livro_id = input("Digite o ID do livro: ")
    quantidade = input("Digite a quantidade: ")

    try:
        cliente_id = int(cliente_id)
        livro_id = int(livro_id)
        quantidade = int(quantidade)
        if quantidade <= 0:
            print("Erro: Quantidade deve ser positiva.")
            return
    except ValueError:
        print("Erro: IDs e quantidade devem ser números inteiros.")
        return

    livro = executar_query("SELECT Estoque FROM LIVROS WHERE ID_Livro = %s", (livro_id,), fetch=True)
    if not livro or livro[0][0] < quantidade:
        print("Erro: Estoque insuficiente.")
        return

    query = "INSERT INTO PEDIDOS (ID_Cliente, ID_Livro, Quantidade, Status) VALUES (%s, %s, %s, 'Pendente')"
    if executar_query(query, (cliente_id, livro_id, quantidade)):
        print("Pedido realizado com sucesso!")

def listar_pedidos():
    pedidos = executar_query("SELECT * FROM PEDIDOS", fetch=True)
    if pedidos:
        for pedido in pedidos:
            print(f"ID: {pedido[0]}, Cliente: {pedido[1]}, Livro: {pedido[2]}, Status: {pedido[3]}")
    else:
        print("Nenhum pedido cadastrado.")

def deletar_item(table, id_name, item_id):
    query = f"DELETE FROM {table} WHERE {id_name} = %s"
    return executar_query(query, (item_id,))

def deletar_cliente():
    cliente_id = input("Digite o ID do cliente que deseja deletar: ")
    try:
        cliente_id = int(cliente_id)
        deletar_item("PEDIDOS", "ID_Cliente", cliente_id)
        if deletar_item("CLIENTES", "ID_Cliente", cliente_id):
            print(f"Cliente com ID {cliente_id} deletado com sucesso!")
        else:
            print("Erro ao deletar o cliente.")
    except ValueError:
        print("Erro: ID do cliente deve ser um número.")

def deletar_autor():
    autor_id = input("Digite o ID do autor que deseja deletar: ")
    try:
        autor_id = int(autor_id)
        deletar_item("LIVROS", "ID_Autor", autor_id)
        if deletar_item("AUTORES", "ID_Autor", autor_id):
            print(f"Autor com ID {autor_id} deletado com sucesso!")
        else:
            print("Erro ao deletar o autor.")
    except ValueError:
        print("Erro: ID do autor deve ser um número.")

def deletar_livro():
    livro_id = input("Digite o ID do livro que deseja deletar: ")
    try:
        livro_id = int(livro_id)
        if deletar_item("LIVROS", "ID_Livro", livro_id):
            print(f"Livro com ID {livro_id} deletado com sucesso!")
        else:
            print("Erro ao deletar o livro.")
    except ValueError:
        print("Erro: ID do livro deve ser um número.")

def deletar_pedido():
    pedido_id = input("Digite o ID do pedido que deseja deletar: ")
    try:
        pedido_id = int(pedido_id)
        if deletar_item("PEDIDOS", "ID_Pedido", pedido_id):
            print(f"Pedido com ID {pedido_id} deletado com sucesso!")
        else:
            print("Erro ao deletar o pedido.")
    except ValueError:
        print("Erro: ID do pedido deve ser um número.")

def autenticar_usuario():
    usuario_validado = "book"
    senha_validada = "1234"
    
    print("Bem-vindo ao sistema de Livraria")
    tentativas = 3  
    for _ in range(tentativas):
        usuario = input("Digite o nome de usuário: ")
        senha = input("Digite a senha: ")

        if usuario == usuario_validado and senha == senha_validada:
            print("\nAcesso concedido!")
            return True
        else:
            print("\nCredenciais inválidas. Tente novamente.")
    print("Número máximo de tentativas alcançado. Saindo...")
    return False

def modificar_status_pedido():
    pedido_id = input("Digite o ID do pedido que deseja modificar: ")
    try:
        pedido_id = int(pedido_id)
    except ValueError:
        print("Erro: ID do pedido deve ser um número inteiro.")
        return

    novo_status = input("Digite o novo status do pedido (Pendente, Em Processamento, Enviado, Entregue): ")


    if novo_status not in ['Pendente', 'Em Processamento', 'Enviado', 'Entregue']:
        print("Erro: Status inválido. Escolha entre 'Pendente', 'Em Processamento', 'Enviado', 'Entregue'.")
        return

    query = """
        UPDATE PEDIDOS 
        SET Status = %s 
        WHERE ID_Pedido = %s
    """
    executar_query(query, (novo_status, pedido_id))
    print(f"Status do pedido com ID {pedido_id} alterado para '{novo_status}'.")


def menu():
    while True:
        print("\n--- Menu da Livraria ---")
        print("1. Cadastrar Cliente")
        print("2. Listar Clientes")
        print("3. Deletar Cliente")
        print("4. Cadastrar Autor")
        print("5. Listar Autores")
        print("6. Deletar Autor")
        print("7. Cadastrar Livro")
        print("8. Listar Livros")  
        print("9. Deletar Livro")
        print("10. Realizar Pedido")
        print("11. Listar Pedidos")
        print("12. Deletar Pedido")
        print("13. Modificar Status de Pedido")
        print("0. Sair")
        
        opcao = input("\nEscolha uma opção: ")
        
        if opcao == "1":
            cadastrar_cliente()
        elif opcao == "2":
            listar_clientes()
        elif opcao == "3":
            deletar_cliente()
        elif opcao == "4":
            cadastrar_autor()
        elif opcao == "5":
            listar_autores()
        elif opcao == "6":
            deletar_autor()
        elif opcao == "7":
            cadastrar_livro()
        elif opcao == "8":
            listar_livros()
        elif opcao == "9":
            deletar_livro()
        elif opcao == "10":
            realizar_pedido()
        elif opcao == "11":
            listar_pedidos()
        elif opcao == "12":
            deletar_pedido()
        elif opcao == "13":
            modificar_status_pedido()
        elif opcao == "0":
            print("Saindo... Até logo!")
            break
        else:
            print("Opção inválida. Tente novamente.")

if autenticar_usuario():
    menu() 
