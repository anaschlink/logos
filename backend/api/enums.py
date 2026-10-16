
from enum import Enum


class Category(str, Enum):
    VEHICLE_ACCIDENT = "Acidente com Veículo"
    ACCIDENT_WITH_VICTIMS = "Acidente com Vítimas"
    ABNORMAL_WEATHER = "Condição Climática Atípica na Pista"
    MECHANICAL_FAILURE = "Problema Mecânico"
    ROAD_BLOCKAGE = "Bloqueio de Pista"


class Severity(str, Enum):
    HIGH = "Alta"
    MEDIUM = "Média"
    LOW = "Baixa"


class IncidentStatus(str, Enum):
    OPEN = "Aberto"
    INVESTIGATING = "Em Investigação"
    CLOSED = "Fechado"
    INCONCLUSIVE = "Inconclusivo"
