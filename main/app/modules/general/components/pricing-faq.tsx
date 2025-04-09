import { FaqSection } from "@/components/ui/faq";

const DEMO_FAQS = [
  {
    question: "How are messages counted?",
    answer: "Messages are all interactions with our AI in the chat, during flow creation, or when testing flows. Each question you ask and each response you receive counts as one message. But running scheduled flows doesn't count toward your message limit. Your plan determines how many messages you can use each month before needing to upgrade.",
  },
  {
    question: "What is the «Rent API keys» feature?",
    answer: "The Rent API keys feature allows you to use our API keys for third-party services without needing to register and create your own accounts. This saves you time and simplifies the integration process for services that support this feature. For more details, see our documentation at https://docs.veyrax.com/features/rentkey.",
  },
  {
    question: "What's included in the Teams plan?",
    answer: "The Teams plan is designed for businesses who want to offer our tools to their clients. While all our other plans (Free, Starter, Pro) are for individual customers who connect their own accounts, the Teams plan allows businesses to let their clients connect through them. We'll build custom tools so your clients can use our tools / agents / flows through your service. This plan includes custom API calls, flows, user authentication, integrations, and on-premise deployment options.",
  },
  {
    question: "What happens if I run out of API requests?",
    answer: "If you run out of API requests, you'll need to upgrade to a higher tier plan or wait until your next billing cycle when your allocation refreshes. Contact our support team if you need immediate assistance with your usage limits.",
  },
  {
    question: "Do you offer refunds?",
    answer: "Yes, we offer refunds under certain conditions. If you're not satisfied with our service or experience issues with API keys and feature usage, contact our support team to discuss refund options available to you.",
  },
  {
    question: "Can I switch between plans?",
    answer: "Yes, you can easily upgrade your plan anytime. When upgrading, changes will take effect immediately. When downgrading, changes will apply at the start of your next billing cycle.",
  },
  {
    question: "What are «Active Flows»?",
    answer: "Active Flows are workflows that are actively running on our platform. Flows can be in two states: draft or active. Draft flows don't run on any schedule and are just stored in your account. Active flows will run according to their scheduled triggers. You can create unlimited draft flows, but the number of flows you can set to 'active' is limited by your plan - from 3 in the Free plan up to 20 in the Pro plan, with custom options for Teams.",
  },
];

export function FaqSectionDemo() {
  return (
    <div className="w-full flex justify-center">
      <div className="container">
        <FaqSection
          title="Frequently Asked Questions"
          description="Everything you need to know about our pricing plans."
          items={DEMO_FAQS}
        />
      </div>
    </div>
  );
}