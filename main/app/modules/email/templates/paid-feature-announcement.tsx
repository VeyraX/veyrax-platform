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

const PaidSubscriptionAnnouncementEmail = () => {
  const currentYear = new Date().getFullYear();

  return (
    <Html>
      <Tailwind>
        <Head>
          <title>Paid Subscriptions Coming Soon</title>
          <Preview>We're launching premium subscriptions soon!</Preview>
        </Head>
        <Body className="bg-gray-100 font-sans py-[40px]">
          <Container className="bg-white rounded-[8px] mx-auto p-[20px] max-w-[600px]">
            <Section>
              <Heading className="text-[24px] font-bold text-black my-[16px]">
                Premium Subscriptions Coming Soon
              </Heading>
              <Text className="text-[16px] text-gray-800 mb-[16px]">
                We're excited to announce that premium subscription plans will be launching soon!
              </Text>
              <Text className="text-[16px] text-gray-800 mb-[16px]">
                <strong>Premium benefits include:</strong>
              </Text>
              <ul className="list-disc pl-[24px] mb-[16px]">
                <li className="text-[16px] text-gray-800">Advanced features</li>
                <li className="text-[16px] text-gray-800">Priority support</li>
                <li className="text-[16px] text-gray-800">Exclusive content</li>
              </ul>
              <Text className="text-[16px] text-gray-800 mb-[16px]">
                Early subscribers will receive a special discount. Stay tuned!
              </Text>
              <Button
                className="bg-black text-white font-bold py-[12px] px-[24px] rounded-[4px] no-underline text-center block box-border"
                href="https://example.com/subscription-waitlist"
              >
                Join the Waitlist
              </Button>
              <Text className="text-[16px] text-gray-800 mt-[24px]">
                If you have any questions, feel free to reply to this email.
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

export default PaidSubscriptionAnnouncementEmail;