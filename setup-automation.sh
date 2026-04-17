#!/bin/bash
# 동탄 쓰레기봉투 판매점 사이트 - 완전 자동 설정 스크립트
# 실행: bash setup-automation.sh

set -e

echo "🚀 동탄 쓰레기봉투 판매점 사이트 자동 설정"
echo "=========================================="

# 1. GitHub CLI 로그인 확인
echo ""
echo "1️⃣ GitHub CLI 확인..."
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh)가 설치되어 있지 않습니다."
    echo "설치: https://cli.github.com/"
    exit 1
fi

if ! gh auth status &> /dev/null; then
    echo "🔐 GitHub CLI 로그인 필요"
    gh auth login
fi
echo "✅ GitHub CLI 인증 완료"

# 2. 저장소 생성
echo ""
echo "2️⃣ GitHub 저장소 생성..."
REPO_NAME="dongtan-bag-shop"
if gh repo view "$REPO_NAME" &> /dev/null; then
    echo "⚠️ 저장소 '$REPO_NAME'가 이미 존재합니다"
else
    gh repo create "$REPO_NAME" --public --source=. --remote=origin --push
    echo "✅ 저장소 생성 완료: https://github.com/$(gh api user -q .login)/$REPO_NAME"
fi

# 3. Firebase CLI 확인
echo ""
echo "3️⃣ Firebase CLI 확인..."
if ! command -v firebase &> /dev/null; then
    echo "📦 Firebase CLI 설치 중..."
    npm install -g firebase-tools
fi

# 4. Firebase CI 토큰 생성
echo ""
echo "4️⃣ Firebase CI 토큰 생성..."
echo "🔐 브라우저에서 Firebase에 로그인하세요..."
FIREBASE_TOKEN=$(firebase login:ci)

# 5. GitHub Secrets에 토큰 등록
echo ""
echo "5️⃣ GitHub Secrets에 FIREBASE_TOKEN 등록..."
echo "$FIREBASE_TOKEN" | gh secret set FIREBASE_TOKEN -R "$(gh api user -q .login)/$REPO_NAME"
echo "✅ FIREBASE_TOKEN 등록 완료"

# 6. 첫 배포 실행
echo ""
echo "6️⃣ 첫 자동 배포 실행..."
git push origin master || git push origin main
echo "✅ 코드 푸시 완료 - GitHub Actions가 자동으로 배포합니다"

# 7. 워크플로우 상태 확인
echo ""
echo "7️⃣ GitHub Actions 워크플로우 상태..."
sleep 5
echo "📊 워크플로우 실행 확인:"
echo "   https://github.com/$(gh api user -q .login)/$REPO_NAME/actions"

echo ""
echo "=========================================="
echo "🎉 설정 완료!"
echo ""
echo "📱 사이트 주소: https://simple-real-db.web.app"
echo "📁 GitHub 저장소: https://github.com/$(gh api user -q .login)/$REPO_NAME"
echo ""
echo "⏰ 자동 갱신 스케줄:"
echo "   - 매일 08:00, 10:00, 12:00, 14:00, 16:00, 18:00, 20:00"
echo "   - 총 7회/일 (2시간 간격, 낮시간만)"
echo ""
echo "✨ 이제 매 2시간마다 데이터가 자동으로 갱신됩니다!"
