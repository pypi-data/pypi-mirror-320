import os
import re
from typing import List, Tuple, Dict
from urllib.parse import urljoin
import requests
from colorama import Fore, Style
from .exeptions import M3u8Error, M3u8NetworkingError, M3u8FileError

__author__ = 'PauloCesar0073-dev404'


class M3u8Analyzer:
    def __init__(self):
        """
         análise e manipulação de streams M3U8 de maneira bruta
        """
        pass

    @staticmethod
    def get_m3u8(url_m3u8: str, headers: dict = None, save_in_file=None, timeout: int = None):
        """
        Obtém o conteúdo de um arquivo M3U8 a partir de uma URL HLS.

        Este método permite acessar, visualizar ou salvar playlists M3U8 utilizadas em transmissões de vídeo sob
        demanda.

        Args: url_m3u8 (str): A URL do arquivo M3U8 que você deseja acessar. headers (dict, optional): Cabeçalhos
        HTTP opcionais para a requisição. Se não forem fornecidos, serão usados cabeçalhos padrão. save_in_file (str,
        optional): Nome do arquivo para salvar o conteúdo M3U8. Se fornecido, o conteúdo da playlist será salvo no
        diretório atual com a extensão `.m3u8`. timeout (int, optional): Tempo máximo (em segundos) para aguardar uma
        resposta do servidor. O padrão é 20 segundos.

        Returns:
            str: O conteúdo do arquivo M3U8 como uma string se a requisição for bem-sucedida.
            None: Se a requisição falhar ou se o servidor não responder com sucesso.

        Raises:
            ValueError: Se a URL não for válida ou se os headers não forem um dicionário.
            ConnectionAbortedError: Se o servidor encerrar a conexão inesperadamente.
            ConnectionRefusedError: Se a conexão for recusada pelo servidor.
            TimeoutError: Se o tempo de espera pela resposta do servidor for excedido.
            ConnectionError: Se não for possível se conectar ao servidor por outros motivos.

        Example:
            ```python
            from m3u8_analyzer import M3u8Analyzer

            url = "https://example.com/playlist.m3u8"
            headers = {"User-Agent": "Mozilla/5.0"}
            playlist_content = M3u8Analyzer.get_m3u8(url, headers=headers, save_in_file="minha_playlist", timeout=30)

            if playlist_content:
                print("Playlist obtida com sucesso!")
            else:
                print("Falha ao obter a playlist.")
            ```
        """

        if headers:
            if not isinstance(headers, dict):
                raise M3u8Error("headers deve ser um dicionário válido!", errors=['headers not dict'])
        if not (url_m3u8.startswith('https://') or url_m3u8.startswith('http://')):
            raise M3u8Error(f"Este valor não se parece ser uma url válida!")
        try:
            time = 20
            respo = ''
            headers_default = {
                "Accept": "application/json, text/plain, */*",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
                "Content-Length": "583",
                "Content-Type": "text/plain",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Ch-Ua": "\"Not:A-Brand\";v=\"99\", \"Google Chrome\";v=\"118\", \"Chromium\";v=\"118\"",
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": "\"Windows\"",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/118.0.0.0 Safari/537.36"
            }
            session = requests.session()
            if timeout:
                time = timeout
                if not headers:
                    headers = headers_default
            r = session.get(url_m3u8, timeout=time, headers=headers)
            if r.status_code == 200:
                # Verificar o conteúdo do arquivo
                if not "#EXTM3U" in r.text:
                    raise M3u8Error("A URL fornecida não parece ser um arquivo M3U8 válido.")
                elif "#EXTM3U" in r.text:
                    if save_in_file:
                        local = os.getcwd()
                        with open(fr"{local}\{save_in_file}.m3u8", 'a', encoding='utf-8') as e:
                            e.write(r.text)
                    return r.text
                else:
                    return None
            else:
                return "NULL"
        except requests.exceptions.SSLError as e:
            raise M3u8NetworkingError(f"Erro SSL: {e}")
        except requests.exceptions.ProxyError as e:
            raise M3u8NetworkingError(f"Erro de proxy: {e}")
        except requests.exceptions.ConnectionError:
            raise M3u8NetworkingError("Erro: O servidor ou o servidor encerrou a conexão.")
        except requests.exceptions.HTTPError as e:
            raise M3u8NetworkingError(f"Erro HTTP: {e}")
        except requests.exceptions.Timeout:
            raise M3u8NetworkingError("Erro de tempo esgotado: A conexão com o servidor demorou muito para responder.")
        except requests.exceptions.TooManyRedirects:
            raise M3u8NetworkingError("Erro de redirecionamento: Muitos redirecionamentos.")
        except requests.exceptions.URLRequired:
            raise M3u8NetworkingError("Erro: URL é necessária para a solicitação.")
        except requests.exceptions.InvalidProxyURL as e:
            raise M3u8NetworkingError(f"Erro: URL de proxy inválida: {e}")
        except requests.exceptions.InvalidURL:
            raise M3u8NetworkingError("Erro: URL inválida fornecida.")
        except requests.exceptions.InvalidSchema:
            raise M3u8NetworkingError("Erro: URL inválida, esquema não suportado.")
        except requests.exceptions.MissingSchema:
            raise M3u8NetworkingError("Erro: URL inválida, esquema ausente.")
        except requests.exceptions.InvalidHeader as e:
            raise M3u8NetworkingError(f"Erro de cabeçalho inválido: {e}")
        except requests.exceptions.ChunkedEncodingError as e:
            raise M3u8NetworkingError(f"Erro de codificação em partes: {e}")
        except requests.exceptions.ContentDecodingError as e:
            raise M3u8NetworkingError(f"Erro de decodificação de conteúdo: {e}")
        except requests.exceptions.StreamConsumedError:
            raise M3u8NetworkingError("Erro: Fluxo de resposta já consumido.")
        except requests.exceptions.RetryError as e:
            raise M3u8NetworkingError(f"Erro de tentativa: {e}")
        except requests.exceptions.UnrewindableBodyError:
            raise M3u8NetworkingError("Erro: Corpo da solicitação não pode ser rebobinado.")
        except requests.exceptions.RequestException as e:
            raise M3u8NetworkingError(f"Erro de conexão: Não foi possível se conectar ao servidor. Detalhes: {e}")
        except requests.exceptions.BaseHTTPError as e:
            raise M3u8NetworkingError(f"Erro HTTP básico: {e}")

    @staticmethod
    def get_high_resolution(m3u8_content: str):
        """
        Obtém a maior resolução disponível em um arquivo M3U8 e o URL correspondente.

        Este método analisa o conteúdo de um arquivo M3U8 para identificar a maior resolução
        disponível entre os fluxos de vídeo listados. Também retorna o URL associado a essa
        maior resolução, se disponível.

        Args:
            m3u8_content (str): O conteúdo do arquivo M3U8 como uma string. Este conteúdo deve
                                incluir as tags e atributos típicos de uma playlist HLS.

        Returns:
            tuple: Uma tupla contendo:
                - str: A maior resolução disponível no formato 'Largura x Altura' (ex.: '1920x1080').
                - str: O URL correspondente à maior resolução. Se o URL não for encontrado,
                       retorna None.
                Se o tipo de playlist não contiver resoluções, retorna uma mensagem indicando
                o tipo de playlist.

        Raises:
            ValueError: Se o conteúdo do M3U8 não contiver resoluções e a função não conseguir
                        determinar o tipo de playlist.

        Examples:
            ```python
            m3u8_content = '''
            #EXTM3U
            #EXT-X-STREAM-INF:BANDWIDTH=500000,RESOLUTION=640x360
            http://example.com/360p.m3u8
            #EXT-X-STREAM-INF:BANDWIDTH=1000000,RESOLUTION=1280x720
            http://example.com/720p.m3u8
            #EXT-X-STREAM-INF:BANDWIDTH=3000000,RESOLUTION=1920x1080
            http://example.com/1080p.m3u8
            '''
            result = M3u8Analyzer.get_high_resolution(m3u8_content)
            print(result)  # Saída esperada: ('1920x1080', 'http://example.com/1080p.m3u8')
            ```

            ```python
            m3u8_content_no_resolutions = '''
            #EXTM3U
            #EXT-X-STREAM-INF:BANDWIDTH=500000
            http://example.com/360p.m3u8
            '''
            result = M3u8Analyzer.get_high_resolution(m3u8_content_no_resolutions)
            print(result)  # Saída esperada: 'Playlist type: <TIPO DA PLAYLIST> not resolutions...'
            ```
        """
        resolutions = re.findall(r'RESOLUTION=(\d+x\d+)', m3u8_content)
        if not resolutions:
            tip = M3u8Analyzer.get_type_m3u8_content(m3u8_content=m3u8_content)
            return f"Playlist type: {Fore.LIGHTRED_EX}{tip}{Style.RESET_ALL} not resolutions..."
        max_resolution = max(resolutions, key=lambda res: int(res.split('x')[0]) * int(res.split('x')[1]))
        url = re.search(rf'#EXT-X-STREAM-INF:[^\n]*RESOLUTION={max_resolution}[^\n]*\n([^\n]+)', m3u8_content).group(1)
        if not url:
            return max_resolution, None
        if not max_resolution:
            return None, url
        else:
            return max_resolution, url

    @staticmethod
    def get_type_m3u8_content(m3u8_content: str) -> str:
        """
        Determina o tipo de conteúdo de um arquivo M3U8 (Master ou Segmentos).

        Este método analisa o conteúdo de um arquivo M3U8 para identificar se ele é do tipo
        'Master', 'Master encrypted', 'Segments', 'Segments encrypted', 'Segments Master', ou
        'Desconhecido'. A identificação é baseada na presença de tags e chaves específicas no
        conteúdo da playlist M3U8.

        Args:
            m3u8_content (str): O conteúdo do arquivo M3U8 como uma string. Pode ser uma URL ou o
                                próprio conteúdo da playlist.

        Returns:
            str: O tipo de conteúdo identificado. Os possíveis valores são:
                - 'Master': Playlist mestre sem criptografia.
                - 'Master encrypted': Playlist mestre com criptografia.
                - 'Segments': Playlist de segmentos sem criptografia.
                - 'Segments encrypted': Playlist de segmentos com criptografia.
                - 'Segments .ts': Playlist de segmentos com URLs terminando em '.ts'.
                - 'Segments .m4s': Playlist de segmentos com URLs terminando em '.m4s'.
                - 'Segments Master': Playlist de segmentos com URLs variadas.
                - 'Desconhecido': Se o tipo não puder ser identificado.

        Examples:
            ```python
            m3u8_content_master = '''
            #EXTM3U
            #EXT-X-STREAM-INF:BANDWIDTH=500000
            http://example.com/master.m3u8
            '''
            result = M3u8Analyzer.get_type_m3u8_content(m3u8_content_master)
            print(result)  # Saída esperada: 'Master'

            m3u8_content_master_encrypted = '''
            #EXTM3U
            #EXT-X-STREAM-INF:BANDWIDTH=500000
            #EXT-X-KEY:METHOD=AES-128,URI="http://example.com/key.key"
            http://example.com/master.m3u8
            '''
            result = M3u8Analyzer.get_type_m3u8_content(m3u8_content_master_encrypted)
            print(result)  # Saída esperada: 'Master encrypted'

            m3u8_content_segments = '''
            #EXTM3U
            #EXTINF:10,
            http://example.com/segment1.ts
            #EXTINF:10,
            http://example.com/segment2.ts
            '''
            result = M3u8Analyzer.get_type_m3u8_content(m3u8_content_segments)
            print(result)  # Saída esperada: 'Segments .ts'

            m3u8_content_unknown = '''
            #EXTM3U
            #EXTINF:10,
            http://example.com/unknown_segment
            '''
            result = M3u8Analyzer.get_type_m3u8_content(m3u8_content_unknown)
            print(result)  # Saída esperada: 'Segments Master'
            ```

        Raises:
            Exception: Em caso de erro durante o processamento do conteúdo, o método retornará uma
                       mensagem de erro descritiva.
        """
        try:
            conteudo = m3u8_content
            if '#EXT-X-STREAM-INF' in conteudo:
                if '#EXT-X-KEY' in conteudo:
                    return 'Master encrypted'
                else:
                    return 'Master'
            elif '#EXTINF' in conteudo:
                if '#EXT-X-KEY' in conteudo:
                    return 'Segments encrypted'
                else:
                    # Verifica se URLs dos segmentos possuem a extensão .ts ou .m4s
                    segment_urls = re.findall(r'#EXTINF:[0-9.]+,\n([^\n]+)', conteudo)
                    if all(url.endswith('.ts') for url in segment_urls):
                        return 'Segments .ts'
                    elif all(url.endswith('.m4s') for url in segment_urls):
                        return 'Segments .m4s'
                    else:
                        return 'Segments Master'
            else:
                return 'Desconhecido'
        except re.error as e:
            raise M3u8FileError(f"Erro ao processar o conteúdo M3U8: {str(e)}")
        except Exception as e:
            raise M3u8FileError(f"Erro inesperado ao processar o conteúdo M3U8: {str(e)}")

    @staticmethod
    def get_player_playlist(m3u8_url: str) -> str:
        """
        Obtém o caminho do diretório base do arquivo M3U8, excluindo o nome do arquivo.

        Este método analisa a URL fornecida do arquivo M3U8 e retorna o caminho do diretório onde o arquivo M3U8 está localizado.
        A URL deve ser uma URL completa e o método irá extrair o caminho do diretório base.

        Args:
            m3u8_url (str): A URL completa do arquivo M3U8. Pode incluir o nome do arquivo e o caminho do diretório.

        Returns:
            str: O caminho do diretório onde o arquivo M3U8 está localizado. Se a URL não contiver um arquivo M3U8,
                 retornará uma string vazia.

        Examples:
            ```python
            # Exemplo 1
            url = 'http://example.com/videos/playlist.m3u8'
            path = M3u8Analyzer.get_player_playlist(url)
            print(path)  # Saída esperada: 'http://example.com/videos/'

            # Exemplo 2
            url = 'https://cdn.example.com/streams/segment.m3u8'
            path = M3u8Analyzer.get_player_playlist(url)
            print(path)  # Saída esperada: 'https://cdn.example.com/streams/'

            # Exemplo 3
            url = 'https://example.com/playlist.m3u8'
            path = M3u8Analyzer.get_player_playlist(url)
            print(path)  # Saída esperada: 'https://example.com/'

            # Exemplo 4
            url = 'https://example.com/videos/'
            path = M3u8Analyzer.get_player_playlist(url)
            print(path)  # Saída esperada: ''
            ```

        """
        if m3u8_url.endswith('/'):
            m3u8_url = m3u8_url[:-1]
        partes = m3u8_url.split('/')
        for i, parte in enumerate(partes):
            if '.m3u8' in parte:
                return '/'.join(partes[:i]) + "/"
        return ''

    @staticmethod
    def get_audio_playlist(m3u8_content: str):
        """
        Extrai o URL da playlist de áudio de um conteúdo M3U8.

        Este método analisa o conteúdo fornecido de um arquivo M3U8 e retorna o URL da playlist de áudio incluída na playlist M3U8.
        O método busca a linha que contém a chave `#EXT-X-MEDIA` e extrai a URL associada ao áudio.

        Args:
            m3u8_content (str): Conteúdo da playlist M3U8 como uma string. Deve incluir informações sobre áudio se disponíveis.

        Returns:
            str: URL da playlist de áudio encontrada no conteúdo M3U8. Retorna `None` se a URL da playlist de áudio não for encontrada.

        Examples:
            ```python
            # Exemplo 1
            content = '''
            #EXTM3U
            #EXT-X-VERSION:3
            #EXT-X-MEDIA:TYPE=AUDIO,GROUP-ID="audio",NAME="English",DEFAULT=YES,URI="http://example.com/audio.m3u8"
            #EXT-X-STREAM-INF:BANDWIDTH=256000,AUDIO="audio"
            http://example.com/stream.m3u8
            '''
            url = M3u8Analyzer.get_audio_playlist(content)
            print(url)  # Saída esperada: 'http://example.com/audio.m3u8'

            # Exemplo 2
            content = '''
            #EXTM3U
            #EXT-X-VERSION:3
            #EXT-X-MEDIA:TYPE=AUDIO,GROUP-ID="audio",NAME="French",DEFAULT=NO,URI="http://example.com/french_audio.m3u8"
            #EXT-X-STREAM-INF:BANDWIDTH=256000,AUDIO="audio"
            http://example.com/stream.m3u8
            '''
            url = M3u8Analyzer.get_audio_playlist(content)
            print(url)  # Saída esperada: 'http://example.com/french_audio.m3u8'

            # Exemplo 3
            content = '''
            #EXTM3U
            #EXT-X-VERSION:3
            #EXT-X-STREAM-INF:BANDWIDTH=256000
            http://example.com/stream.m3u8
            '''
            url = M3u8Analyzer.get_audio_playlist(content)
            print(url)  # Saída esperada: None
            ```

        """
        match = re.search(r'#EXT-X-MEDIA:.*URI="([^"]+)"(?:.*,IV=(0x[0-9A-Fa-f]+))?', m3u8_content)
        if match:
            return match.group(1)
        return None

    @staticmethod
    def get_segments(content: str, base_url: str) -> Dict[str, List[Tuple[str, str]]]:
        """
            Extrai URLs de segmentos de uma playlist M3U8 e fornece informações detalhadas sobre os segmentos.

            Este método analisa o conteúdo de uma playlist M3U8 para extrair URLs de segmentos, identificar resoluções associadas,
            e retornar um dicionário com informações sobre as URLs dos segmentos, a quantidade total de segmentos,
            e a ordem de cada URI. Completa URLs relativas com base na URL base da playlist.

            Args:
                content (str): Conteúdo da playlist M3U8 como uma string.
                base_url (str): A URL base da playlist M3U8 para completar os caminhos relativos dos segmentos.

            Returns:
                dict: Um dicionário com as seguintes chaves:
                    - 'uris' (List[str]): Lista de URLs dos segmentos.
                    - 'urls' (List[str]): Lista de URLs de stream extraídas do conteúdo.
                    - 'len' (int): Contagem total de URLs de stream encontradas.
                    - 'enumerated_uris' (List[Tuple[int, str]]): Lista de tuplas contendo a ordem e o URL de cada segmento.
                    - 'resolutions' (Dict[str, str]): Dicionário mapeando resoluções para suas URLs correspondentes.
                    - 'codecs' (List[str]): Lista de codecs identificados nas streams.

            Raises:
                ValueError: Se o conteúdo fornecido for uma URL em vez de uma string de conteúdo M3U8.
            """
        url_pattern = re.compile(r'^https?://', re.IGNORECASE)

        if url_pattern.match(content):
            raise ValueError("O conteúdo não deve ser uma URL, mas sim uma string de uma playlist M3U8.")

        if content == "NULL":
            raise ValueError("essa url não é de uma playlist m3u8!")

        # Separação das linhas da playlist, ignorando linhas vazias e comentários
        urls_segmentos = [linha for linha in content.splitlines() if linha and not linha.startswith('#')]

        # Completa as URLs relativas usando a base_url
        full_urls = [urljoin(base_url, url) for url in urls_segmentos]

        # Inicializa o dicionário para armazenar os dados dos segmentos
        data_segments = {
            'uris': full_urls,  # Armazena as URLs completas
            'urls': [],
            'len': 0,
            'enumerated_uris': [(index + 1, url) for index, url in enumerate(full_urls)],
            'resolutions': {},
            'codecs': []
        }

        # Busca por resoluções na playlist e armazena suas URLs correspondentes
        resolution_pattern = r'RESOLUTION=(\d+x\d+)'
        resolutions = re.findall(resolution_pattern, content)

        codec_pattern = r'CODECS="([^"]+)"'
        codecs = re.findall(codec_pattern, content)

        for res in resolutions:
            match = re.search(rf'#EXT-X-STREAM-INF:[^\n]*RESOLUTION={re.escape(res)}[^\n]*\n([^\n]+)', content)
            if match:
                url = match.group(1)
                data_segments['urls'].append(urljoin(base_url, url))  # Completa a URL se for relativa
                data_segments['resolutions'][res] = urljoin(base_url, url)

        # Adiciona os codecs encontrados, evitando repetições
        for codec in codecs:
            if codec not in data_segments['codecs']:
                data_segments['codecs'].append(codec)

        # Adiciona a contagem de URLs de stream encontradas ao dicionário
        data_segments['len'] = len(data_segments['urls'])

        return data_segments


class EncryptSuport:
    """
        suporte a operações de criptografia AES-128 e SAMPLE-AES relacionadas a M3U8.
        Fornece métodos para obter a URL da chave de criptografia e o IV (vetor de inicialização) associado,
        necessários para descriptografar conteúdos M3U8 protegidos por AES-128.

        Métodos:
            - get_url_key_m3u8: Extrai a URL da chave de criptografia e o IV de um conteúdo M3U8.
        """

    @staticmethod
    def get_url_key_m3u8(m3u8_content: str, player: str, headers=None):
        """
            Extrai a URL da chave de criptografia AES-128 e o IV (vetor de inicialização) de um conteúdo M3U8.

            Este método analisa o conteúdo M3U8 para localizar a URL da chave de criptografia e o IV, se disponível.
            Em seguida, faz uma requisição HTTP para obter a chave em formato hexadecimal.

            Args:
                m3u8_content (str): String contendo o conteúdo do arquivo M3U8.
                player (str): URL base para formar o URL completo da chave, se necessário.
                headers (dict, optional): Cabeçalhos HTTP opcionais para a requisição da chave. Se não fornecido,
                                          cabeçalhos padrão serão utilizados.

            Returns:
                dict: Um dicionário contendo as seguintes chaves:
                    - 'key' (str): A chave de criptografia em hexadecimal.
                    - 'iv' (str): O vetor de inicialização (IV) em hexadecimal, se disponível.

                Caso não seja possível extrair a URL da chave ou o IV, retorna None.

            Examples:
                ```python
                m3u8_content = '''
                #EXTM3U
                #EXT-X-KEY:METHOD=AES-128,URI="https://example.com/key.bin",IV=0x1234567890abcdef
                #EXTINF:10.0,
                http://example.com/segment1.ts
                '''
                player = "https://example.com"
                result = EncryptSuport.get_url_key_m3u8(m3u8_content, player)
                print(result)
                # Saída esperada:
                # {'key': 'aabbccddeeff...', 'iv': '1234567890abcdef'}

                # Com cabeçalhos personalizados
                headers = {
                    "Authorization": "Bearer your_token"
                }
                result = EncryptSuport.get_url_key_m3u8(m3u8_content, player, headers=headers)
                print(result)
                ```

            Raises:
                requests.HTTPError: Se a requisição HTTP para a chave falhar.
            """
        pattern = r'#EXT-X-KEY:.*URI="([^"]+)"(?:.*,IV=(0x[0-9A-Fa-f]+))?'
        match = re.search(pattern, m3u8_content)
        data = {}
        if match:
            url_key = f"{player}{match.group(1)}"
            iv_hex = match.group(2)
            if not headers:
                headers_default = {
                    "Accept": "application/json, text/plain, */*",
                    "Accept-Encoding": "gzip, deflate, br, zstd",
                    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
                    "Content-Length": "583",
                    "Content-Type": "text/plain",
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "same-origin",
                    "Sec-Ch-Ua": "\"Not:A-Brand\";v=\"99\", \"Google Chrome\";v=\"118\", \"Chromium\";v=\"118\"",
                    "Sec-Ch-Ua-Mobile": "?0",
                    "Sec-Ch-Ua-Platform": "\"Windows\"",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                                  "Chrome/118.0.0.0 Safari/537.36"
                }
                headers = headers_default

                try:
                    resp = requests.get(url_key, headers=headers)
                    resp.raise_for_status()
                    key_bytes = resp.content
                    key_hex = key_bytes.hex()
                    data['key'] = key_hex
                    if iv_hex:
                        data['iv'] = iv_hex[2:]  # Remove '0x' prefix
                    return data
                except requests.exceptions.InvalidProxyURL as e:
                    raise M3u8NetworkingError(f"Erro: URL de proxy inválida: {e}")
                except requests.exceptions.InvalidURL:
                    raise M3u8NetworkingError("Erro: URL inválida fornecida.")
                except requests.exceptions.InvalidSchema:
                    raise M3u8NetworkingError("Erro: URL inválida, esquema não suportado.")
                except requests.exceptions.MissingSchema:
                    raise M3u8NetworkingError("Erro: URL inválida, esquema ausente.")
                except requests.exceptions.InvalidHeader as e:
                    raise M3u8NetworkingError(f"Erro de cabeçalho inválido: {e}")
                except ValueError as e:
                    raise M3u8FileError(f"Erro de valor: {e}")
                except requests.exceptions.ContentDecodingError as e:
                    raise M3u8NetworkingError(f"Erro de decodificação de conteúdo: {e}")
                except requests.exceptions.BaseHTTPError as e:
                    raise M3u8NetworkingError(f"Erro HTTP básico: {e}")
                except requests.exceptions.SSLError as e:
                    raise M3u8NetworkingError(f"Erro SSL: {e}")
                except requests.exceptions.ProxyError as e:
                    raise M3u8NetworkingError(f"Erro de proxy: {e}")
                except requests.exceptions.ConnectionError:
                    raise M3u8NetworkingError("Erro: O servidor ou o servidor encerrou a conexão.")
                except requests.exceptions.HTTPError as e:
                    raise M3u8NetworkingError(f"Erro HTTP: {e}")
                except requests.exceptions.Timeout:
                    raise M3u8NetworkingError(
                        "Erro de tempo esgotado: A conexão com o servidor demorou muito para responder.")
                except requests.exceptions.TooManyRedirects:
                    raise M3u8NetworkingError("Erro de redirecionamento: Muitos redirecionamentos.")
                except requests.exceptions.URLRequired:
                    raise M3u8NetworkingError("Erro: URL é necessária para a solicitação.")
                except requests.exceptions.ChunkedEncodingError as e:
                    raise M3u8NetworkingError(f"Erro de codificação em partes: {e}")
                except requests.exceptions.StreamConsumedError:
                    raise M3u8NetworkingError("Erro: Fluxo de resposta já consumido.")
                except requests.exceptions.RetryError as e:
                    raise M3u8NetworkingError(f"Erro de tentativa: {e}")
                except requests.exceptions.UnrewindableBodyError:
                    raise M3u8NetworkingError("Erro: Corpo da solicitação não pode ser rebobinado.")
                except requests.exceptions.RequestException as e:
                    raise M3u8NetworkingError(
                        f"Erro de conexão: Não foi possível se conectar ao servidor. Detalhes: {e}")

        else:
            return None


class M3U8Playlist:
    """análise de maneira mais limpa de m3u8"""

    def __init__(self, url: str, headers: dict = None):
        self.__parsing = M3u8Analyzer()
        self.__url = url
        self.__version = ''
        self.__number_segments = []
        self.__uris = []
        self.__codecs = []
        self.__playlist_type = None
        self.__headers = headers
        if not (url.startswith('https://') or url.startswith('http://')):
            raise ValueError("O Manifesto deve ser uma URL HTTPS ou HTTP!")

        self.__load_playlist()

    def __load_playlist(self):
        """
        Método privado para carregar a playlist a partir de uma URL ou arquivo.
        """
        self.__parsing = M3u8Analyzer()
        self.__content = self.__parsing.get_m3u8(url_m3u8=self.__url, headers=self.__headers)
        # Simulação do carregamento de uma playlist para este exemplo:
        self.__uris = self.__parsing.get_segments(self.__content, self.__url).get('enumerated_uris')
        self.__number_segments = len(self.__uris)
        self.__playlist_type = self.__parsing.get_type_m3u8_content(self.__content)
        self.__version = self.__get_version_manifest(content=self.__content)
        self.__resolutions = self.__parsing.get_segments(self.__content, self.__url).get('resolutions')
        self.__codecs = self.__parsing.get_segments(self.__content, self.__url).get('codecs')

    def __get_version_manifest(self, content):
        """
        Obtém a versão do manifesto #EXTM em uma playlist m3u8.
        #EXT-X-VERSION:4
        #EXT-X-VERSION:3
        etc...
        :param content: Conteúdo da playlist m3u8.
        :return: A versão do manifesto encontrada ou None se não for encontrado.
        """
        # Expressão regular para encontrar o manifesto
        pattern = re.compile(r'#EXT-X-VERSION:(\d*)')
        match = pattern.search(content)

        if match:
            # Retorna a versão encontrada
            ver = f"#EXT-X-VERSION:{match.group(1)}"
            return ver

        else:
            return '#EXT-X-VERSION:Undefined'  # Default para versão 1 se não houver número

    def get_codecs(self):
        """obter codecs na playlist"""
        return self.__codecs

    def info(self):
        """
        Retorna informações básicas sobre a playlist.

        Returns:
            dict: Informações sobre a URL, versão do manifesto, número de segmentos, tipo da playlist, se é criptografada e URIs dos segmentos.
        """
        info = {
            "url": self.__url,
            "version_manifest": self.__version,
            "number_of_segments": self.__number_segments,
            "playlist_type": self.__playlist_type,
            "codecs": self.__codecs,
            "encript": self.__is_encrypted(url=self.__url, headers=self.__headers),
            "uris": self.__uris,
        }
        return info

    def __is_encrypted(self, url, headers: dict = None):
        parser = M3u8Analyzer()
        m3u8_content = parser.get_m3u8(url)
        player = parser.get_player_playlist(url)
        try:
            cript = EncryptSuport.get_url_key_m3u8(m3u8_content=m3u8_content,
                                                   player=player,
                                                   headers=headers)
        except Exception as e:
            raise ValueError(f"erro {e}")
        return cript

    def this_encrypted(self):
        """
        Verifica se a playlist M3U8 está criptografada.

        Returns:
            bool: True se a playlist estiver criptografada, False caso contrário.
        """
        return self.__is_encrypted(url=self.__url, headers=self.__headers)

    def uris(self):
        """
        Retorna a lista de URIs dos segmentos.

        Returns:
            list: Lista de URIs dos segmentos.
        """
        return self.__uris

    def version_manifest(self):
        """
        Retorna a versão do manifesto da playlist M3U8.

        Returns:
            str: Versão do manifesto.
        """
        return self.__version

    def number_segments(self):
        """
        Retorna o número total de segmentos na playlist.

        Returns:
            int: Número de segmentos.
        """
        return self.__number_segments

    def playlist_type(self):
        """
        Retorna o tipo da playlist M3U8.

        Returns:
            str: Tipo da playlist.
        """
        return self.__playlist_type

    def get_resolutions(self):
        """
        Retorna as resoluções disponíveis na playlist M3U8.

        Returns:
            list: Lista de resoluções.
        """
        data = self.__resolutions
        resolutions = []
        for r in data:
            resolutions.append(r)
        return resolutions

    def filter_resolution(self, filtering: str):
        """
        Filtra e retorna a URL do segmento com a resolução especificada.

        Args:
            filtering (str): Resolução desejada (ex: '1920x1080').

        Returns:
            Optional[str]: URL do segmento correspondente à resolução, ou None se não encontrado.
        """
        data = self.__resolutions
        if filtering in data:
            return data.get(filtering)
        else:
            return None


class Wrapper:
    """Classe para parsear playlists M3U8."""

    @staticmethod
    def parsing_m3u8(url: str, headers: dict = None) -> M3U8Playlist:
        """
        Cria uma instância de M3U8Playlist a partir de uma URL de playlist M3U8.

        Este método estático é utilizado para inicializar e retornar um objeto da classe `M3U8Playlist`,
        que fornece funcionalidades para análise e manipulação de playlists M3U8.

        Args:
            url (str): URL da playlist M3U8 que deve ser parseada.
            headers (Optional[dict]): Cabeçalhos HTTP adicionais para a requisição (opcional).

        Returns:
            M3U8Playlist: Uma instância da classe `M3U8Playlist` inicializada com a URL fornecida.

        Raises:
            ValueError: Se a URL não for uma URL válida.

        Examples:
            ```python
            url_playlist = "https://example.com/playlist.m3u8"
            headers = {
                "User-Agent": "CustomAgent/1.0"
            }

            playlist = ParsingM3u8.parsing_m3u8(url=url_playlist, headers=headers)

            print(playlist.info())
            ```

        Notes:
            - Certifique-se de que a URL fornecida é uma URL válida e acessível.
            - Se os cabeçalhos forem fornecidos, eles serão utilizados na requisição para obter o conteúdo da playlist.
        """
        return M3U8Playlist(url=url, headers=headers)
