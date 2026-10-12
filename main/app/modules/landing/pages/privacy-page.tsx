export default function PrivacyPage() {
  return (
    <div className="px-8 py-6 w-full mb-10">
      <div className="mx-auto max-full p-4">
        <h1 className="text-4xl font-bold tracking-tight">Privacy Policy</h1>
        <p className="mt-4 text-sm text-muted-foreground">Last Updated: February 22, 2025</p>
        <p className="mt-4 text-lg text-muted-foreground">
          This Privacy Policy explains how we collect, use, and process information when you use our service. By using our service, you agree to the collection and use of information as described in this policy. If you have any questions, you can contact us at {process.env.NEXT_PUBLIC_SUPPORT_EMAIL || "support@veyrax.com"}.
        </p>
        <div className="mt-12 space-y-8">
          <div>
            <h2 className="text-2xl font-semibold">1. Information We Collect</h2>
            <p className="mt-2 text-muted-foreground">
              Our service allows users to connect third-party services such as Gmail, Google Drive, Google Calendar, Notion, and others. When you connect an external service, you explicitly grant us permission to access specific data scopes that you select.
            </p>
            <p className="mt-2 text-muted-foreground">
              We collect and process only the data within the scopes you authorize. The types of data we may process include:
            </p>
            <ul className="mt-2 text-muted-foreground list-disc list-inside">
              <li>Emails</li>
              <li>Files</li>
              <li>Calendar events</li>
              <li>Documents and notes</li>
            </ul>
          </div>
          <div>
            <h2 className="text-2xl font-semibold">2. How We Use Your Information</h2>
            <p className="mt-2 text-muted-foreground">
              The information collected is used exclusively to provide, maintain, and improve our service. Specifically, we use it to:
            </p>
            <ul className="mt-2 text-muted-foreground list-disc list-inside">
              <li>Process and analyze data within the selected scopes to deliver requested functionalities.</li>
              <li>Enhance user experience by integrating data from connected services.</li>
              <li>Provide insights and automated workflows based on authorized data.</li>
              <li>Communicate with you regarding your account and support inquiries.</li>
            </ul>
          </div>
          <div>
            <h2 className="text-2xl font-semibold">3. Actions We May Perform</h2>
            <p className="mt-2 text-muted-foreground">
              With your explicit consent, our service may perform actions on your behalf within authorized third-party services. These actions may include, but are not limited to:
            </p>
            <ul className="mt-2 text-muted-foreground list-disc list-inside">
              <li>Sending emails from your account (only with granted permissions).</li>
              <li>Creating and managing calendar events</li>
              <li>Generating and editing documents</li>
              <li>Interacting with other third-party services as specified by the user.</li>
            </ul>
            <p className="mt-2 text-muted-foreground">
              These actions will only be performed within the scope you explicitly authorize. We do not take any action without your consent.
            </p>
          </div>
          <div>
            <h2 className="text-2xl font-semibold">4. Data Sharing and Third-Party Services</h2>
            <p className="mt-2 text-muted-foreground">
              We share data only with specific third-party services that are essential for our application's functionality:
            </p>
            <ul className="mt-2 text-muted-foreground list-disc list-inside">
              <li>OpenAI - for processing and analyzing data within authorized scopes</li>
              <li>Qdrant - for storing and retrieving indexed data only if user has enabled it via settings</li>
            </ul>
            <p className="mt-2 text-muted-foreground">
              We only transmit data that falls within the specific scopes you have authorized. No data is shared with any other third parties. All Google Workspace API data is handled in strict compliance with <a href="https://developers.google.com/terms/api-services-user-data-policy" className="underline" target="_blank" rel="noopener noreferrer">Google API Services User Data Policy</a>, <a href="https://learn.microsoft.com/en-us/legal/microsoft-apis/terms-of-use" className="underline" target="_blank" rel="noopener noreferrer">Microsoft APIs Terms of Use</a>, and other third-party services with their respective User Data Policy.
            </p>
            <p className="mt-2 text-muted-foreground">
              We do not permanently store any of your data from connected services. The only exception is vector embeddings stored in Qdrant, which are only created and stored if you explicitly enable and authorize this feature in your settings.
            </p>
          </div>
          <div>
            <h2 className="text-2xl font-semibold">5. Data Protection and Security Measures</h2>
            <p className="mt-2 text-muted-foreground">
              We implement robust security measures to protect your sensitive data. Our data is stored in <a href="https://supabase.com/security" className="underline" target="_blank" rel="noopener noreferrer">Supabase</a>, which provides enterprise-grade security features:
            </p>
            <ul className="mt-2 text-muted-foreground list-disc list-inside">
              <li>All user data and refresh tokens are stored in Supabase's secure, encrypted database</li>
              <li>Supabase implements Row Level Security (RLS) policies to ensure data isolation</li>
              <li>Data is encrypted at rest using AES-256 encryption and in transit via TLS</li>
              <li>Sensitive information like refresh tokens and keys are encrypted at the application level</li>
              <li>Multi-factor authentication (MFA) is available for additional security</li>
              <li>SOC2 Type 2 certified and HIPAA compliant infrastructure</li>
              <li>Regular security audits, vulnerability scanning, and penetration testing</li>
              <li>DDoS protection through Cloudflare and built-in rate limiting</li>
              <li>Automated daily backups and disaster recovery capabilities</li>
            </ul>
          </div>
          <div>
            <h2 className="text-2xl font-semibold">6. AI and Machine Learning Policy</h2>
            <p className="mt-2 text-muted-foreground">
              We want to be absolutely clear about how we handle your data in relation to AI and machine learning:
            </p>
            <ul className="mt-2 text-muted-foreground list-disc list-inside">
              <li>We do NOT use your data to train, develop, or improve any AI or machine learning models</li>
              <li>We do NOT retain user data obtained through Google Workspace APIs / Microsoft Graph API or other third-party services for AI/ML purposes</li>
              <li>The AI services we use (OpenAI, Qdrant) are compliant with data protection requirements and do not train on your data</li>
              <li>All AI processing is performed on-demand and solely within the scope of providing our service functionality</li>
            </ul>
          </div>
          <div>
            <h2 className="text-2xl font-semibold">7. User Control and Data Deletion</h2>
            <p className="mt-2 text-muted-foreground">
              You have full control over your data, including the ability to delete it at any time. You can:
            </p>
            <ul className="mt-2 text-muted-foreground list-disc list-inside">
              <li>Manage and revoke access to third-party services through your account settings.</li>
              <li>Request data deletion by contacting us at {process.env.NEXT_PUBLIC_SUPPORT_EMAIL || "support@veyrax.com"}.</li>
              <li>Completely remove all stored information associated with your account.</li>
            </ul>
          </div>
          <div>
            <h2 className="text-2xl font-semibold">8. Children's Privacy</h2>
            <p className="mt-2 text-muted-foreground">
              Our service is not intended for children under the age of 13, and we do not knowingly collect personal data from individuals under this age. If we discover that a child under 13 has provided us with personal information, we will delete it immediately.
            </p>
          </div>
          <div>
            <h2 className="text-2xl font-semibold">9. Changes to This Privacy Policy</h2>
            <p className="mt-2 text-muted-foreground">
              We may update this Privacy Policy from time to time. Any changes will be posted on this page, and, if material changes occur, we will notify you via email or an in-app notification before they take effect.
            </p>
          </div>
          <div>
            <h2 className="text-2xl font-semibold">10. Contact Us</h2>
            <p className="mt-2 text-muted-foreground">
              If you have any questions about this Privacy Policy or your data, you can contact us at {process.env.NEXT_PUBLIC_SUPPORT_EMAIL || "support@veyrax.com"}.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}