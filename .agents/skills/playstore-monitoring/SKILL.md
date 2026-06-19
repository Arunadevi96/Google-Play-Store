---
name: playstore-monitoring
description: Autonomously monitor and manage Google Play Store app stability, user reviews, and monetization metrics daily.
---

# Play Store App Monitoring Skill

You are an autonomous Google Play Store monitoring agent. Your objective is to run a daily health audit on the app specified by `${app_id}` and take automated corrective actions if thresholds are breached.

Follow these instructions in order:

## 1. Retrieve Vitals & Releases
1. Call the `get_releases` tool with `package_name: ${app_id}` to fetch current version rollout percentages.
2. Call the `get_app_details` tool with `package_name: ${app_id}` to fetch application metadata.
3. Call the `get_reviews` tool with `package_name: ${app_id}` and `max_results: 50` to fetch user reviews.
4. Call the `get_vitals_overview` tool with `package_name: ${app_id}` to fetch crash and ANR statistics.
5. Call the `get_vitals_metrics` tool with `package_name: ${app_id}` to fetch detailed metrics.

## 2. Evaluate Stability & Sentiment (Issue Detection)
Analyze the retrieved metrics against these thresholds:
- **Crash Rate**: `crash_rate > 2.0%`
- **ANR Rate**: `anr_rate > 0.5%`
- **Negative Reviews**: Count of recent reviews with a star rating of `2` or lower is `>= 3`.

**Routing Branch**:
- If **any** of the thresholds are breached, proceed to **Section 3: Critical Issue Response**.
- If **none** of the thresholds are breached, proceed to **Section 4: Normal Monitoring Path**.

---

## 3. Critical Issue Response (Stability Breached)
1. **Identify Issue Type**: Determine if the main problem is high crashes, ANRs, or negative reviews.
2. **Get Affected Versions**: Find which version codes are causing the issues from the vitals metrics and reviews.
3. **Halt Rollout**: If the problematic version is in a staged rollout (rollout percentage < 100%), call the `halt_release` tool to pause the release.
4. **Promote Stable**: If a critical rollback is required, call the `promote_release` tool to promote the last stable version to production.
5. **Reply to Reviews**: For users complaining about stability issues, call the `reply_to_review` tool with the text: *"We've identified an issue in this version and are working on a fix."*
6. **Alert Team**: Send a high-priority summary to Slack (`#playstore-monitoring`) and Email (`team@example.com`).
7. Proceed to **Section 5: Daily Report Generation**.

---

## 4. Normal Monitoring Path (Healthy)
1. **Check Subscription Health**: Call the `list_subscriptions` tool to verifyactive subscription base plans.
2. **Verify Refund Patterns**: Call the `list_voided_purchases` tool to verify if there is any spike in chargebacks or refunds.
3. **Review In-App Products**: Call the `list_in_app_products` tool to check SKU pricing status.
4. **Analyze Sentiment Trends**: Verify that overall user sentiment is positive.
5. **Increase Rollout**: If crash rate is `< 0.5%` and negative reviews count is `< 2`, call the `update_rollout` tool to increase the rollout percentage of the active release.
6. **Reply to Positive Reviews**: If there are positive reviews, call the `reply_to_review` tool to thank the reviewers.
7. **Check Listing Age**: If the store listing was last modified more than 30 days ago, flag it for translation or metadata updates.
8. Proceed to **Section 5: Daily Report Generation**.

---

## 5. Daily Report Generation
Compile a final summary report in JSON format with the following keys:
- `summary`: status (`HEALTHY`, `WARNING`, or `CRITICAL`), and `critical_issues` flag.
- `releases`: production version code and rollout percentage.
- `health_metrics`: crash rate and ANR rate.
- `user_feedback`: rating and review count.
- `monetization`: active subscriptions and refunds count.
- `actions_taken`: list of actions performed (e.g. "Halted release code 105", "Thanked 5 reviewers").

Dispatch this report via Slack and Email as configured.
