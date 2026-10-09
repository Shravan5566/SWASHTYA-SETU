"use client";

import { AuroraCreditCardBento } from "@/components/ui/aurora-credit-card-bento";

export default function AuroraCreditCardBentoDemo() {
    return (
        <div className="flex w-full justify-center bg-background p-6 sm:p-10">
            <div className="w-full max-w-[340px]">
                <AuroraCreditCardBento
                    title="Launch a card programme"
                    brand="mastercard"
                    color1="#ff7ac1"
                    color2="#a06bff"
                    color3="#4f46e5"
                    color4="#22d3ee"
                    color5="#4ade80"
                    color6="#ffb26b"
                    glow="#a06bff"
                />
            </div>
        </div>
    );
}
