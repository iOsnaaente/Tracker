__author__     = "Bruno Gabriel F. Sampaio"
__version__    = "0.81.0"
__company__    = "Jet Towers - Telecomunicações // http://www.jettowers.com.br/"
__maintainer__ = "Bruno Gabriel F. Sampaio"
__email__      = "bruno.sampaio@acad.ufsm.br"
__status__     = "Prototype"
 
""" Protótipo de criação de um rastreador solar - Tracker
    
    Firmware utilizado em um Raspberry pi Pico para controle
    de motores de passo que realizam o rastreamento solar
    garantindo mais geração elétrica a partir de painéis
    fotovoltáicos.
    
    Versão 0.9.3.0::
        >>> Mudança do controle dos motores usando os PIOs  
    
    Versão 0.9.2::
        >>> Código AS5043A para encoder Magnético
        >>> Nova tentativa de rastreamento da posição dos motores
        
        
    Versão 0.9.1::
        >>> Processamento dos dados do acelerometro
        >>> Valores obtidos inconclusivos para a finalidade
        >>> Acelerometro não será usado 
    
    Versão 0.9.0::
        >>> Criação do arquivo Acell.py para os dados do acelerometro
        >>> Teste do acelerometro
        >>> Criação das funções de acionamento dos motores via relé 
    
    
    Versão 0.8.1::
        >>> Adaptação da placa de desenvolvimento::
            >>> Acrescimo do relé de acionamento dos motores 
    
    Versão 0.8.0::
        >>> Correção da comunicação serial.
        >>> Criação de mais variáveis de estado
        
    Versão  0.7.0::
        >>> Criação do módulo Timanager. Junção de Timer e Manager
            Realiza todo controle de passagem de tempo e movimento
            decorrente desse periodo.
    
    Versão 0.6.1::
        >>> Correção do movimento de retorno do Tracker.
            >>>Segundo teste de fogo::
                >>> Controle de retorno OK
                
    Versão 0.6.0::
        >>> Movimentação acelerada do movimento real de rastreio.
            >>>Primeiro teste de fogo::
                >>> Movimentação OK 
                >>> Dados precisos OK
                >>> Controle de retorno FAIL
    
    Versão 0.55.0::
        >>> Extinção do uso de threads para os Levers.
        >>> Extinção do uso de threads para a Serial.
        
    Versão  0.5.0::
        >>> Levers. Criação da Classe Levers para controle manual dos
            motores via alavancas presas à placa de desenvolvimento.
            Evitando poluição de código.
            
    Versão  0.4.0::
        >>> Const. Evitando poluição do escopo principal (main),
            separou-se as constantes em outro file.py chamado Const
        >>> FileStatements. Criação de um file.py FileStatements
            que guarda as funções de escrita Flash do RasPico.
            
    Versão  0.3.0::
        >>> Serial comunication. Ponta pé inicial da comunicação serial
            utilizando structs pack e unpack. Funcional, mas incompleto.
            
    Versão  0.23.0::
        >>> Finalização da Classe StepMotors. Adição dos nanoSteps que
            guardam decimais do movimento dos motores.
            StepMotors agora esta mais organizado e limpo.
            Funcionando 100% porém falta documentar.
        >>> Criação da função get_twilights() dentro de SunPosition.
            Função responsável por pegar os horários de crepusculos do dia.
            
    Versão  0.21.0::
        >>> Correção da classe StepMotors. Separação da classe Motors
            em duas classes distintas. Motors e Motor ( pai e filho).
        >>> Correção no código do DS3231.
        >>> Documentação do código do DS3231. Agora esta 100%.
        
    Versão  0.2.0::
        >>> Criação da interface StepMotors para fazer o controle dos
            motores de passo.
        >>> Criação da interface DS3231. Faltam ajustes.
        >>> Finalização do código SunPosition de rastreio solar. Já funciona.
        
    Versão  0.1.0::
        >>> Correções no código SunPosition de rastreio solar. Definição
            final de como será feito a computação das posições de azimute
            e zenite( altitude ) sem o uso de classes.
            >>> Função Compute() realiza todos os cálculos.
            
    Versão 0.01.0::
        >>> Estruturação do primeiro modelo funcional.
        >>> Definição de todo o escopo do Firmware.
            >>> Rastreio solar - SunPosition
            >>> Contagem da hora - DS3231
            >>> Controle dos motores - StepMotors
            
    Versão 0.0.10::
        >>> Migração do código em C ( Arduino ) para Python 
     
"""

