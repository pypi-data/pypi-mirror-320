"""Xbox Switch Bridge - Use Xbox controller with Nintendo Switch via Raspberry Pi."""

from .bridge import XboxSwitchBridge
from .service import install_service, uninstall_service, check_service_status

__version__ = "0.3.4"
__author__ = "Leonardo Carta"
__email__ = "leonardo@carta.vision"

__all__ = ['XboxSwitchBridge', 'install_service', 'uninstall_service', 'check_service_status']