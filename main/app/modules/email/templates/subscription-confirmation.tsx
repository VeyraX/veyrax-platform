import * as React from 'react';
import {
  Body,
  Button,
  Container,
  Head,
  Heading,
  Hr,
  Html,
  Preview,
  Section,
  Text,
  Tailwind,
  Img,
} from '@react-email/components';

const SubscriptionConfirmationEmail = () => {
  const currentYear = new Date().getFullYear();

  return (
    <Html>
      <Tailwind>
        <Head>
          <title>Subscription Confirmation</title>
          <Preview>Thanks for subscribing to our newsletter!</Preview>
        </Head>
        <Body className="bg-gray-100 font-sans py-[40px]">
          <Container className="bg-white rounded-[8px] mx-auto p-[20px] max-w-[600px]">
            <Section>
              <Heading className="text-[24px] font-bold text-black my-[16px]">
                Subscription Confirmed!
              </Heading>
              <Text className="text-[16px] text-gray-800 mb-[24px]">
                Thank you for subscribing to our newsletter. We're excited to have you join our community!
              </Text>
              <Text className="text-[16px] text-gray-800 mb-[24px]">
                You'll now receive our latest updates, exclusive offers, and valuable content directly to your inbox.
              </Text>
              <Button
                className="bg-black text-white font-bold py-[12px] px-[24px] rounded-[4px] no-underline text-center block box-border"
                href="https://example.com/account"
              >
                Visit Your Account
              </Button>
              <Text className="text-[16px] text-gray-800 mt-[24px]">
                If you have any questions or need assistance, feel free to reply to this email.
              </Text>
              <Text className="text-[16px] text-gray-800 mb-[24px]">
                Best regards,<br />
                The Veyrax Team
              </Text>
            </Section>
            <Hr className="border-gray-300 my-[24px]" />
            <Section>
              <Img
                src="https://www.veyrax.com/logo.svg"
                alt="Veyrax Logo"
                width="60"
                height="auto"
                className="mb-[16px]"
              />
              <Text className="text-[14px] text-gray-600 m-0">
                123 Example Street, San Francisco, CA 94123
              </Text>
              <Text className="text-[14px] text-gray-600 m-0">
                © {currentYear} Veyrax. All rights reserved.
              </Text>
              <Text className="text-[14px] text-gray-600 mt-[8px]">
                <a href="https://example.com/unsubscribe" className="text-gray-800 underline">
                  Unsubscribe
                </a>{' '}
                •{' '}
                <a href="https://www.veyrax.com/terms" className="text-gray-800 underline">
                  Terms
                </a>{' '}
                •{' '}
                <a href="https://www.veyrax.com/privacy" className="text-gray-800 underline">
                  Privacy
                </a>
              </Text>
            </Section>
          </Container>
        </Body>
      </Tailwind>
    </Html>
  );
};

export default SubscriptionConfirmationEmail;