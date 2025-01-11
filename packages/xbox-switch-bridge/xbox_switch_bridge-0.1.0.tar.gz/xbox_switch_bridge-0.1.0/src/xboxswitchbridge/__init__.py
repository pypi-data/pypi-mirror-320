"""Xbox Switch Bridge - Use Xbox controller with Nintendo Switch via Raspberry Pi."""

from .bridge import XboxSwitchBridge
from .service import install_service, uninstall_service, check_service_status

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = ['XboxSwitchBridge', 'install_service', 'uninstall_service', 'check_service_status']