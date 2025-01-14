import sys
import os

# Adiciona o diretório atual do pacote ao sys.path
package_dir = os.path.dirname(__file__)
if package_dir not in sys.path:
    sys.path.insert(0, package_dir)