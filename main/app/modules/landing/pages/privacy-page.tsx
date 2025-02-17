export default function PrivacyPage() {
  return (
    <div className="px-8 py-6 w-full mb-10">
      <div className="mx-auto max-full p-4">
        <h1 className="text-4xl font-bold tracking-tight">Privacy Policy</h1>
        <p className="mt-4 text-sm text-muted-foreground">Last Updated: February 16, 2025</p>
        <p className="mt-4 text-lg text-muted-foreground">
          This Privacy Policy explains how we collect, use, and process information when you use our service. By using our service, you agree to the collection and use of information as described in this policy. If you have any questions, you can contact us at korzhov.work2019@gmail.com.
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
            <h2 className="text-2xl font-semibold">4. Data Storage and Security</h2>
            <p className="mt-2 text-muted-foreground">
              We do not store user authentication tokens or passwords. However, we securely store Refresh Tokens to ensure a seamless user experience by automatically renewing Access Tokens when they expire. This allows users to maintain uninterrupted access to their connected services without needing to reauthorize frequently.
            </p>
            <p className="mt-2 text-muted-foreground">
              We retain only the necessary extracted information to deliver the service, and you have full control over your data. If you choose to disconnect a service or delete your account, all associated data, including Refresh Tokens, are permanently deleted from our system.
            </p>
          </div>
          <div>
            <h2 className="text-2xl font-semibold">5. User Control and Data Deletion</h2>
            <p className="mt-2 text-muted-foreground">
              You have full control over your data, including the ability to delete it at any time. You can:
            </p>
            <ul className="mt-2 text-muted-foreground list-disc list-inside">
              <li>Manage and revoke access to third-party services through your account settings.</li>
              <li>Request data deletion by contacting us at korzhov.work2019@gmail.com.</li>
              <li>Completely remove all stored information associated with your account.</li>
            </ul>
          </div>
          <div>
            <h2 className="text-2xl font-semibold">6. Children’s Privacy</h2>
            <p className="mt-2 text-muted-foreground">
              Our service is not intended for children under the age of 13, and we do not knowingly collect personal data from individuals under this age. If we discover that a child under 13 has provided us with personal information, we will delete it immediately.
            </p>
          </div>
          <div>
            <h2 className="text-2xl font-semibold">7. Changes to This Privacy Policy</h2>
            <p className="mt-2 text-muted-foreground">
              We may update this Privacy Policy from time to time. Any changes will be posted on this page, and, if material changes occur, we will notify you via email or an in-app notification before they take effect.
            </p>
          </div>
          <div>
            <h2 className="text-2xl font-semibold">8. Contact Us</h2>
            <p className="mt-2 text-muted-foreground">
              If you have any questions about this Privacy Policy or your data, you can contact us at korzhov.work2019@gmail.com.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}