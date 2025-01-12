from setuptools import setup, find_packages

# Abrindo o arquivo README.md com a codificação UTF-8
long_description = open("README.md", encoding="utf-8").read()

setup(
    name="par_impar",  # Nome do seu módulo
    version="0.1",  # Versão do seu módulo
    packages=find_packages(),  # Encontra todos os pacotes do seu módulo
    install_requires=[],  # Dependências que seu módulo precisa
    long_description=long_description,  # Conteúdo do README
    long_description_content_type="text/markdown",  # Tipo do conteúdo (markdown)
    author="Seu Nome",  # Seu nome
    author_email="seuemail@example.com",  # Seu email
    description="Jogo de Par ou Ímpar em Python",  # Descrição do seu projeto
    url="https://github.com/seuusuario/par_impar",  # URL do repositório
)
