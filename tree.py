import sqlite3
from database import setup


class Node_diretorio:
    def __init__(self, nome):
        self.nome = nome
        self.sub_diretorios = []
        self.arquivos = []


class sistema_arquivo:
    def __init__(self):
        setup()
        self.conn = sqlite3.connect('sistema_arquivos.db')

        self.raiz = Node_diretorio('/')
        self.atual = self.raiz
        self.historico = []

    def save_to_database(self):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM directories')
        cursor.execute('DELETE FROM files')
        self._save_directory(self.raiz, None, cursor)
        self.conn.commit()

    def _save_directory(self, directory, parent_id, cursor):
        cursor.execute(
            'INSERT INTO directories (name, parent_id) VALUES (?, ?)', (directory.nome, parent_id))
        directory_id = cursor.lastrowid

        for file in directory.arquivos:
            cursor.execute(
                'INSERT INTO files (name, directory_id) VALUES (?, ?)', (file, directory_id))

        for subdirectory in directory.sub_diretorios:
            self._save_directory(subdirectory, directory_id, cursor)

    def load_from_database(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM directories')
        rows = cursor.fetchall()
        self.raiz = self._load_directory(rows, None, cursor)

    def _load_directory(self, rows, parent_id, cursor):
        directories = [row for row in rows if row[2] == parent_id]
        directory_objects = []

        for directory_row in directories:
            directory = Node_diretorio(directory_row[1])
            directory_objects.append(directory)

            subdirectories = self._load_directory(
                rows, directory_row[0], cursor)
            directory.sub_diretorios.extend(subdirectories)

            cursor.execute(
                'SELECT name FROM files WHERE directory_id = ?', (directory_row[0],))
            files = cursor.fetchall()
            directory.arquivos.extend([file[0] for file in files])

        return directory_objects

    # Include other methods...

    def close_connection(self):
        self.conn.close()

# Your other class and method definitions...


    def ls(self):
        """
        função para listar os arquivos e diretorios daquela parte
        """
        print('Conteúdo de', self.atual.nome)
        for subdiretorio in self.atual.sub_diretorios:
            print('{}/ (diretorio)'.format(subdiretorio.nome))
        for arquivo in self.atual.arquivos:
            print('arquivo: {}'.format(arquivo))

    def cd(self, nome):
        """
        função para voltar um diretorio ou voltar 2
        """
        if nome == '..':
            self.mover_diretorio(1)
        elif nome == '../..':
            self.mover_diretorio(2)
        else:
            encontrado = False
            for subdiretorio in self.atual.sub_diretorios:
                if subdiretorio.nome.lower() == nome.lower():
                    self.historico.append(self.atual)
                    self.atual = subdiretorio
                    encontrado = True
                    break
            if not encontrado:
                print('diretório não encontrado')

    def mover_diretorio(self, nivel):
        """
        função usada para voltar os diretorios
        """
        if nivel == 0:
            return
        if nivel == 1:
            if self.historico:
                self.atual = self.historico.pop()
            else:
                print("Já está no diretório raiz")
        else:
            if self.historico:
                self.historico.pop()
                self.mover_diretorio(nivel - 1)
            else:
                print("Já está no diretório raiz")

    def mkdir(self, nome_pasta, dir=None, nivel=2):
        """
        função para criar pasta no diretorio atual ou especificando um caminho
        """
        if nivel == 2:
            caracter_especial = ['!', '@', '#', '$', '%', '^', '&', '*',
                                 '(', ')', '+', '-', '=', '{', '}', '[', ']', '|', ';', ':', "'", '"', ',', '.', '<', '>', '/', '?']
            if any(caracter in nome_pasta for caracter in caracter_especial):
                print(
                    'Nome de pasta não pode conter caracteres especiais. Exemplo: ! @ # / : >')
            elif nome_pasta:
                novo_diretorio = Node_diretorio(nome_pasta)
                self.atual.sub_diretorios.append(novo_diretorio)
                print('Pasta {} criada com sucesso em {}'.format(
                    nome_pasta, self.atual.nome))
        elif nivel == 3:
            caracter_especial = ['!', '@', '#', '$', '%', '^', '&', '*',
                                 '(', ')', '+', '-', '=', '{', '}', '[', ']', '|', ';', ':', "'", '"', ',', '.', '<', '>', '/', '?']
            if any(caracter in nome_pasta for caracter in caracter_especial):
                print(
                    'Nome de pasta não pode conter caracteres especiais. Exemplo: ! @ # / : >')
            elif dir:
                partes = dir.split('/')
                diretorio_atual = self.raiz
                for parte in partes:
                    encontrado = False
                    for subdiretorio in diretorio_atual.sub_diretorios:
                        if subdiretorio.nome.lower() == parte.lower():
                            diretorio_atual = subdiretorio
                            encontrado = True
                            break
                    if not encontrado:
                        print('Diretório {} não encontrado'.format(parte))
                        return
                novo_diretorio = Node_diretorio(nome_pasta)
                diretorio_atual.sub_diretorios.append(novo_diretorio)
                print('Pasta {} criada com sucesso em {}'.format(
                    nome_pasta, diretorio_atual.nome))
            else:
                print('Caminho não especificado')

    def touch(self, nome_arquivo):
        """
        função para criar arquivo
        """
        caracter_especial = ['!', '@', '#', '$', '%', '^', '&', '*',
                             '(', ')', '+', '-', '=', '{', '}', '[', ']', '|', ';', ':', "'", '"', ',', '<', '>', '/', '?']
        if any(caracter in nome_arquivo for caracter in caracter_especial):
            print(
                'Nome de pasta não pode conter caracteres especiais. Exemplo: ! @ # / : >')
        else:
            if nome_arquivo:
                self.atual.arquivos.append(nome_arquivo)
                print('Arquivo {} criado com sucesso' .format(nome_arquivo))
            else:
                pass

    def mv(self, nome_origem, novo_nome):
        """
        função para renomear arquivo
        """
        encontrado = False
        for i, arquivo in enumerate(self.atual.arquivos):
            if arquivo == nome_origem:
                self.atual.arquivos[i] = novo_nome
                print('Arquivo {} renomeado para {}'.format(
                    nome_origem, novo_nome))
                encontrado = True
                break
        if not encontrado:
            print('Arquivo não encontrado: {}'.format(nome_origem))

    def rm(self, nome_arquivo):
        """
        função para deletar arquivo
        """
        encontrado = False
        for arquivo in self.atual.arquivos:
            if arquivo == nome_arquivo:
                self.atual.arquivos.remove(arquivo)
                print('Arquivo {} removido'.format(nome_arquivo))
                encontrado = True
                break
        if not encontrado:
            print('Arquivo não encontrado: {}'.format(nome_arquivo))

    def print_tree(self, node, prefix=""):
        result = ""
        for subdir in node.sub_diretorios:
            result += prefix + "\n|-- " + subdir.nome + "/\n"
            result += self.print_tree(subdir, prefix + "|   ")
        for arquivo in node.arquivos:
            result += prefix + "|-- " + arquivo + "\n"
        return result

    def tree(self):
        print(self.atual.nome, '/')
        self.print_tree(self.atual)

    def execute_command(self, comando):
        output = []

        if comando == 'ls':
            output.append('\nConteúdo de ' + self.atual.nome)
            for subdiretorio in self.atual.sub_diretorios:
                output.append('{}/ (diretorio)'.format(subdiretorio.nome))
            for arquivo in self.atual.arquivos:
                output.append('arquivo: {}'.format(arquivo))

        elif comando.startswith('cd'):
            partes = comando.split()
            if len(partes) == 2:
                self.cd(partes[1].capitalize())
                output.append('\nMudou para diretório {}'.format(partes[1]))
            else:
                output.append('Uso: cd <diretorio>')

        elif comando.startswith('mkdir'):
            partes = comando.split()
            if len(partes) == 2:
                self.mkdir(partes[1].capitalize(), None, 2)
            elif len(partes) == 3:
                self.mkdir(partes[1].capitalize(),
                           partes[2].capitalize(), 3)
            else:
                output.append('Uso: mkdir <nome da pasta>')

        elif comando.startswith('touch'):
            partes = comando.split()
            if len(partes) == 2:
                self.touch(partes[1].capitalize())
            else:
                output.append('Uso: touch <nome do arquivo>')

        elif comando.startswith('mv'):
            partes = comando.split()
            if len(partes) == 3:
                self.mv(partes[1].capitalize(),
                        partes[2].capitalize())
            else:
                output.append(
                    'Uso: mv <nome do arquivo que quer alterar>  <nome do novo arquivo>')

        elif comando.startswith('rm'):
            partes = comando.split()
            if len(partes) == 2:
                self.rm(partes[1].capitalize())
            else:
                output.append('Uso: rm <nome do arquivo que quer excluir>')

        elif comando == 'tree':
            output.append(self.print_tree(self.atual, ''))

        elif comando == 'help':
            output.append("\nComandos:")
            output.append("ls | cd | mkdir | touch | mv | rm | tree | exit")

        elif comando == 'exit':
            output.append('Saindo do sistema')
            return output, True

        else:
            pass

        return "\n".join(output), False

    def run(self, sistema):
        print('Digite help para ver os comandos.')
        while True:
            comando = input('$ {} '.format(sistema.atual.nome))
            output, should_exit = self.execute_command(comando)
            print(output)
            if should_exit:
                break
