#!/bin/bash
# Script to adjust branch protection rules for develop branch

set -e

OWNER="pgsotos"
REPO="compas-scan"
BRANCH="develop"

echo "🔧 Ajustando protecciones de rama para develop..."
echo ""

echo "📋 Configuración actual:"
gh api repos/$OWNER/$REPO/branches/$BRANCH/protection | jq '{
  required_pull_request_reviews: .required_pull_request_reviews.required_approving_review_count,
  enforce_admins: .enforce_admins.enabled,
  required_status_checks: .required_status_checks.strict
}'
echo ""

echo "🎯 Opciones disponibles:"
echo ""
echo "1. Mantener protecciones actuales (requiere --admin para mergear)"
echo "2. Deshabilitar enforce_admins (admins pueden mergear sin restricciones)"
echo "3. Eliminar completamente las protecciones de develop"
echo "4. Reducir reviews requeridos a 0 (auto-merge permitido)"
echo ""
read -p "Selecciona una opción (1-4): " -n 1 -r
echo ""
echo ""

case $REPLY in
    1)
        echo "✅ Manteniendo configuración actual"
        echo "   Usa 'gh pr merge --admin' para mergear PRs"
        ;;
    2)
        echo "🔧 Deshabilitando enforce_admins..."
        gh api -X DELETE repos/$OWNER/$REPO/branches/$BRANCH/protection/enforce_admins
        echo "✅ Admins ahora pueden mergear sin restricciones"
        ;;
    3)
        echo "⚠️  ¿Estás seguro de eliminar TODAS las protecciones? (y/n)"
        read -p "> " -n 1 -r CONFIRM
        echo ""
        if [[ $CONFIRM =~ ^[Yy]$ ]]; then
            gh api -X DELETE repos/$OWNER/$REPO/branches/$BRANCH/protection
            echo "✅ Protecciones eliminadas completamente"
        else
            echo "❌ Operación cancelada"
        fi
        ;;
    4)
        echo "🔧 Eliminando requisito de reviews..."
        gh api -X DELETE repos/$OWNER/$REPO/branches/$BRANCH/protection/required_pull_request_reviews
        echo "✅ Reviews ya no son requeridos (auto-merge habilitado)"
        ;;
    *)
        echo "❌ Opción inválida"
        exit 1
        ;;
esac

echo ""
echo "📊 Nueva configuración:"
gh api repos/$OWNER/$REPO/branches/$BRANCH/protection 2>&1 | jq -r 'if type == "object" then {
  required_pull_request_reviews: .required_pull_request_reviews.required_approving_review_count,
  enforce_admins: .enforce_admins.enabled,
  required_status_checks: .required_status_checks.strict
} else "No protections" end' || echo "Sin protecciones"
echo ""

