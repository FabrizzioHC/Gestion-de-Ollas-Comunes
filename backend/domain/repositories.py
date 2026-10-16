"""
CAPA DE DOMINIO - Interfaces de Repositorio
Define los contratos que deben implementar los repositorios
"""
from abc import ABC, abstractmethod
from typing import List, Optional

class UserRepository(ABC):
    @abstractmethod
    def create(self, user) -> int:
        pass

    @abstractmethod
    def find_by_id(self, user_id: int):
        pass

    @abstractmethod
    def find_by_email(self, email: str):
        pass

    @abstractmethod
    def find_all(self, role: Optional[str] = None) -> List:
        pass

    @abstractmethod
    def update(self, user_id: int, user_data: dict) -> bool:
        pass

    @abstractmethod
    def delete(self, user_id: int) -> bool:
        pass


class OllaComunRepository(ABC):
    @abstractmethod
    def create(self, olla) -> int:
        pass

    @abstractmethod
    def find_by_id(self, olla_id: int):
        pass

    @abstractmethod
    def find_all(self, estado: Optional[str] = None) -> List:
        pass

    @abstractmethod
    def find_by_usuario(self, usuario_id: int) -> List:
        pass

    @abstractmethod
    def update(self, olla_id: int, olla_data: dict) -> bool:
        pass

    @abstractmethod
    def delete(self, olla_id: int) -> bool:
        pass


class DonacionRepository(ABC):
    @abstractmethod
    def create(self, donacion) -> int:
        pass

    @abstractmethod
    def find_by_id(self, donacion_id: int):
        pass

    @abstractmethod
    def find_all(self, estado: Optional[str] = None) -> List:
        pass

    @abstractmethod
    def find_by_donador(self, donador_id: int) -> List:
        pass

    @abstractmethod
    def find_by_olla(self, olla_id: int) -> List:
        pass

    @abstractmethod
    def update(self, donacion_id: int, donacion_data: dict) -> bool:
        pass

    @abstractmethod
    def delete(self, donacion_id: int) -> bool:
        pass


class SolicitudRecursoRepository(ABC):
    @abstractmethod
    def create(self, solicitud) -> int:
        pass

    @abstractmethod
    def find_by_id(self, solicitud_id: int):
        pass

    @abstractmethod
    def find_all(self, estado: Optional[str] = None) -> List:
        pass

    @abstractmethod
    def find_by_olla(self, olla_id: int) -> List:
        pass

    @abstractmethod
    def update(self, solicitud_id: int, solicitud_data: dict) -> bool:
        pass

    @abstractmethod
    def delete(self, solicitud_id: int) -> bool:
        pass


class EntregaRepository(ABC):
    @abstractmethod
    def create(self, entrega) -> int:
        pass

    @abstractmethod
    def find_by_id(self, entrega_id: int):
        pass

    @abstractmethod
    def find_all(self) -> List:
        pass

    @abstractmethod
    def find_by_olla(self, olla_id: int) -> List:
        pass

    @abstractmethod
    def update(self, entrega_id: int, entrega_data: dict) -> bool:
        pass

    @abstractmethod
    def delete(self, entrega_id: int) -> bool:
        pass
