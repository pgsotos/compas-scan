# 🛡️ Branch Protection Guide

Guide for managing branch protection rules in CompasScan repository.

---

## Current Configuration

### Branch: `develop`

**Protection Rules:**
- **Required Pull Request Reviews:** 0 (auto-merge enabled)
- **Enforce for Admins:** ❌ Disabled (admins can bypass)
- **Required Status Checks:** None (strict mode disabled)
- **Allow Force Pushes:** ❌ Disabled
- **Allow Deletions:** ❌ Disabled

**Status:** ✅ Configured for fast iteration - GitHub MCP can merge directly

### Branch: `staging`

**Protection Rules:**
- **Required Pull Request Reviews:** 1 approval required
- **Enforce for Admins:** ❌ Disabled (admins can bypass)
- **Required Status Checks:** Vercel (strict mode enabled)
- **Allow Force Pushes:** ❌ Disabled
- **Allow Deletions:** ❌ Disabled

**Status:** ✅ Configured for QA validation

### Branch: `main`

**Protection Rules:**
- **Required Pull Request Reviews:** 2 approvals required
- **Enforce for Admins:** ✅ Enabled (even admins must follow rules)
- **Required Status Checks:** Vercel + Tests (strict mode enabled)
- **Allow Force Pushes:** ❌ Disabled
- **Allow Deletions:** ❌ Disabled

**Status:** ✅ Configured for maximum production safety

---

## Recommended Configuration for Gitflow

### Development Branch (`develop`)

**Recommended Settings:**
```json
{
  "required_pull_request_reviews": {
    "required_approving_review_count": 0
  },
  "enforce_admins": false,
  "required_status_checks": {
    "strict": false,
    "contexts": ["Vercel"]
  }
}
```

**Rationale:**
- Solo developer team - no need for mandatory reviews
- Allows fast iteration during development
- Vercel deployment check ensures code compiles
- Admins can merge without restrictions

### Staging Branch (`staging`)

**Recommended Settings:**
```json
{
  "required_pull_request_reviews": {
    "required_approving_review_count": 1
  },
  "enforce_admins": false,
  "required_status_checks": {
    "strict": true,
    "contexts": ["Vercel"]
  }
}
```

**Rationale:**
- At least 1 review before going to staging
- Strict status checks to ensure all tests pass
- Admins can bypass if urgent fix needed

### Production Branch (`main`)

**Recommended Settings:**
```json
{
  "required_pull_request_reviews": {
    "required_approving_review_count": 2,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": true
  },
  "enforce_admins": true,
  "required_status_checks": {
    "strict": true,
    "contexts": ["Vercel", "Tests"]
  },
  "required_linear_history": true
}
```

**Rationale:**
- Highest protection for production code
- Multiple reviews required
- Even admins must follow the rules
- Linear history for clean git log

---

## Managing Protection Rules

### View Current Protection

```bash
# For develop branch
gh api repos/pgsotos/compas-scan/branches/develop/protection | jq

# For all branches
gh api repos/pgsotos/compas-scan/branches | jq '.[] | {name, protected}'
```

### Configure All Branches (Recommended)

Use the comprehensive script to configure all branches at once:

```bash
./scripts/configure-branch-protections.sh
```

This script configures:
- `develop`: 0 reviews, fast iteration
- `staging`: 1 review, QA validation
- `main`: 2 reviews, production safety

### Adjust Protection (Interactive)

For individual branch adjustments, use:

```bash
./scripts/adjust-branch-protection.sh
```

Options:
1. Keep current protections (use `--admin` to merge)
2. Disable enforce_admins (recommended for solo dev)
3. Remove all protections (not recommended)
4. Remove review requirement (recommended for `develop`)

### Manual Adjustments

#### Disable Enforce for Admins

```bash
gh api -X DELETE repos/pgsotos/compas-scan/branches/develop/protection/enforce_admins
```

#### Remove Review Requirement

```bash
gh api -X DELETE repos/pgsotos/compas-scan/branches/develop/protection/required_pull_request_reviews
```

#### Add Status Check Requirement

```bash
gh api -X PATCH repos/pgsotos/compas-scan/branches/develop/protection \
  -f required_status_checks='{"strict":true,"contexts":["Vercel"]}'
```

---

## Merging PRs with Protections

### Option 1: Use Admin Flag (Current Setup)

```bash
gh pr merge <number> --squash --admin
```

**Pros:**
- Keeps protections in place
- Bypasses reviews when needed
- Maintains audit trail

**Cons:**
- Need to remember `--admin` flag
- Can't use GitHub MCP for merge (requires admin API access)

### Option 2: Adjust Protections (Recommended)

Remove review requirement for `develop`:

```bash
./scripts/adjust-branch-protection.sh
# Select option 4
```

Then merge normally:

```bash
gh pr merge <number> --squash
# OR use GitHub MCP
```

**Pros:**
- No need for special flags
- GitHub MCP can merge directly
- Faster workflow

**Cons:**
- Less protection during development

---

## GitHub MCP Considerations

### Current Token Permissions

The GitHub MCP token has the following scopes:
- `repo` - Full repository access
- `workflow` - Workflow management
- `read:org` - Read organization data
- `gist` - Gist management

### MCP Merge Capabilities

GitHub MCP can merge PRs when:
- ✅ Token has `repo` scope (achieved)
- ✅ User is admin of repository (achieved)
- ✅ Branch protection allows admin bypass OR no review requirement

### Recommended Setup

For GitHub MCP to work seamlessly:

1. **Update token** (already done):
   ```bash
   ./scripts/fix-github-mcp-token.sh
   ```

2. **Adjust branch protection**:
   ```bash
   ./scripts/adjust-branch-protection.sh
   # Option 2 or 4
   ```

3. **Restart Cursor** to apply token changes

---

## Best Practices

### Solo Developer (Current Situation)

**Develop:**
- No review requirement
- Vercel deployment check only
- Fast iteration

**Staging:**
- Optional 1 review (self-review acceptable)
- All checks must pass
- QA validation

**Main:**
- Mandatory 2 reviews (or use `--admin` for hotfixes)
- All checks must pass
- Production release only

### Team Environment (Future)

**Develop:**
- 1 review from peer
- CI/CD checks must pass
- Daily integration

**Staging:**
- 1 review from senior developer
- All tests must pass
- Weekly releases

**Main:**
- 2 reviews (1 from code owner)
- All tests + security scans
- Enforce for admins
- Monthly releases

---

## Troubleshooting

### PR Won't Merge

**Error:** "the base branch policy prohibits the merge"

**Solutions:**
1. Use admin flag: `gh pr merge --admin`
2. Adjust branch protection (see script)
3. Get required approvals

### GitHub MCP Can't Merge

**Error:** "403 Resource not accessible by personal access token"

**Solutions:**
1. Update token: `./scripts/fix-github-mcp-token.sh`
2. Adjust branch protection to allow admin bypass
3. Restart Cursor to reload token

### Status Checks Blocking Merge

**Error:** "Required status checks have not passed"

**Solutions:**
1. Wait for Vercel deployment to complete
2. Fix failing tests
3. Temporarily disable status checks (not recommended)

---

## References

- [GitHub Branch Protection API](https://docs.github.com/en/rest/branches/branch-protection)
- [GitHub CLI Documentation](https://cli.github.com/manual/)
- [CompasScan Gitflow](.cursorrules#gitflow--version-control)

---

**Last Updated:** 2024-12-04  
**Maintainer:** @pgsotos

