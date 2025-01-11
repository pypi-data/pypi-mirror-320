import React from "react"
import ReactDOM from "react-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { getDefaultConfig, RainbowKitProvider } from "@rainbow-me/rainbowkit";
import { WagmiProvider } from "wagmi";
import { gnosis } from "wagmi/chains";
import PythonWeb3Wallet from "./PythonWeb3Wallet";

const queryClient = new QueryClient();

// for using with forked-Gnosis chain
// const gnosisFoundryLocalhost = {
//   id: 99,
//   name: 'Gnosis-Fork',
//   nativeCurrency: { name: 'Ether', symbol: 'xDAI', decimals: 18 },
//   rpcUrls: {
//     default: { http: ['http://127.0.0.1:8545'] },
//   },
// } as const satisfies Chain;

console.log('debug', process.env.REACT_APP_DEBUG_VARIABLE);

const config = getDefaultConfig({
  appName: 'app',
  projectId: process.env.REACT_APP_RAINBOW_PROJECT_ID!,
  chains: [
    gnosis,
    //gnosisFoundryLocalhost
  ],
});

ReactDOM.render(
  <WagmiProvider config={config}>
  <QueryClientProvider client={queryClient}>
    <RainbowKitProvider>
      <PythonWeb3Wallet />
    </RainbowKitProvider>
  </QueryClientProvider>
</WagmiProvider>,
  document.getElementById("root")
)