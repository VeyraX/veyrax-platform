import PricingOptions from "../components/pricing-options";
import PricingOptionsTable from "../components/pricing-options-table";
export default function PricingPage() {
    return (
        <div className="flex flex-col gap-8">
            <PricingOptions />
            <PricingOptionsTable />
        </div>
    );
}