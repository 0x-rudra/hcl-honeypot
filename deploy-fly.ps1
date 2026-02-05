# Fly.io Quick Deployment Script for Windows PowerShell

Write-Host "🚀 HCL Honeypot API - Fly.io Deployment" -ForegroundColor Cyan
Write-Host "=" * 50

# Check if flyctl is installed
if (!(Get-Command flyctl -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Fly.io CLI not found. Installing..." -ForegroundColor Yellow
    iwr https://fly.io/install.ps1 -useb | iex
    Write-Host "✅ Fly.io CLI installed. Please restart your terminal and run this script again." -ForegroundColor Green
    exit
}

Write-Host "✅ Fly.io CLI found" -ForegroundColor Green

# Check if logged in
$authCheck = fly auth whoami 2>&1
if ($authCheck -like "*not authenticated*") {
    Write-Host "🔑 Logging into Fly.io..." -ForegroundColor Yellow
    fly auth login
}

Write-Host "✅ Authenticated with Fly.io" -ForegroundColor Green

# Deploy
Write-Host ""
Write-Host "📦 Deploying application..." -ForegroundColor Cyan

# Set secrets (you'll need to edit these)
Write-Host "Setting secrets..." -ForegroundColor Yellow
Write-Host "⚠️  Make sure to set your actual Gemini API key!" -ForegroundColor Red
# fly secrets set GEMINI_API_KEY=your_actual_key_here
# fly secrets set API_KEY=honeypot-test-key-2026-secure

# Deploy
Write-Host "Deploying to Fly.io..." -ForegroundColor Cyan
fly deploy

Write-Host ""
Write-Host "=" * 50
Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Your API is available at:" -ForegroundColor Cyan
Write-Host "https://hcl-honeypot-api.fly.dev/honeypot" -ForegroundColor Yellow
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Cyan
Write-Host "  fly logs          - View real-time logs" -ForegroundColor White
Write-Host "  fly status        - Check app status" -ForegroundColor White
Write-Host "  fly dashboard     - Open dashboard in browser" -ForegroundColor White
Write-Host "  fly ssh console   - SSH into your app" -ForegroundColor White
