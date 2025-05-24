#!/bin/bash

# Nome do pacote final
PACKAGE_NAME="lambda-embrapa.zip"

# Pasta da venv
VENV_DIR="venv"

# Python version folder (ajuste se necessário)
PYTHON_VERSION="python3.9"

# Limpa arquivos antigos
rm -rf lambda-package "$PACKAGE_NAME"
mkdir lambda-package

# Copia dependências da venv para a pasta
cp -r $VENV_DIR/lib/$PYTHON_VERSION/site-packages/* lambda-package/

# Copia o código da aplicação
cp lambda_function.py lambda-package/

# Cria o pacote zipado
cd lambda-package
zip -r ../$PACKAGE_NAME .
cd ..

echo "✅ Pacote $PACKAGE_NAME criado com sucesso!"
