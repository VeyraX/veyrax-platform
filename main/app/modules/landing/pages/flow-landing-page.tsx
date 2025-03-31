import { Hero } from "../components/flow/hero";
import UseCases from "../components/flow/usecases";
import HowTo from "../components/flow/how-to";
import { Footer } from "../components/footer";

export default function FlowLandingPage() {
  return (
    <>
      <Hero />
      <UseCases />
      <HowTo />
      <Footer />
    </>
  );
}