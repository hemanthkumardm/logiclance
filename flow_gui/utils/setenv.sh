#!/bin/bash

# Usage: ./generate_env.sh <project_name>
# Example: ./generate_env.sh axl

if [ -z "$1" ]; then
  echo "❌ Please provide a project name. Usage: ./generate_env.sh <project_name>"
  exit 1
fi

PROJECT_NAME="$1"
PROJECT_DIR="configs/projects/${PROJECT_NAME}"

if [ ! -d "$PROJECT_DIR" ]; then
  echo "❌ Project '$PROJECT_NAME' not found in configs/projects/"
  exit 1
fi

# Get absolute path of Logic Lance root
LOGICLANCE_ROOT=$(cd "$(dirname "$0")" && pwd)

ENV_FILE="${PROJECT_DIR}/env.sh"

echo "📦 Generating environment file at $ENV_FILE"

cat > "$ENV_FILE" <<EOF
#!/bin/bash

# Auto-generated env file for Logic Lance project: ${PROJECT_NAME}

export LOGICLANCE_PROJECT=${PROJECT_NAME}
export LOGICLANCE_ROOT=${LOGICLANCE_ROOT}

export LOGICLANCE_RTL=\$LOGICLANCE_ROOT/${PROJECT_DIR}/rtl
export LOGICLANCE_LIB=\$LOGICLANCE_ROOT/${PROJECT_DIR}/lib
export LOGICLANCE_LEF=\$LOGICLANCE_ROOT/${PROJECT_DIR}/lef
export LOGICLANCE_SDC=\$LOGICLANCE_ROOT/${PROJECT_DIR}/sdc

export LOGICLANCE_USER_SCRIPTS=\$LOGICLANCE_ROOT/user_scripts
export LOGICLANCE_LAUNCH_SCRIPTS=\$LOGICLANCE_ROOT/scripts
export LOGICLANCE_REPORTS=\$LOGICLANCE_ROOT/reports
export LOGICLANCE_LOGS=\$LOGICLANCE_ROOT/logs

echo "✅ Environment set for project: ${PROJECT_NAME}"
EOF

chmod +x "$ENV_FILE"
echo "✅ Done. To use it, run: source ${ENV_FILE}"
