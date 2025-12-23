# Getting Started with Vercel Web Analytics

This guide will help you get started with using Vercel Web Analytics on the TaskCert project. Vercel Web Analytics provides insights into your website's traffic, user behavior, and page performance metrics.

## Prerequisites

- A Vercel account. If you don't have one, you can [sign up for free](https://vercel.com/signup).
- A Vercel project. The TaskCert project is already configured for Vercel deployment.
- The Vercel CLI installed. If you don't have it, you can install it using:
  
```bash
npm i -g vercel
```

or using your preferred package manager:

```bash
pnpm i -g vercel
yarn global add vercel
bun add -g vercel
```

## Step 1: Enable Web Analytics in Vercel

1. Go to the [Vercel Dashboard](https://vercel.com/dashboard)
2. Select the **TaskCert** project
3. Click the **Analytics** tab in the top navigation
4. Click **Enable** to enable Web Analytics

> **💡 Note:** Enabling Web Analytics will add new routes (scoped at `/_vercel/insights/*`) after your next deployment. These routes are automatically handled by Vercel and require no additional configuration on your Django backend.

## Step 2: Add Vercel Analytics Script to Your Django Templates

For a Django project, you need to add the Vercel Analytics script to your base template. This is different from the framework-specific implementations shown in the official Vercel documentation.

### Option A: Using the HTML Script Tag (Recommended for Django)

Add the following code to your base template (`templates/base.html`), preferably in the `<head>` section or just before the closing `</body>` tag:

```html
<!-- Vercel Web Analytics -->
<script>
  window.va = window.va || function () { (window.vaq = window.vaq || []).push(arguments); };
</script>
<script defer src="/_vercel/insights/script.js"></script>
```

This is the simplest approach for Django and doesn't require any additional npm packages.

### Full Example for `templates/base.html`

```html
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Task Certification Platform{% endblock %}</title>

    <!-- Your existing meta tags, fonts, and stylesheets -->
    ...

    <!-- Vercel Web Analytics -->
    <script>
      window.va = window.va || function () { (window.vaq = window.vaq || []).push(arguments); };
    </script>
    <script defer src="/_vercel/insights/script.js"></script>
</head>

<body>
    <!-- Your page content -->
    ...

    <!-- Your existing scripts -->
    ...
</body>

</html>
```

## Step 3: Deploy Your App to Vercel

After enabling Web Analytics and adding the script to your templates, deploy your app:

```bash
vercel deploy
```

Or, if you've connected your Git repository to Vercel (recommended), simply push your changes:

```bash
git add .
git commit -m "Add Vercel Web Analytics integration"
git push origin main
```

Vercel will automatically deploy your latest changes. Once deployed, the analytics script will start collecting data.

> **💡 Note:** If everything is set up properly, you should be able to see a Fetch/XHR request in your browser's Network tab from `/_vercel/insights/view` when you visit any page on your deployed site.

## Step 4: View Your Data in the Dashboard

Once your app is deployed and users have visited your site:

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select the **TaskCert** project
3. Click the **Analytics** tab

After a few days of visitors, you'll be able to start exploring your data by viewing and filtering the analytics panels.

### Available Metrics

- **Page Views**: Track how many times pages are visited
- **Visitors**: Monitor unique visitor counts
- **Performance**: View Core Web Vitals and page load metrics
- **Top Pages**: See which pages get the most traffic
- **Referrers**: Understand where your traffic comes from
- **Devices**: Track traffic by device type (desktop, mobile, tablet)
- **Browsers**: Monitor which browsers your users are using

## Custom Events (Pro/Enterprise)

If you're on a Pro or Enterprise plan, you can add custom events to track user interactions such as button clicks, form submissions, or task completions.

### Adding Custom Events

To track custom events, use the Web Analytics API:

```html
<script>
  // Track a custom event
  window.va('event', { 
    name: 'Task Submitted',
    value: 'task-123'
  });
</script>
```

Or in your Django templates:

```html
<button onclick="window.va('event', { name: 'Button Clicked', value: 'submit-btn' })">
  Submit Task
</button>
```

## Verification

To verify that Web Analytics is working correctly:

1. Deploy your app with the analytics script
2. Open your deployed site in your browser
3. Open the browser's Developer Tools (F12 or Cmd+Option+I)
4. Go to the **Network** tab
5. Visit different pages on your site
6. Look for requests to `/_vercel/insights/view` and `/_vercel/insights/script.js`
7. These requests confirm that analytics are being tracked

## Next Steps

Now that you have Vercel Web Analytics set up, you can:

- [View detailed performance metrics](/docs/analytics/package)
- [Set up custom events](/docs/analytics/custom-events) (Pro/Enterprise plans)
- [Filter and analyze your data](/docs/analytics/filtering)
- [Review privacy and compliance information](/docs/analytics/privacy-policy)
- [Explore pricing and limits](/docs/analytics/limits-and-pricing)
- [Troubleshoot any issues](/docs/analytics/troubleshooting)

## Privacy & Compliance

Vercel Web Analytics is GDPR and privacy-compliant by default. No personally identifiable information (PII) is collected. For more information about privacy and data compliance, see [Privacy and Compliance Standards](/docs/analytics/privacy-policy).

## Troubleshooting

### Analytics Not Showing Data

1. **Verify deployment**: Ensure your latest changes are deployed to Vercel
2. **Check the script**: Open your page source and verify the analytics script is present
3. **Check network requests**: Open DevTools Network tab and confirm `/_vercel/insights/script.js` is loaded
4. **Wait for data**: It may take a few minutes for data to appear in the dashboard after the first visit
5. **Check filters**: Ensure you're not filtering out your own traffic

### Script Not Loading

1. **Verify Vercel routes**: Confirm that `/_vercel/insights/*` routes are not blocked by your application
2. **Check CORS**: Ensure no CORS issues are blocking the analytics requests
3. **Verify deployment**: Re-deploy your application to Vercel

### Performance Impact

The Vercel Web Analytics script is designed to have minimal performance impact:
- The script is only ~1.2kb gzipped
- It's loaded asynchronously with the `defer` attribute
- It doesn't block page rendering or interactions

## Additional Resources

- [Vercel Web Analytics Documentation](https://vercel.com/docs/analytics)
- [Vercel Dashboard](https://vercel.com/dashboard)
- [Vercel Help & Support](https://vercel.com/support)
