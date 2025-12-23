# Vercel Web Analytics Implementation Guide - TaskCert

This document provides technical implementation details for Vercel Web Analytics integration in the TaskCert Django project.

## What Was Implemented

Vercel Web Analytics has been integrated into the TaskCert project to track user traffic, page views, and performance metrics. This implementation follows Vercel's best practices for Django-based applications.

## Changes Made

### 1. Updated Base Template (`templates/base.html`)

Added the Vercel Web Analytics tracking script to the base template's `<head>` section:

```html
<!-- Vercel Web Analytics -->
<script>
  window.va = window.va || function () { (window.vaq = window.vaq || []).push(arguments); };
</script>
<script defer src="/_vercel/insights/script.js"></script>
```

**Location**: After CSS includes, before `{% block extra_css %}`

**Why this location?**
- Placed in `<head>` to ensure the analytics script initializes early
- Uses `defer` attribute to load asynchronously without blocking page rendering
- The `window.va` queue allows events to be queued before the script fully loads
- Affects all child templates that extend `base.html`

### 2. Created Documentation

Two documentation files were created:

- **VERCEL_ANALYTICS_SETUP.md**: User-friendly guide for enabling and using Vercel Web Analytics
- **ANALYTICS_IMPLEMENTATION.md**: This technical implementation guide

## How It Works

### Script Flow

1. **Page Load**: When a user visits any page on TaskCert, the `window.va` function is defined
2. **Script Download**: The `/_vercel/insights/script.js` deferred script loads asynchronously
3. **Event Tracking**: The analytics script automatically tracks:
   - Page views and navigation
   - Core Web Vitals (LCP, FID, CLS)
   - User interactions
   - Error tracking
4. **Data Collection**: Events are sent to `/_vercel/insights/view` endpoint
5. **Dashboard**: Data appears in the Vercel Dashboard Analytics tab

### Coverage

Since the analytics script is in the `base.html` template, it affects all pages that extend this template, which includes:
- User dashboard
- Task pages
- Exam pages
- Certificate pages
- Admin dashboard
- All other authenticated pages

### No Backend Changes Required

This implementation requires **no changes to Django views, models, or URL patterns** because:
- Vercel automatically handles the `/_vercel/insights/*` routes
- The analytics script is purely client-side JavaScript
- No new dependencies were added to `requirements.txt`
- No database schema changes are needed

## Deployment

### To Deploy

1. Commit the changes:
   ```bash
   git add templates/base.html VERCEL_ANALYTICS_SETUP.md ANALYTICS_IMPLEMENTATION.md
   git commit -m "Add Vercel Web Analytics integration"
   ```

2. Push to your repository:
   ```bash
   git push origin main
   ```

3. Enable Web Analytics in Vercel Dashboard:
   - Navigate to your project on [Vercel Dashboard](https://vercel.com/dashboard)
   - Go to the **Analytics** tab
   - Click **Enable**

4. Vercel will automatically deploy your changes on the next push

### Verification

After deployment, verify analytics are working:

1. Visit your deployed TaskCert site at `task-cert.vercel.app`
2. Open browser DevTools (F12)
3. Go to the **Network** tab
4. Look for requests to:
   - `/_vercel/insights/script.js` (loads the analytics script)
   - `/_vercel/insights/view` (sends analytics events)

If you see these requests, analytics are working correctly.

## Data Available in Dashboard

Once analytics are enabled and collecting data, you can view:

- **Page Views**: Total and unique page visits
- **Visitors**: Unique visitor count
- **Top Pages**: Most visited pages
- **Referrers**: Where traffic is coming from
- **Devices**: Traffic breakdown by device type
- **Browsers**: Usage by browser type
- **Core Web Vitals**: Performance metrics (LCP, FID, CLS)

## Custom Events (Pro/Enterprise Plans)

For Pro or Enterprise plans, you can track custom events (e.g., task submissions, exam completions):

### Example: Track Task Submission

In your task submission template:

```html
<form method="POST" onsubmit="window.va('event', { name: 'Task Submitted', value: 'task-{{ task.id }}' })">
    {% csrf_token %}
    <!-- form fields -->
    <button type="submit">Submit Task</button>
</form>
```

### Example: Track Exam Completion

In your exam completion view:

```html
<script>
  window.va('event', { 
    name: 'Exam Completed', 
    value: 'exam-{{ exam.id }}'
  });
</script>
```

## Performance Impact

- **Script Size**: ~1.2 KB gzipped
- **Impact**: Minimal - loads asynchronously with `defer` attribute
- **Load Time**: Does not block page rendering or user interactions
- **CPU/Memory**: Negligible overhead

## Privacy & Data Compliance

Vercel Web Analytics is:
- **GDPR Compliant**: No PII (personally identifiable information) collected
- **Privacy-Focused**: IP addresses are anonymized
- **No Third-Party Cookies**: Does not use cookies for tracking
- **EU Data Residency**: Data can be stored in EU if needed

For more information, see the [Vercel Privacy Policy](https://vercel.com/legal/privacy-policy).

## Troubleshooting

### Analytics Not Showing

1. Verify deployment succeeded
2. Wait a few minutes - data takes time to appear
3. Check DevTools Network tab for `/_vercel/insights/view` requests
4. Ensure you're viewing the deployed version, not localhost

### Script Not Loading

1. Check that `/_vercel/insights/script.js` appears in Network tab
2. Verify the analytics script is in your page source
3. Check browser console for any error messages

### Check Current Status

View analytics status:
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project
3. Click the **Analytics** tab
4. Status and metrics will be displayed

## Disabling Analytics

To disable analytics:

1. Remove the script from `templates/base.html`
2. Go to Vercel Dashboard → Project → Analytics
3. Click **Disable**

## Next Steps

- Monitor analytics in the Vercel Dashboard
- Use insights to improve user experience
- Consider implementing custom events for better tracking
- Review [Vercel Analytics Documentation](https://vercel.com/docs/analytics) for advanced features

## References

- [Vercel Web Analytics Docs](https://vercel.com/docs/analytics)
- [Vercel Dashboard](https://vercel.com/dashboard)
- [Privacy Policy](https://vercel.com/docs/analytics/privacy-policy)
- [Custom Events](https://vercel.com/docs/analytics/custom-events)
