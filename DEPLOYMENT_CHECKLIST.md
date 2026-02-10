# 🚀 PR Bounty System - DEPLOYMENT CHECKLIST

**Branch**: `pr-bounty-system`
**Status**: ✅ Code uploaded, ready to merge & deploy

---

## ✅ COMPLETED (by Claude)

- [x] Created branch `pr-bounty-system`
- [x] Uploaded 9 new files to GitHub
- [x] Modified `bridge_web.py` (added 2 imports, 2 blueprint registrations)
- [x] Verified `base58>=2.1.0` already in requirements.txt
- [x] Created comprehensive documentation

**Files Added:**
```
✅ pr_security.py
✅ api_pr_review.py
✅ api_webhooks.py
✅ data/pr_reviews.json
✅ data/pr_payouts.json
✅ data/pr_rate_limits.json
✅ data/security_logs.json
✅ .github/PULL_REQUEST_TEMPLATE.md
✅ docs/PR_BOUNTY_SYSTEM.md
✅ docs/INTEGRATION_GUIDE.md
```

**Files Modified:**
```
✅ bridge_web.py (lines 60-73: added PR blueprints)
```

---

## 🎯 YOUR NEXT STEPS

### Step 1: Review & Merge Branch (5 min)

```bash
# Go to GitHub
https://github.com/WattCoin-Org/wattcoin/tree/pr-bounty-system

# Review changes (10 files modified)
# Create PR: pr-bounty-system → main
# Title: "Add PR Bounty System - Automated Review & Payouts"
# Merge PR
```

### Step 2: Set Railway Environment Variables (2 min)

Go to Railway → wattcoin project → Variables

Add these 4 variables:

```bash
GITHUB_WEBHOOK_SECRET=<paste_value_below>
PAUSE_PR_PAYOUTS=false
PAUSE_PR_REVIEWS=false
REQUIRE_DOUBLE_APPROVAL=false
```

**Generate webhook secret:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and use it for `GITHUB_WEBHOOK_SECRET`.

### Step 3: Deploy to Railway (Auto - 3 min)

Railway will auto-deploy when you merge to main.

Watch logs:
```
Railway → Deployments → Latest
```

Wait for: `✅ Build successful` → `✅ Deployed`

### Step 4: Verify Deployment (1 min)

Test health endpoint:
```bash
curl https://api.wattcoin.org/webhooks/health
```

Expected response:
```json
{"status": "ok", "webhook_secret_configured": true}
```

### Step 5: Configure GitHub Webhook (3 min)

1. Go to: https://github.com/WattCoin-Org/wattcoin/settings/hooks
2. Click **"Add webhook"**
3. Fill in:

```
Payload URL: https://api.wattcoin.org/webhooks/github
Content type: application/json
Secret: [paste same GITHUB_WEBHOOK_SECRET from Railway]
```

4. Which events?
   - Select: "Let me select individual events"
   - Check ONLY: ✅ **Pull requests**
   - Uncheck everything else

5. Check: ✅ Active
6. Click **"Add webhook"**

### Step 6: Test with Dummy PR (10 min)

Create a test PR:

```markdown
**Closes**: #[create_test_issue_first]
**Payout Wallet**: 7vvNkG3JF3JpxLEavqZSkc5T3n9hHR98Uw23fbWdXVSF

## Description
Test PR to verify bounty system works

## Changes Made
- Added comment to README
```

Then:
```bash
# Test review endpoint
curl -X POST https://api.wattcoin.org/api/v1/review_pr \
  -H "Content-Type: application/json" \
  -d '{
    "pr_url": "https://github.com/WattCoin-Org/wattcoin/pull/[NUMBER]"
  }'
```

Expected:
- ✅ Grok posts review comment on PR
- ✅ Returns score 1-10
- ✅ Review saved to data/pr_reviews.json

Merge the test PR:
- ✅ Webhook triggers
- ✅ Payout queued in data/pr_payouts.json
- ✅ Status comment posted

### Step 7: Post First Real Bounty Issues (15 min)

Create 3 bounty issues with this format:

**Title:**
```
[BOUNTY: 50,000 WATT] Add Error Handling to watt_scrape Function
```

**Labels:**
- `bounty`

**Body:**
```markdown
## Description
Improve error handling in the web scraper function to gracefully handle network failures.

## Requirements
- Add try/catch blocks around network requests
- Return meaningful error messages
- Update tests

## Acceptance Criteria
- PR passes Grok review (score ≥8)
- No breaking changes
- Follows existing code style

## How to Claim
1. Fork the repo
2. Submit PR with format from PULL_REQUEST_TEMPLATE.md
3. Include your Solana wallet address
4. Grok will review automatically
5. Admin approves payout after merge

**Reward**: 50,000 WATT
**Stake Required**: 5,000 WATT (10%)
```

Suggested bounties:
1. **50K WATT**: Add error handling to watt_scrape
2. **75K WATT**: Improve WattNode job routing logic
3. **100K WATT**: Add unit tests for PR review system

---

## 🧪 TESTING CHECKLIST

After deployment, verify:

- [ ] `/webhooks/health` returns 200 OK
- [ ] Test PR review endpoint works
- [ ] Grok posts review comment
- [ ] Webhook triggers on PR merge
- [ ] Payout queues correctly
- [ ] Rate limiting works (try 6 PRs from same wallet)
- [ ] Security logs are created
- [ ] Emergency pause env vars work

---

## 🚨 EMERGENCY CONTROLS

If something goes wrong:

**Pause all reviews:**
```bash
# In Railway env vars:
PAUSE_PR_REVIEWS=true
```

**Pause all payouts:**
```bash
PAUSE_PR_PAYOUTS=true
```

**View security logs:**
```bash
# SSH into Railway or check in GitHub:
cat data/security_logs.json | jq '.events[-10:]'
```

**Clear rate limits for a wallet:**
```bash
# Edit data/pr_rate_limits.json
# Remove the wallet entry
```

---

## 📊 MONITORING

**What to watch:**

1. **PR Reviews** - Check `data/pr_reviews.json`
2. **Payout Queue** - Check `data/pr_payouts.json`
3. **Security Events** - Check `data/security_logs.json`
4. **Rate Limits** - Check `data/pr_rate_limits.json`

**GitHub webhook deliveries:**
- Go to: Settings → Webhooks → Recent Deliveries
- Check for errors or failed deliveries

---

## ⏭️ NEXT: WSI Phase 1

Once PR system is deployed and tested:

**Tomorrow's Build:**
- WSI Phase 1 (token-gated Grok chat)
- Web interface
- "WattCoin SuperIntelligence" personality
- Balance gate (5K WATT minimum)

**Estimated time:** 8-10 hours

---

## 📝 NOTES

- All payouts require manual admin approval
- Grok review is advisory (you still control merge)
- Rate limits: 5 PRs/day per wallet + 24h cooldown
- Code scanning catches dangerous patterns
- Emergency controls available via env vars

---

## 🎯 SUCCESS METRICS

You'll know it's working when:

✅ First bounty PR submitted
✅ Grok posts review comment
✅ PR gets merged
✅ Payout queued automatically
✅ No errors in Railway logs

---

**Questions?** Check `docs/PR_BOUNTY_SYSTEM.md` or `docs/INTEGRATION_GUIDE.md`

**Ready to ship!** 🚀
