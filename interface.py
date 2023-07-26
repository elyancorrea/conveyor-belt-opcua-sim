import PySimpleGUI as sg
from opcua import Client, ua

CONFIG_FILE = 'config.cfg'

def create_layout(config):
    layout = [
        [sg.Text('Endereço do servidor OPCUA:')],
        [sg.InputText(default_text=config.get('endereco', ''), key='endereco')],
        [sg.Text('NodeID do status da esteira:')],
        [sg.InputText(default_text=config.get('status', ''), key='status')],
        [sg.Text('NodeID do S1:')],
        [sg.InputText(default_text=config.get('s1', ''), key='s1')],
        [sg.Text('NodeID do S2:')],
        [sg.InputText(default_text=config.get('s2', ''), key='s2')],
        [sg.Text('NodeID do S3:')],
        [sg.InputText(default_text=config.get('s3', ''), key='s3')],
        [sg.Button('Conectar')],
        [sg.Text('Estado da esteira:', key='status_value')],
        [sg.Text('Valor do S1:', key='s1_value')],
        [sg.Text('Valor do S2:', key='s2_value')],
        [sg.Text('Valor do S3:', key='s3_value')],
    ]
    return layout


def read_config_file():
    try:
        with open(CONFIG_FILE, 'r') as file:
            config = {}
            for line in file:
                key, value = line.strip().split(':', 1)
                config[key] = value
        return config
    except FileNotFoundError:
        return {}
    except Exception as e:
        sg.popup(f'Erro ao ler o arquivo de configuração: {str(e)}', title='Erro')
        return {}


def write_config_file(config):
    try:
        with open(CONFIG_FILE, 'w') as file:
            for key, value in config.items():
                file.write(f'{key}:{value}\n')
    except Exception as e:
        sg.popup(f'Erro ao escrever o arquivo de configuração: {str(e)}', title='Erro')


def update_values(window, values):
    window['status_value'].update(f'Estado da esteira: {values["status"]}')
    window['s1_value'].update(f'Valor do S1: {values["s1"]}')
    window['s2_value'].update(f'Valor do S2: {values["s2"]}')
    window['s3_value'].update(f'Valor do S3: {values["s3"]}')


def subscribe_node(client, node, handler):
    subscription = client.create_subscription(500, handler)
    handle = subscription.subscribe_data_change(node)
    return handle


class SubHandler(object):
    def __init__(self, window, values, key):
        self.window = window
        self.values = values
        self.key = key

    def datachange_notification(self, node, val, data):
        self.values[self.key] = val
        update_values(self.window, self.values)

last_sensor_states = {'S1': None, 'S2': None, 'S3': None, 'status': None}

def write_node(sensor_name, state):
    config = read_config_file()
    endereco = config['endereco']

    node_id = None
    if sensor_name == 'S1':
        node_id = config['s1']
    elif sensor_name == 'S2':
        node_id = config['s2']
    elif sensor_name == 'S3':
        node_id = config['s3']
    elif sensor_name == 'status':
        node_id = config['status']

    if node_id:
        last_state = last_sensor_states[sensor_name]
        if last_state is None or state != last_state:
            client = Client(endereco)
            client.connect()
            node = client.get_node(node_id)
            node.set_value(state)
            print(node_id, state)
            last_sensor_states[sensor_name] = state

            client.disconnect()



def connect_to_server(window, values):
    try:
        client = Client(values['endereco'])
        client.connect()
        print(f'Conectado ao servidor OPCUA em {values["endereco"]}')

        # Verifica se os NodeIDs estão corretos e existem no servidor OPC UA
        node_ids = {
            'status': 'NodeID do status da esteira',
            's1': 'NodeID do S1',
            's2': 'NodeID do S2',
            's3': 'NodeID do S3'
        }

        for key, label in node_ids.items():
            try:
                node = client.get_node(values[key])
                # Testa a leitura do valor para verificar se o NodeID é válido
                _ = node.get_value()
            except ua.uaerrors.BadNodeIdUnknown:
                sg.popup(f'O NodeID "{values[key]}" para o nó "{label}" é inválido!', title='Erro')
                client.disconnect()
                return None, None

        # Lê os valores dos NodeIDs
        status_node = client.get_node(values['status'])
        s1_node = client.get_node(values['s1'])
        s2_node = client.get_node(values['s2'])
        s3_node = client.get_node(values['s3'])


        # Obtém os valores
        status = status_node.get_value()
        s1 = s1_node.get_value()
        s2 = s2_node.get_value()
        s3 = s3_node.get_value()

        # Atualiza os valores exibidos na janela
        update_values(window, {
            'status': status,
            's1': s1,
            's2': s2,
            's3': s3
        })

        # Inicia a subscrição dos NodeIDs
        handler = SubHandler(window, values, 'status')
        subscription_handler = subscribe_node(client, status_node, handler)
        handler = SubHandler(window, values, 's1')
        subscribe_node(client, s1_node, handler)
        handler = SubHandler(window, values, 's2')
        subscribe_node(client, s2_node, handler)
        handler = SubHandler(window, values, 's3')
        subscribe_node(client, s3_node, handler)

        # Escreve os valores no arquivo de configuração
        write_config_file(values)
        return client, subscription_handler
    except ua.uaerrors.BadNodeIdUnknown as e:
        sg.popup(f'Erro: NodeID inválido! Detalhes: {str(e)}', title='Erro')
    except Exception as e:
        sg.popup(f'Erro ao conectar e ler do servidor OPCUA: {str(e)}', title='Erro')
    return None, None


def main():
    sg.theme('DefaultNoMoreNagging')

    config = read_config_file()
    layout = create_layout(config)

    window = sg.Window('Aplicação OPCUA', layout)

    client = None
    subscription_handler = None

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == 'Conectar':
            if '' in values.values():
                sg.popup('Preencha todos os campos!', title='Erro')
            else:
                if client is not None:
                    client.disconnect()
                    print('Desconectado do servidor OPCUA')

                client, subscription_handler = connect_to_server(window, values)

    if subscription_handler is not None:
        subscription_handler.delete()

    if client is not None:
        client.disconnect()
        print('Desconectado do servidor OPCUA')

    window.close()

