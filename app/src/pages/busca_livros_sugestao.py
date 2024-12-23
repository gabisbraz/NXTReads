import flet as ft
import mysql.connector
from loguru import logger


class Livro:

    def __init__(self):
        """
        Inicializa a classe 'Livro' e estabelece conexão com o banco de dados.
        """
        self.connection = self.create_connection()

    def create_connection(self):
        """
        Cria a conexão com o banco de dados MySQL.
        """
        try:
            connection = mysql.connector.connect(
                host="database-1.ctj2rmaeyrwc.us-east-1.rds.amazonaws.com",
                user="admin",
                password="admin123",
                database="nxt_reads_db",
            )
            logger.info("Conexão estabelecida com sucesso!")
            return connection
        except mysql.connector.Error as err:
            logger.error(f"Erro ao conectar ao banco de dados: {err}")
            return None

    def search_books_by_title(self, title_part):
        """
        Busca livros pelo título parcial no banco de dados.
        """
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = (
                "SELECT bookID, title, authors FROM Livros WHERE title LIKE %s LIMIT 5"
            )
            cursor.execute(query, ("%" + title_part + "%",))
            books = cursor.fetchall()
            cursor.close()
            return books
        except mysql.connector.Error as err:
            logger.error(f"Erro ao buscar livros: {err}")
            return []


def busca_livros_sugestao(page: ft.Page):
    page.title = "Busca de Livros com Sugestões"
    page.window_width = 480
    page.window_height = 800

    # Campo de pesquisa com sugestão
    input_pesquisa = ft.TextField(
        label="Buscar livro pelo título",
        width=480,
        color="#000000",
        label_style=ft.TextStyle(color="#03103F"),
        border=ft.InputBorder.OUTLINE,
        border_radius=20,
        icon=ft.icons.SEARCH_ROUNDED,
        on_change=lambda e: buscar_sugestoes(
            e.control.value
        ),  # Executa busca ao digitar
        hint_text="Please enter text here",
    )

    # Container para mostrar as sugestões de livros
    sugestoes_container = ft.Column([])

    def buscar_sugestoes(search_term):
        """
        Função que busca e exibe sugestões de livros enquanto o usuário digita.
        """
        livro_instance = Livro()

        if len(search_term) < 2:
            sugestoes_container.controls.clear()
            page.update()
            return

        # Busca livros pelo título parcial
        livros_encontrados = livro_instance.search_books_by_title(search_term)

        # Limpa as sugestões anteriores
        sugestoes_container.controls.clear()

        if livros_encontrados:
            # Adiciona cada livro encontrado como uma sugestão clicável
            for livro in livros_encontrados:
                sugestoes_container.controls.append(
                    ft.ListTile(
                        title=ft.Text(livro["title"]),
                        subtitle=ft.Text(livro["authors"]),
                        on_click=lambda e, livro_id=livro["bookID"]: page.go(
                            f"/book/{livro_id}"
                        ),
                    )
                )
        else:
            sugestoes_container.controls.append(ft.Text("Nenhum livro encontrado."))

        page.update()

    # Layout da página
    content = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "Busque seu próximo livro", size=30, weight="bold", color="#03103F"
                ),
                input_pesquisa,  # Campo de pesquisa
                sugestoes_container,  # Container onde as sugestões serão exibidas
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=20,
        ),
        padding=ft.padding.all(20),
        bgcolor="#FFFFFF",
        width=480,
        height=800,
    )

    return content
